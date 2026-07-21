# Agrégateur de modèles et d'enums (ADR-0014).
#
# Double rôle : stabilité des imports applicatifs (`from app.models import X`)
# et découverte des tables par Alembic (migrations/env.py importe ce module).
# À tenir à jour dès qu'un module ajoute un modèle.

from app.modules.audit.models import AuditLog
from app.modules.contact.models import ContactMessage
from app.modules.content.models import (
    Article,
    ArticleStatus,
    Division,
    DivisionStatus,
    Faq,
    Service,
    ServiceStatus,
)
from app.modules.locations.models import Location, LocationStatus
from app.modules.media.models import MediaFile
from app.modules.notifications.models import Notification
from app.modules.requests.models import (
    Appointment,
    AppointmentStatus,
    ClientType,
    ContactPreference,
    RequestStatus,
    ServiceRequest,
    ServiceRequestHistory,
)
from app.modules.settings.models import Setting
from app.modules.users.models import PasswordResetToken, User, UserRole

__all__ = [
    "Appointment",
    "AppointmentStatus",
    "Article",
    "ArticleStatus",
    "AuditLog",
    "ClientType",
    "ContactMessage",
    "ContactPreference",
    "Division",
    "DivisionStatus",
    "Faq",
    "Location",
    "LocationStatus",
    "MediaFile",
    "Notification",
    "PasswordResetToken",
    "RequestStatus",
    "Service",
    "ServiceRequest",
    "ServiceRequestHistory",
    "ServiceStatus",
    "Setting",
    "User",
    "UserRole",
]
