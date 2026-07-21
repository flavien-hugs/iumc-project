import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.orm import aliased

from app.core.db import DbSession
from app.core.pagination import Page, PageParams, paginate
from app.core.storage import full_path
from app.models import (
    Appointment,
    AppointmentStatus,
    Division,
    Notification,
    RequestStatus,
    Service,
    ServiceRequest,
    ServiceRequestHistory,
    User,
)
from app.modules.audit.service import log_action
from app.modules.auth.deps import CurrentUser
from app.modules.notifications.service import publish_notification
from app.modules.requests.service import ensure_can_modify, ensure_can_read, scope_requests

router = APIRouter(prefix="/admin", tags=["admin"])


class ServiceRequestSummary(BaseModel):
    id: int
    reference: str | None
    full_name: str
    phone: str
    city: str | None
    client_type: str | None
    division: str
    service: str
    status: str
    created_at: dt.datetime


class HistoryEntry(BaseModel):
    id: int
    previous_status: str | None
    new_status: str
    user_name: str | None
    note: str | None
    created_at: dt.datetime


class AppointmentSummary(BaseModel):
    id: int
    date: dt.date
    time: dt.time | None
    status: str
    assignee_name: str | None
    note: str | None


class ServiceRequestDetail(ServiceRequestSummary):
    company: str | None
    email: str | None
    subject: str | None
    description: str
    contact_preference: str
    preferred_appointment_date: dt.date | None
    agent_id: int | None
    agent_name: str | None
    location_id: int | None
    attachment: str | None
    history: list[HistoryEntry]
    appointments: list[AppointmentSummary]


class ServiceRequestUpdate(BaseModel):
    status: RequestStatus | None = None
    agent_id: int | None = None
    location_id: int | None = None
    note: str | None = None


class AppointmentCreate(BaseModel):
    date: dt.date
    time: dt.time | None = None
    assignee_id: int | None = None
    note: str | None = None


class AppointmentUpdate(BaseModel):
    status: AppointmentStatus | None = None
    date: dt.date | None = None
    time: dt.time | None = None
    assignee_id: int | None = None
    note: str | None = None


class AppointmentRow(BaseModel):
    id: int
    date: dt.date
    time: dt.time | None
    status: str
    note: str | None
    assignee_name: str | None
    request_id: int
    request_reference: str | None
    request_full_name: str


@router.get("/service-requests", response_model=Page[ServiceRequestSummary])
async def list_service_requests(
    db: DbSession,
    user: CurrentUser,
    q: str | None = None,
    status_filter: RequestStatus | None = None,
    date_from: dt.date | None = None,
    date_to: dt.date | None = None,
    sort: str = "desc",
    params: PageParams = Depends(),
) -> Page[ServiceRequestSummary]:
    query = (
        select(ServiceRequest, Division.name, Service.title)
        .join(Division, ServiceRequest.division_id == Division.id)
        .join(Service, ServiceRequest.service_id == Service.id)
    )
    query = scope_requests(query, user)
    if status_filter is not None:
        query = query.where(ServiceRequest.status == status_filter)
    if date_from is not None:
        query = query.where(ServiceRequest.created_at >= date_from)
    if date_to is not None:
        query = query.where(ServiceRequest.created_at < date_to + dt.timedelta(days=1))
    if q:
        pattern = f"%{q.strip()}%"
        query = query.where(
            or_(
                ServiceRequest.reference.ilike(pattern),
                ServiceRequest.full_name.ilike(pattern),
                ServiceRequest.phone.ilike(pattern),
                ServiceRequest.city.ilike(pattern),
            )
        )
    query = query.order_by(
        ServiceRequest.created_at.asc() if sort == "asc" else ServiceRequest.created_at.desc()
    )
    rows, total = await paginate(db, query, params)
    return Page(
        items=[
            ServiceRequestSummary(
                id=item.id,
                reference=item.reference,
                full_name=item.full_name,
                phone=item.phone,
                city=item.city,
                client_type=item.client_type.value if item.client_type else None,
                division=division_name,
                service=service_title,
                status=item.status.value,
                created_at=item.created_at,
            )
            for item, division_name, service_title in rows
        ],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


async def _get_request_or_404(db, request_id: int) -> ServiceRequest:
    item = await db.get(ServiceRequest, request_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Demande introuvable")
    return item


@router.get("/service-requests/{request_id}", response_model=ServiceRequestDetail)
async def get_service_request(
    request_id: int, db: DbSession, user: CurrentUser
) -> ServiceRequestDetail:
    item = await _get_request_or_404(db, request_id)
    ensure_can_read(item, user)

    division = await db.get(Division, item.division_id)
    service = await db.get(Service, item.service_id)
    agent = await db.get(User, item.agent_id) if item.agent_id else None

    history_rows = (
        await db.execute(
            select(ServiceRequestHistory, User.name)
            .outerjoin(User, ServiceRequestHistory.user_id == User.id)
            .where(ServiceRequestHistory.request_id == item.id)
            .order_by(ServiceRequestHistory.created_at.desc())
        )
    ).all()

    assignee = aliased(User)
    appointment_rows = (
        await db.execute(
            select(Appointment, assignee.name)
            .outerjoin(assignee, Appointment.assignee_id == assignee.id)
            .where(Appointment.request_id == item.id)
            .order_by(Appointment.date.desc())
        )
    ).all()

    return ServiceRequestDetail(
        id=item.id,
        reference=item.reference,
        full_name=item.full_name,
        phone=item.phone,
        city=item.city,
        client_type=item.client_type.value if item.client_type else None,
        division=division.name if division else "",
        service=service.title if service else "",
        status=item.status.value,
        created_at=item.created_at,
        company=item.company,
        email=item.email,
        subject=item.subject,
        description=item.description,
        contact_preference=item.contact_preference.value,
        preferred_appointment_date=item.preferred_appointment_date,
        agent_id=item.agent_id,
        agent_name=agent.name if agent else None,
        location_id=item.location_id,
        attachment=item.attachment,
        history=[
            HistoryEntry(
                id=entry.id,
                previous_status=entry.previous_status.value if entry.previous_status else None,
                new_status=entry.new_status.value,
                user_name=user_name,
                note=entry.note,
                created_at=entry.created_at,
            )
            for entry, user_name in history_rows
        ],
        appointments=[
            AppointmentSummary(
                id=appointment.id,
                date=appointment.date,
                time=appointment.time,
                status=appointment.status.value,
                assignee_name=assignee_name,
                note=appointment.note,
            )
            for appointment, assignee_name in appointment_rows
        ],
    )


@router.patch("/service-requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_service_request(
    request_id: int, payload: ServiceRequestUpdate, db: DbSession, user: CurrentUser
) -> None:
    item = await _get_request_or_404(db, request_id)
    ensure_can_modify(item, user)

    status_changed = payload.status is not None and payload.status != item.status
    if status_changed or payload.note:
        db.add(
            ServiceRequestHistory(
                request_id=item.id,
                previous_status=item.status,
                new_status=payload.status if status_changed else item.status,
                user_id=user.id,
                note=payload.note,
            )
        )
    if status_changed:
        item.status = payload.status
        log_action(
            db, user.id, "status_change", resource="service_request", resource_id=item.id,
            details={"status": payload.status.value},
        )

    assignment_notification: Notification | None = None
    if payload.agent_id is not None and payload.agent_id != item.agent_id:
        agent = await db.get(User, payload.agent_id)
        if agent is None or not agent.is_usable:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Agent introuvable")
        item.agent_id = agent.id
        # Notification d'affectation à l'agent concerné (PRD section 19.3),
        # livrée en direct par SSE (ADR-0016).
        assignment_notification = Notification(
            user_id=agent.id,
            type="request_assigned",
            title=f"Demande {item.reference} affectée à vous",
            resource="service_request",
            resource_id=item.id,
        )
        db.add(assignment_notification)
        log_action(
            db, user.id, "assignment", resource="service_request", resource_id=item.id,
            details={"agent_id": agent.id},
        )

    if payload.location_id is not None:
        item.location_id = payload.location_id

    await db.commit()

    if assignment_notification is not None:
        await publish_notification(assignment_notification)


@router.get("/appointments", response_model=Page[AppointmentRow])
async def list_appointments(
    db: DbSession, user: CurrentUser, params: PageParams = Depends()
) -> Page[AppointmentRow]:
    assignee = aliased(User)
    query = (
        select(Appointment, assignee.name, ServiceRequest)
        .join(ServiceRequest, Appointment.request_id == ServiceRequest.id)
        .outerjoin(assignee, Appointment.assignee_id == assignee.id)
    )
    query = scope_requests(query, user)
    query = query.order_by(Appointment.date.desc())
    rows, total = await paginate(db, query, params)
    return Page(
        items=[
            AppointmentRow(
                id=appointment.id,
                date=appointment.date,
                time=appointment.time,
                status=appointment.status.value,
                note=appointment.note,
                assignee_name=assignee_name,
                request_id=request.id,
                request_reference=request.reference,
                request_full_name=request.full_name,
            )
            for appointment, assignee_name, request in rows
        ],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


@router.post(
    "/service-requests/{request_id}/appointments", status_code=status.HTTP_201_CREATED
)
async def create_appointment(
    request_id: int, payload: AppointmentCreate, db: DbSession, user: CurrentUser
) -> dict[str, int]:
    item = await _get_request_or_404(db, request_id)
    ensure_can_modify(item, user)
    appointment = Appointment(
        request_id=item.id,
        date=payload.date,
        time=payload.time,
        assignee_id=payload.assignee_id,
        note=payload.note,
    )
    db.add(appointment)
    if item.status in (RequestStatus.new, RequestStatus.to_contact):
        db.add(
            ServiceRequestHistory(
                request_id=item.id,
                previous_status=item.status,
                new_status=RequestStatus.appointment_scheduled,
                user_id=user.id,
                note="Rendez-vous planifié",
            )
        )
        item.status = RequestStatus.appointment_scheduled
    await db.flush()
    log_action(
        db, user.id, "create", resource="appointment", resource_id=appointment.id,
        details={"request_id": item.id},
    )
    await db.commit()
    return {"id": appointment.id}


@router.patch("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_appointment(
    appointment_id: int, payload: AppointmentUpdate, db: DbSession, user: CurrentUser
) -> None:
    appointment = await db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rendez-vous introuvable")
    parent_request = await _get_request_or_404(db, appointment.request_id)
    ensure_can_modify(parent_request, user)

    date_or_time_changed = (
        payload.date is not None and payload.date != appointment.date
    ) or (payload.time is not None and payload.time != appointment.time)

    if payload.date is not None:
        appointment.date = payload.date
    if payload.time is not None:
        appointment.time = payload.time
    if payload.assignee_id is not None:
        appointment.assignee_id = payload.assignee_id
    if payload.note is not None:
        appointment.note = payload.note
    if payload.status is not None:
        appointment.status = payload.status
    elif date_or_time_changed:
        # Date/heure déplacées sans statut explicite fourni : le statut doit
        # refléter le report plutôt que de rester sur une valeur (ex.
        # "confirmed") devenue incohérente avec la nouvelle date.
        appointment.status = AppointmentStatus.rescheduled

    log_action(
        db, user.id, "update", resource="appointment", resource_id=appointment.id,
        details={
            "status": appointment.status.value,
            "date": appointment.date.isoformat(),
        },
    )
    await db.commit()


@router.get("/service-requests/{request_id}/attachment")
async def download_attachment(
    request_id: int, db: DbSession, user: CurrentUser
) -> FileResponse:
    item = await _get_request_or_404(db, request_id)
    ensure_can_read(item, user)
    if not item.attachment:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Aucune pièce jointe")
    path = full_path(item.attachment)
    if path is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fichier introuvable")
    return FileResponse(path, filename=f"{item.reference}-piece-jointe{path.suffix}")
