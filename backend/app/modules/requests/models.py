import datetime as dt
import enum

from sqlalchemy import Date, DateTime, Enum as SaEnum, ForeignKey, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class RequestStatus(str, enum.Enum):
    new = "new"
    to_contact = "to_contact"
    appointment_scheduled = "appointment_scheduled"
    in_progress = "in_progress"
    awaiting_client = "awaiting_client"
    processed = "processed"
    closed = "closed"
    rejected = "rejected"
    archived = "archived"


class ClientType(str, enum.Enum):
    individual = "individual"
    company = "company"
    industrial = "industrial"
    developer = "developer"
    community = "community"


class ContactPreference(str, enum.Enum):
    phone = "phone"
    email = "email"
    whatsapp = "whatsapp"


class AppointmentStatus(str, enum.Enum):
    proposed = "proposed"
    confirmed = "confirmed"
    rescheduled = "rescheduled"
    cancelled = "cancelled"
    completed = "completed"


class ServiceRequest(Base):
    """Demande de prestation au sens du PRD (section 10.8)."""

    __tablename__ = "service_request"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Renseignée juste après le premier flush (construite à partir de l'id),
    # d'où la nullabilité malgré l'unicité. Le format IUMC-DEM-AAAA-NNNNN est
    # imposé par le PRD (référence métier, reste en français).
    reference: Mapped[str | None] = mapped_column(String(30), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(150))
    company: Mapped[str | None] = mapped_column(String(150))
    phone: Mapped[str] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100))
    client_type: Mapped[ClientType | None] = mapped_column(SaEnum(ClientType, name="client_type"))
    division_id: Mapped[int] = mapped_column(ForeignKey("division.id", ondelete="RESTRICT"))
    service_id: Mapped[int] = mapped_column(ForeignKey("service.id", ondelete="RESTRICT"))
    subject: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    contact_preference: Mapped[ContactPreference] = mapped_column(
        SaEnum(ContactPreference, name="contact_preference"),
        default=ContactPreference.phone,
    )
    preferred_appointment_date: Mapped[dt.date | None] = mapped_column(Date)
    attachment: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[RequestStatus] = mapped_column(
        SaEnum(RequestStatus, name="request_status"), default=RequestStatus.new, index=True
    )
    agent_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("location.id", ondelete="SET NULL")
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ServiceRequestHistory(Base):
    __tablename__ = "service_request_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("service_request.id", ondelete="CASCADE"))
    previous_status: Mapped[RequestStatus | None] = mapped_column(
        SaEnum(RequestStatus, name="request_status", create_type=False)
    )
    new_status: Mapped[RequestStatus] = mapped_column(
        SaEnum(RequestStatus, name="request_status", create_type=False)
    )
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Appointment(Base):
    __tablename__ = "appointment"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("service_request.id", ondelete="CASCADE"))
    date: Mapped[dt.date] = mapped_column(Date)
    time: Mapped[dt.time | None] = mapped_column(Time)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    status: Mapped[AppointmentStatus] = mapped_column(
        SaEnum(AppointmentStatus, name="appointment_status"), default=AppointmentStatus.proposed
    )
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
