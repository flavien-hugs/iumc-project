from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.core.db import DbSession
from app.core.pagination import Page, PageParams, paginate
from app.core.sanitize import sanitize_html
from app.models import Location, LocationStatus, UserRole
from app.modules.audit.service import log_action
from app.modules.auth.deps import CurrentUser, require_roles

router = APIRouter(
    prefix="/admin/locations",
    tags=["admin"],
    # Gestion des implantations : super admin et administrateur de contenu (PRD section 12.2).
    dependencies=[Depends(require_roles(UserRole.super_admin, UserRole.content_admin))],
)


class LocationRow(BaseModel):
    id: int
    name: str
    city: str
    district: str | None
    address: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    status: str
    phone: str | None
    whatsapp: str | None
    email: str | None
    opening_hours: str | None
    manager_name: str | None
    description: str | None
    is_visible: bool
    updated_at: datetime


class LocationCreate(BaseModel):
    name: str
    city: str
    district: str | None = None
    address: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    status: LocationStatus = LocationStatus.planned
    phone: str | None = None
    whatsapp: str | None = None
    email: str | None = None
    opening_hours: str | None = None
    manager_name: str | None = None
    description: str | None = None
    is_visible: bool = True


class LocationUpdate(BaseModel):
    name: str | None = None
    city: str | None = None
    district: str | None = None
    address: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    status: LocationStatus | None = None
    phone: str | None = None
    whatsapp: str | None = None
    email: str | None = None
    opening_hours: str | None = None
    manager_name: str | None = None
    description: str | None = None
    is_visible: bool | None = None


def _to_row(location: Location) -> LocationRow:
    return LocationRow(
        id=location.id,
        name=location.name,
        city=location.city,
        district=location.district,
        address=location.address,
        latitude=location.latitude,
        longitude=location.longitude,
        status=location.status.value,
        phone=location.phone,
        whatsapp=location.whatsapp,
        email=location.email,
        opening_hours=location.opening_hours,
        manager_name=location.manager_name,
        description=location.description,
        is_visible=location.is_visible,
        updated_at=location.updated_at,
    )


@router.get("", response_model=Page[LocationRow])
async def list_locations(
    db: DbSession, _: CurrentUser, params: PageParams = Depends()
) -> Page[LocationRow]:
    query = select(Location).order_by(Location.status, Location.city)
    rows, total = await paginate(db, query, params)
    return Page(
        items=[_to_row(row[0]) for row in rows],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


@router.post("", response_model=LocationRow, status_code=status.HTTP_201_CREATED)
async def create_location(
    payload: LocationCreate, db: DbSession, user: CurrentUser
) -> LocationRow:
    data = payload.model_dump()
    data["description"] = sanitize_html(data["description"])
    location = Location(**data)
    db.add(location)
    await db.flush()
    log_action(db, user.id, "create", resource="location", resource_id=location.id)
    await db.commit()
    return _to_row(location)


@router.patch("/{location_id}", response_model=LocationRow)
async def update_location(
    location_id: int, payload: LocationUpdate, db: DbSession, user: CurrentUser
) -> LocationRow:
    location = await db.get(Location, location_id)
    if location is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Implantation introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(location, field, sanitize_html(value) if field == "description" else value)
    log_action(db, user.id, "update", resource="location", resource_id=location.id)
    await db.commit()
    # `updated_at` est calculée côté serveur (onupdate) : après un UPDATE (à la
    # différence d'un INSERT, qui la récupère via RETURNING), SQLAlchemy la
    # marque seulement "expirée" plutôt que de la relire. Y accéder sans ce
    # refresh déclenche une IO implicite hors contexte async (MissingGreenlet).
    await db.refresh(location)
    return _to_row(location)


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(location_id: int, db: DbSession, user: CurrentUser) -> None:
    location = await db.get(Location, location_id)
    if location is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Implantation introuvable")
    log_action(db, user.id, "delete", resource="location", resource_id=location_id)
    await db.delete(location)
    await db.commit()
