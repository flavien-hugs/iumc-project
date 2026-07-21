import datetime as dt

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import func, select

from app.core.db import DbSession
from app.models import (
    Appointment,
    AppointmentStatus,
    Article,
    ArticleStatus,
    Location,
    RequestStatus,
    Service,
    ServiceRequest,
    ServiceStatus,
)
from app.models import UserRole
from app.modules.auth.deps import CurrentUser
from app.modules.requests.service import scope_requests

router = APIRouter(prefix="/admin", tags=["admin"])

IN_PROGRESS_STATUSES = [
    RequestStatus.to_contact,
    RequestStatus.appointment_scheduled,
    RequestStatus.in_progress,
    RequestStatus.awaiting_client,
]
CLOSED_STATUSES = [RequestStatus.processed, RequestStatus.closed]


class DashboardResponse(BaseModel):
    total_requests: int
    new_requests: int
    in_progress_requests: int
    closed_requests: int
    upcoming_appointments: int
    active_services: int
    locations: int
    published_articles: int


async def _count(db, query) -> int:
    return (await db.execute(query)).scalar_one()


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(db: DbSession, user: CurrentUser) -> DashboardResponse:
    # L'admin de contenu n'accède pas aux demandes (PRD section 12.2) :
    # ses compteurs de demandes restent à zéro.
    if user.role == UserRole.content_admin:
        total = new = in_progress = closed = 0
    else:
        base = scope_requests(select(func.count(ServiceRequest.id)), user)
        total = await _count(db, base)
        new = await _count(db, base.where(ServiceRequest.status == RequestStatus.new))
        in_progress = await _count(db, base.where(ServiceRequest.status.in_(IN_PROGRESS_STATUSES)))
        closed = await _count(db, base.where(ServiceRequest.status.in_(CLOSED_STATUSES)))
    return DashboardResponse(
        total_requests=total,
        new_requests=new,
        in_progress_requests=in_progress,
        closed_requests=closed,
        upcoming_appointments=await _count(
            db,
            select(func.count(Appointment.id)).where(
                Appointment.date >= dt.date.today(),
                Appointment.status != AppointmentStatus.cancelled,
            ),
        ),
        active_services=await _count(
            db, select(func.count(Service.id)).where(Service.status == ServiceStatus.active)
        ),
        locations=await _count(
            db, select(func.count(Location.id)).where(Location.is_visible.is_(True))
        ),
        published_articles=await _count(
            db, select(func.count(Article.id)).where(Article.status == ArticleStatus.published)
        ),
    )
