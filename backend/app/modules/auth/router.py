import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select

from app.core.config import settings
from app.core.db import DbSession
from app.core.rate_limit import client_ip, limit_submissions
from app.core.redis import get_redis
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.models import PasswordResetToken, User
from app.modules.audit.service import log_action
from app.modules.auth.deps import CurrentUser, get_user_by_email
from app.modules.users.tasks import send_password_reset


router = APIRouter(prefix="/auth", tags=["auth"])

MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_WINDOW_SECONDS = 15 * 60


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str


def _set_auth_cookies(response: Response, user_id: int) -> None:
    secure = settings.environment != "development"
    response.set_cookie(
        "access_token",
        create_token(user_id, "access"),
        httponly=True,
        secure=secure,
        samesite="strict",
        max_age=settings.jwt_access_token_expires_minutes * 60,
        path="/",
    )
    response.set_cookie(
        "refresh_token",
        create_token(user_id, "refresh"),
        httponly=True,
        secure=secure,
        samesite="strict",
        max_age=settings.jwt_refresh_token_expires_days * 24 * 3600,
        path=f"{settings.api_prefix}/auth",
    )


@router.post("/login", response_model=UserResponse)
async def login(
    payload: LoginRequest, request: Request, response: Response, db: DbSession
) -> User:
    redis = get_redis()
    ip = client_ip(request)
    attempts_key = f"login_attempts:{payload.email.lower()}:{ip}"

    attempts = await redis.get(attempts_key)
    if attempts is not None and int(attempts) >= MAX_LOGIN_ATTEMPTS:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Trop de tentatives. Réessayez dans quelques minutes.",
        )

    user = await get_user_by_email(db, payload.email)
    if user is None or not user.is_usable or not verify_password(payload.password, user.password_hash):
        count = await redis.incr(attempts_key)
        if count == 1:
            await redis.expire(attempts_key, LOGIN_ATTEMPT_WINDOW_SECONDS)
        log_action(
            db,
            user.id if user else None,
            "login_failed",
            resource="user",
            resource_id=user.id if user else None,
            ip_address=ip,
        )
        await db.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiants invalides")

    await redis.delete(attempts_key)
    user.last_login_at = datetime.now(UTC)
    log_action(db, user.id, "login", resource="user", resource_id=user.id, ip_address=ip)
    await db.commit()

    _set_auth_cookies(response, user.id)
    return user


@router.post("/refresh", status_code=status.HTTP_204_NO_CONTENT)
async def refresh(request: Request, response: Response, db: DbSession) -> None:
    token = request.cookies.get("refresh_token")
    user_id = decode_token(token, "refresh") if token else None
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expirée")
    user = await db.get(User, user_id)
    if user is None or not user.is_usable:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Compte introuvable ou désactivé")
    _set_auth_cookies(response, user.id)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path=f"{settings.api_prefix}/auth")


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser) -> User:
    return user


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=32, max_length=128)
    new_password: str = Field(min_length=10)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=10)


def _hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(
    payload: ForgotPasswordRequest, request: Request, db: DbSession
) -> None:
    """Toujours 204, que le compte existe ou non (pas d'énumération d'e-mails)."""
    await limit_submissions(request, "forgot_password")
    user = await get_user_by_email(db, payload.email)
    if user is not None and user.is_usable:
        token = secrets.token_hex(32)
        db.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=_hash_reset_token(token),
                expires_at=datetime.now(UTC) + timedelta(hours=1),
            )
        )
        log_action(
            db, user.id, "password_reset_requested", resource="user", resource_id=user.id,
            ip_address=client_ip(request),
        )
        await db.commit()
        reset_link = f"{settings.admin_base_url}/admin/reset-password?token={token}"
        send_password_reset.delay(user.email, reset_link)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    payload: ResetPasswordRequest, request: Request, db: DbSession
) -> None:
    reset_token = (
        await db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == _hash_reset_token(payload.token),
                PasswordResetToken.is_used.is_(False),
                PasswordResetToken.expires_at > datetime.now(UTC),
            )
        )
    ).scalar_one_or_none()
    if reset_token is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Lien invalide ou expiré")
    user = await db.get(User, reset_token.user_id)
    if user is None or not user.is_usable:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Compte introuvable")
    user.password_hash = hash_password(payload.new_password)
    reset_token.is_used = True
    log_action(
        db, user.id, "password_reset", resource="user", resource_id=user.id,
        ip_address=client_ip(request),
    )
    await db.commit()


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    payload: ChangePasswordRequest, request: Request, db: DbSession, user: CurrentUser
) -> None:
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Mot de passe actuel invalide")
    user.password_hash = hash_password(payload.new_password)
    log_action(
        db, user.id, "password_change", resource="user", resource_id=user.id,
        ip_address=client_ip(request),
    )
    await db.commit()
