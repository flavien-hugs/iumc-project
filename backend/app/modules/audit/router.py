import datetime as dt
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select

from app.core.db import DbSession
from app.core.pagination import Page, PageParams, paginate
from app.models import AuditLog, User, UserRole
from app.modules.auth.deps import require_roles

router = APIRouter(
    prefix="/admin/audit-logs",
    tags=["admin"],
    dependencies=[Depends(require_roles(UserRole.super_admin))],
)


class AuditLogRow(BaseModel):
    id: int
    user_name: str | None
    action: str
    resource: str | None
    resource_id: int | None
    ip_address: str | None
    details: dict[str, Any] | None
    created_at: dt.datetime


@router.get("", response_model=Page[AuditLogRow])
async def list_audit_logs(
    db: DbSession,
    date_from: dt.date | None = None,
    date_to: dt.date | None = None,
    params: PageParams = Depends(),
) -> Page[AuditLogRow]:
    query = select(AuditLog, User.name).outerjoin(User, AuditLog.user_id == User.id)
    if date_from is not None:
        query = query.where(AuditLog.created_at >= date_from)
    if date_to is not None:
        query = query.where(AuditLog.created_at < date_to + dt.timedelta(days=1))
    query = query.order_by(AuditLog.created_at.desc())
    rows, total = await paginate(db, query, params)
    return Page(
        items=[
            AuditLogRow(
                id=entry.id,
                user_name=user_name,
                action=entry.action,
                resource=entry.resource,
                resource_id=entry.resource_id,
                ip_address=entry.ip_address,
                details=entry.details,
                created_at=entry.created_at,
            )
            for entry, user_name in rows
        ],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )
