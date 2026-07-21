from decimal import Decimal

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from app.core.db import DbSession
from app.models import Location

router = APIRouter(tags=["public-locations"])


class PublicLocation(BaseModel):
    name: str
    city: str
    district: str | None
    address: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    status: str
    phone: str | None
    whatsapp: str | None
    opening_hours: str | None


@router.get("/locations", response_model=list[PublicLocation])
async def list_public_locations(db: DbSession) -> list[PublicLocation]:
    locations = (
        (
            await db.execute(
                select(Location)
                .where(Location.is_visible.is_(True))
                .order_by(Location.status, Location.city)
            )
        )
        .scalars()
        .all()
    )
    return [
        PublicLocation(
            name=location.name,
            city=location.city,
            district=location.district,
            address=location.address,
            latitude=location.latitude,
            longitude=location.longitude,
            status=location.status.value,
            phone=location.phone,
            whatsapp=location.whatsapp,
            opening_hours=location.opening_hours,
        )
        for location in locations
    ]
