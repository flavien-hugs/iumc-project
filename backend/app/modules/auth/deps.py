from typing import Annotated, TypeAlias

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import DbSession
from app.core.security import decode_token
from app.models import User, UserRole


async def get_current_user(request: Request, db: DbSession) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentification requise")
    user_id = decode_token(token, "access")
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Jeton invalide ou expiré")
    user = await db.get(User, user_id)
    if user is None or not user.is_usable:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Compte introuvable ou désactivé")
    return user


CurrentUser: TypeAlias = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole):
    async def dependency(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Accès refusé pour ce rôle")
        return user

    return dependency


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
