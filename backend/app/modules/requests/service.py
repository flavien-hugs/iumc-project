from fastapi import HTTPException, status
from sqlalchemy import Select

from app.models import ServiceRequest, User, UserRole


def scope_requests(query: Select, user: User) -> Select:
    """Cloisonnement par rôle (PRD section 12) : l'agent ne voit que ses
    demandes, le responsable d'agence celles de son implantation ; le super
    admin et le lecteur voient tout ; l'admin de contenu n'y accède pas."""
    if user.role == UserRole.content_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Accès refusé pour ce rôle")
    if user.role == UserRole.sales_agent:
        return query.where(ServiceRequest.agent_id == user.id)
    if user.role == UserRole.branch_manager:
        return query.where(ServiceRequest.location_id == user.location_id)
    return query


def ensure_can_read(item: ServiceRequest, user: User) -> None:
    allowed = (
        user.role in (UserRole.super_admin, UserRole.viewer)
        or (user.role == UserRole.sales_agent and item.agent_id == user.id)
        or (user.role == UserRole.branch_manager and item.location_id == user.location_id)
    )
    if not allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Accès refusé à cette demande")


def ensure_can_modify(item: ServiceRequest, user: User) -> None:
    allowed = (
        user.role == UserRole.super_admin
        or (user.role == UserRole.sales_agent and item.agent_id == user.id)
        or (user.role == UserRole.branch_manager and item.location_id == user.location_id)
    )
    if not allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Modification refusée pour ce rôle")
