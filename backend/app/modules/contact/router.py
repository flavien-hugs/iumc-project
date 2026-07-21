from fastapi import APIRouter, Request, status
from pydantic import BaseModel, EmailStr, Field

from app.core.db import DbSession
from app.core.rate_limit import limit_submissions
from app.models import ContactMessage

router = APIRouter(tags=["contact"])


class ContactMessageCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    phone: str = Field(min_length=8, max_length=30)
    email: EmailStr | None = None
    subject: str = Field(min_length=2, max_length=255)
    message: str = Field(min_length=10)


@router.post("/contact", status_code=status.HTTP_201_CREATED)
async def create_contact_message(
    payload: ContactMessageCreate, request: Request, db: DbSession
) -> dict[str, str]:
    await limit_submissions(request, "contact")
    db.add(
        ContactMessage(
            name=payload.name,
            phone=payload.phone,
            email=str(payload.email) if payload.email else None,
            subject=payload.subject,
            message=payload.message,
        )
    )
    await db.commit()
    return {"status": "received"}
