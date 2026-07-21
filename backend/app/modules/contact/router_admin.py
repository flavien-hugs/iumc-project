from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.core.db import DbSession
from app.core.pagination import Page, PageParams, paginate
from app.models import ContactMessage
from app.modules.auth.deps import CurrentUser

router = APIRouter(prefix="/admin/contact-messages", tags=["admin"])


class ContactMessageRow(BaseModel):
    id: int
    name: str
    phone: str
    email: str | None
    subject: str
    message: str
    is_processed: bool
    created_at: datetime


class ContactMessageUpdate(BaseModel):
    is_processed: bool


@router.get("", response_model=Page[ContactMessageRow])
async def list_contact_messages(
    db: DbSession, _: CurrentUser, params: PageParams = Depends()
) -> Page[ContactMessageRow]:
    query = select(ContactMessage).order_by(ContactMessage.created_at.desc())
    rows, total = await paginate(db, query, params)
    return Page(
        items=[
            ContactMessageRow(
                id=item.id,
                name=item.name,
                phone=item.phone,
                email=item.email,
                subject=item.subject,
                message=item.message,
                is_processed=item.is_processed,
                created_at=item.created_at,
            )
            for row in rows
            for item in [row[0]]
        ],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


@router.patch("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_contact_message(
    message_id: int, payload: ContactMessageUpdate, db: DbSession, _: CurrentUser
) -> None:
    item = await db.get(ContactMessage, message_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Message introuvable")
    item.is_processed = payload.is_processed
    await db.commit()
