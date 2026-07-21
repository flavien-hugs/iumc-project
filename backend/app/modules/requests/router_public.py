import datetime as dt
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, UploadFile, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select

from app.core.config import get_settings
from app.core.db import DbSession
from app.core.rate_limit import limit_submissions
from app.core.storage import full_path, save_bytes
from app.modules.notifications.service import publish_notification
from app.modules.requests.tasks import send_acknowledgment

settings = get_settings()

# Formats de pièces jointes autorisés (PRD section 10.8).
ALLOWED_ATTACHMENT_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
from app.models import (
    ClientType,
    ContactPreference,
    Division,
    DivisionStatus,
    Notification,
    Service,
    ServiceRequest,
    ServiceStatus,
    User,
    UserRole,
)

router = APIRouter(tags=["service-requests"])


class ServiceRequestCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    company: str | None = Field(default=None, max_length=150)
    phone: str = Field(min_length=8, max_length=30)
    email: EmailStr | None = None
    city: str | None = Field(default=None, max_length=100)
    client_type: ClientType | None = None
    division: str = Field(min_length=1, max_length=150)
    service: str = Field(min_length=1, max_length=255)
    subject: str | None = Field(default=None, max_length=255)
    description: str = Field(min_length=10)
    contact_preference: ContactPreference = ContactPreference.phone
    preferred_appointment_date: dt.date | None = None
    # Chemin opaque retourné par POST /service-requests/attachments.
    attachment: str | None = None


class ServiceRequestCreated(BaseModel):
    reference: str


class AttachmentUploaded(BaseModel):
    attachment: str


@router.post(
    "/service-requests/attachments",
    response_model=AttachmentUploaded,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(file: UploadFile, request: Request) -> AttachmentUploaded:
    await limit_submissions(request, "attachment")
    extension = Path(file.filename or "").suffix.lstrip(".").lower()
    if extension not in ALLOWED_ATTACHMENT_EXTENSIONS:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Format non autorisé (PDF, JPG ou PNG uniquement)",
        )
    data = await file.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Fichier trop volumineux (maximum {settings.max_upload_mb} Mo)",
        )
    # Stockage privé : jamais servi statiquement, uniquement via l'endpoint
    # admin authentifié (exigence de confidentialité, PRD section 14).
    relative_path = save_bytes(data, "attachments", extension)
    return AttachmentUploaded(attachment=relative_path)


@router.post(
    "/service-requests", response_model=ServiceRequestCreated, status_code=status.HTTP_201_CREATED
)
async def create_service_request(
    payload: ServiceRequestCreate, request: Request, db: DbSession
) -> ServiceRequestCreated:
    await limit_submissions(request, "service_request")

    division = (
        await db.execute(select(Division).where(Division.slug == payload.division))
    ).scalar_one_or_none()
    if division is None or division.status != DivisionStatus.active:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Pôle inconnu ou indisponible")

    service = (
        await db.execute(
            select(Service).where(
                Service.slug == payload.service, Service.division_id == division.id
            )
        )
    ).scalar_one_or_none()
    if service is None or service.status != ServiceStatus.active:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Service inconnu ou indisponible"
        )

    attachment = None
    if payload.attachment:
        if payload.attachment.startswith("attachments/") and full_path(payload.attachment):
            attachment = payload.attachment
        else:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Pièce jointe invalide")

    service_request = ServiceRequest(
        full_name=payload.full_name,
        company=payload.company,
        phone=payload.phone,
        email=str(payload.email) if payload.email else None,
        city=payload.city,
        client_type=payload.client_type,
        division_id=division.id,
        service_id=service.id,
        subject=payload.subject,
        description=payload.description,
        contact_preference=payload.contact_preference,
        preferred_appointment_date=payload.preferred_appointment_date,
        attachment=attachment,
    )
    db.add(service_request)
    await db.flush()
    # Référence métier au format imposé par le PRD section 10.8.
    service_request.reference = f"IUMC-DEM-{dt.datetime.now().year}-{service_request.id:05d}"

    # Notification in-app des super administrateurs (ADR-0010, livrée en
    # direct par SSE depuis l'ADR-0016).
    admin_ids = (
        await db.execute(
            select(User.id).where(
                User.role == UserRole.super_admin,
                User.is_active.is_(True),
                User.deleted_at.is_(None),
            )
        )
    ).scalars()
    new_notifications = [
        Notification(
            user_id=admin_id,
            type="new_service_request",
            title=f"Nouvelle demande {service_request.reference} : {service.title}",
            resource="service_request",
            resource_id=service_request.id,
        )
        for admin_id in admin_ids
    ]
    db.add_all(new_notifications)

    await db.commit()

    for notification in new_notifications:
        await publish_notification(notification)

    # Accusé de réception au demandeur via Celery (PRD section 19.2).
    if service_request.email:
        send_acknowledgment.delay(
            service_request.email,
            service_request.full_name,
            service_request.reference,
            service.title,
        )

    return ServiceRequestCreated(reference=service_request.reference)
