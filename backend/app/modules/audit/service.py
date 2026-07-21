from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.request_context import current_client_ip
from app.modules.audit.models import AuditLog


def log_action(
    db: AsyncSession,
    user_id: int | None,
    action: str,
    resource: str | None = None,
    resource_id: int | None = None,
    ip_address: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """Ajoute une entrée au journal d'activité (PRD section 11.8) dans la
    transaction courante ; l'appelant reste responsable du commit.

    `ip_address` n'a besoin d'être passé explicitement que hors contexte
    requête HTTP normal ; sinon elle est reprise automatiquement de la
    requête en cours via `RequestContextMiddleware`."""
    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            ip_address=ip_address or current_client_ip(),
            details=details,
        )
    )
