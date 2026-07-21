from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import select

from app.core.db import DbSession
from app.models import Setting, UserRole
from app.modules.audit.service import log_action
from app.core.sanitize import sanitize_html
from app.modules.auth.deps import CurrentUser, require_roles

router = APIRouter(
    prefix="/admin/settings",
    tags=["admin"],
    dependencies=[Depends(require_roles(UserRole.super_admin))],
)

# Clés éditables du MVP (coordonnées de l'entreprise, CDC section 8.14).
# Les valeurs réelles restent à fournir par IUMC (PRD section 24).
KNOWN_KEYS = [
    "company_phone",
    "company_whatsapp",
    "company_email",
    "company_address",
    "opening_hours",
    "facebook_url",
    "linkedin_url",
    "x_url",
    "youtube_url",
]


class SettingsPayload(BaseModel):
    values: dict[str, str]


@router.get("", response_model=SettingsPayload)
async def get_settings_values(db: DbSession) -> SettingsPayload:
    rows = (
        (await db.execute(select(Setting).where(Setting.key.in_(KNOWN_KEYS)))).scalars().all()
    )
    stored = {row.key: str(row.value) if row.value is not None else "" for row in rows}
    return SettingsPayload(values={key: stored.get(key, "") for key in KNOWN_KEYS})


@router.patch("", status_code=status.HTTP_204_NO_CONTENT)
async def update_settings_values(
    payload: SettingsPayload, db: DbSession, user: CurrentUser
) -> None:
    rows = (
        (await db.execute(select(Setting).where(Setting.key.in_(KNOWN_KEYS)))).scalars().all()
    )
    existing = {row.key: row for row in rows}
    for key, value in payload.values.items():
        if key not in KNOWN_KEYS:
            continue
        if key in existing:
            existing[key].value = value
        else:
            db.add(Setting(key=key, value=value))
    log_action(db, user.id, "update", resource="settings")
    await db.commit()


# ---------------------------------------------------------------------------
# Contenu institutionnel de la page « Qui sommes-nous » (PRD sections 2, 3).
# Stocké en un seul enregistrement JSONB (clé "company_about"), distinct des
# clés simples ci-dessus qui sont contraintes à des chaînes.
# ---------------------------------------------------------------------------

ABOUT_KEY = "company_about"

# Contenu par défaut : celui déjà rédigé pour le site, retourné tel quel
# lorsque aucune modification n'a encore été enregistrée depuis le panel.
DEFAULT_ABOUT = {
    "founded_year": "2026",
    "legal_form": "Entreprise individuelle de droit ivoirien",
    "headquarters": "Bouaké, quartier Koko",
    "vision": (
        "<p>Devenir, à l'horizon 2030, une holding qui soit la porte d'accès de référence, "
        "en Côte d'Ivoire et en Afrique, à <strong>la sécurité juridique absolue</strong> "
        "dont chacun a besoin, où qu'il soit, pour la réalisation sereine de son projet "
        "personnel ou professionnel.</p>"
    ),
    "missions": [
        "Services juridiques dans les domaines commercial, de l'immobilier et industriel — le cœur de l'objet social d'IUMC",
        "Accompagnement foncier et immobilier, urbain comme industriel",
        "Audit documentaire et vérification de conformité",
        "Assistance aux entreprises, investisseurs et communautés villageoises",
        "Prévention et accompagnement dans la gestion des litiges fonciers",
        "À moyen terme : activités agropastorales, puis, à titre accessoire, transport de marchandises et commerce d'aliments pour bovins",
    ],
    "values": [
        "Respect", "Intégrité", "Transparence", "Excellence", "Orientation client", "Innovation",
    ],
    "differentiators": [
        {
            "title": "Un relais fiable des services de l'État",
            "description": (
                "Dans l'écosystème de l'ingénierie immobilière, IUMC agit comme un acteur "
                "clé et un relais fiable des services de l'État auprès des citoyens, des "
                "opérateurs économiques et des investisseurs industriels."
            ),
        },
        {
            "title": "Des packages de services sur mesure",
            "description": (
                "Des offres pluridisciplinaires assemblées selon la situation réelle de "
                "chaque client — particulier, entreprise, communauté villageoise ou "
                "industriel — plutôt qu'un service isolé."
            ),
        },
        {
            "title": "Un modèle de gestion intégrée",
            "description": (
                "Un seul interlocuteur coordonne les volets juridique, foncier, immobilier "
                "et industriel d'un même projet, du premier échange à l'aboutissement du "
                "dossier."
            ),
        },
        {
            "title": "Un maillage progressif du territoire",
            "description": (
                "Une présence qui s'étend ville après ville depuis le siège de Bouaké, "
                "pour rapprocher les services de leurs bénéficiaires."
            ),
        },
    ],
}


class Differentiator(BaseModel):
    title: str
    description: str


class CompanyAbout(BaseModel):
    founded_year: str
    legal_form: str
    headquarters: str
    vision: str
    missions: list[str]
    values: list[str]
    differentiators: list[Differentiator]


class CompanyAboutUpdate(BaseModel):
    """Mise à jour partielle : seuls les champs fournis sont remplacés,
    pour que chaque onglet de la page Paramètres puisse enregistrer sa
    propre section sans écraser les brouillons en cours des autres onglets
    (tous partagent le même enregistrement `company_about`)."""

    founded_year: str | None = None
    legal_form: str | None = None
    headquarters: str | None = None
    vision: str | None = None
    missions: list[str] | None = None
    values: list[str] | None = None
    differentiators: list[Differentiator] | None = None


@router.get("/about", response_model=CompanyAbout)
async def get_company_about(db: DbSession) -> CompanyAbout:
    row = (
        await db.execute(select(Setting).where(Setting.key == ABOUT_KEY))
    ).scalar_one_or_none()
    return CompanyAbout(**(row.value if row and row.value else DEFAULT_ABOUT))


@router.patch("/about", response_model=CompanyAbout)
async def update_company_about(
    payload: CompanyAboutUpdate, db: DbSession, user: CurrentUser
) -> CompanyAbout:
    row = (
        await db.execute(select(Setting).where(Setting.key == ABOUT_KEY))
    ).scalar_one_or_none()
    current = row.value if row and row.value else DEFAULT_ABOUT
    updates = payload.model_dump(exclude_unset=True)
    if "vision" in updates:
        updates["vision"] = sanitize_html(updates["vision"])
    if "differentiators" in updates:
        for item in updates["differentiators"]:
            item["description"] = sanitize_html(item["description"])
    value = {**current, **updates}
    if row is None:
        db.add(Setting(key=ABOUT_KEY, value=value))
    else:
        row.value = value
    log_action(
        db, user.id, "update", resource="settings",
        details={"key": ABOUT_KEY, "fields": list(updates.keys())},
    )
    await db.commit()
    return CompanyAbout(**value)
