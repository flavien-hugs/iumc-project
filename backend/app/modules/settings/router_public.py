"""Lecture publique des paramètres généraux et du contenu institutionnel."""

from pydantic import BaseModel
from fastapi import APIRouter
from sqlalchemy import select

from app.core.db import DbSession
from app.models import Setting
from app.modules.settings.router import DEFAULT_ABOUT, KNOWN_KEYS, ABOUT_KEY, CompanyAbout

router = APIRouter(tags=["public-company"])


class PublicCompany(BaseModel):
    about: CompanyAbout
    contact: dict[str, str]


@router.get("/company", response_model=PublicCompany)
async def get_public_company(db: DbSession) -> PublicCompany:
    rows = (
        await db.execute(select(Setting).where(Setting.key.in_([*KNOWN_KEYS, ABOUT_KEY])))
    ).scalars().all()
    stored = {row.key: row.value for row in rows}

    about_value = stored.get(ABOUT_KEY) or DEFAULT_ABOUT
    contact = {key: str(stored.get(key) or "") for key in KNOWN_KEYS}

    return PublicCompany(about=CompanyAbout(**about_value), contact=contact)
