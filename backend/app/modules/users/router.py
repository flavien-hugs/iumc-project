from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select

from app.core.db import DbSession
from app.core.pagination import Page, PageParams, paginate
from app.core.security import hash_password
from app.models import User, UserRole
from app.modules.audit.service import log_action
from app.modules.auth.deps import CurrentUser, get_user_by_email, require_roles

router = APIRouter(
    prefix="/admin/users",
    tags=["admin"],
    # Gestion des comptes réservée au super administrateur (PRD section 11.6).
    dependencies=[Depends(require_roles(UserRole.super_admin))],
)


class UserRow(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    role: str
    location_id: int | None
    is_active: bool
    deleted_at: datetime | None
    last_login_at: datetime | None


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=10)
    role: UserRole
    phone: str | None = None
    location_id: int | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    role: UserRole | None = None
    phone: str | None = None
    location_id: int | None = None
    is_active: bool | None = None


def _to_row(user: User) -> UserRow:
    return UserRow(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=user.role.value,
        location_id=user.location_id,
        is_active=user.is_active,
        deleted_at=user.deleted_at,
        last_login_at=user.last_login_at,
    )


@router.get("", response_model=Page[UserRow])
async def list_users(
    db: DbSession, params: PageParams = Depends(), include_deleted: bool = False
) -> Page[UserRow]:
    query = select(User).order_by(User.name)
    if not include_deleted:
        query = query.where(User.deleted_at.is_(None))
    rows, total = await paginate(db, query, params)
    return Page(
        items=[_to_row(row[0]) for row in rows],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


@router.post("", response_model=UserRow, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: DbSession, current: CurrentUser) -> UserRow:
    if await get_user_by_email(db, payload.email) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Un compte existe déjà avec cet e-mail")
    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        phone=payload.phone,
        location_id=payload.location_id,
    )
    db.add(user)
    await db.flush()
    log_action(db, current.id, "create", resource="user", resource_id=user.id)
    await db.commit()
    return _to_row(user)


@router.patch("/{user_id}", response_model=UserRow)
async def update_user(
    user_id: int, payload: UserUpdate, db: DbSession, current: CurrentUser
) -> UserRow:
    user = await db.get(User, user_id)
    if user is None or user.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utilisateur introuvable")
    if user.id == current.id and payload.is_active is False:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Impossible de désactiver son propre compte"
        )
    if payload.name is not None:
        user.name = payload.name
    if payload.role is not None:
        user.role = payload.role
    if payload.phone is not None:
        user.phone = payload.phone
    if payload.location_id is not None:
        user.location_id = payload.location_id
    if payload.is_active is not None:
        user.is_active = payload.is_active
    log_action(db, current.id, "update", resource="user", resource_id=user.id)
    await db.commit()
    return _to_row(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: DbSession, current: CurrentUser) -> None:
    """Suppression logique (PRD section 11.6) : les données restent en base
    (historique, logs) mais le compte devient invisible et immuable par
    défaut, jusqu'à restauration explicite via `/restore`."""
    if user_id == current.id:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Impossible de supprimer son propre compte"
        )
    user = await db.get(User, user_id)
    if user is None or user.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utilisateur introuvable")
    user.deleted_at = datetime.now(UTC)
    user.is_active = False
    log_action(db, current.id, "delete", resource="user", resource_id=user.id)
    await db.commit()


@router.post("/{user_id}/restore", response_model=UserRow)
async def restore_user(user_id: int, db: DbSession, current: CurrentUser) -> UserRow:
    user = await db.get(User, user_id)
    if user is None or user.deleted_at is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utilisateur supprimé introuvable")
    user.deleted_at = None
    log_action(db, current.id, "restore", resource="user", resource_id=user.id)
    await db.commit()
    return _to_row(user)
