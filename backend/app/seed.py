"""Peuplement initial idempotent : super admin, pôles, services, implantations.

Usage : python -m app.seed
Le mot de passe du super admin se règle via SEED_ADMIN_PASSWORD (défaut de dev sinon).
"""

import asyncio
import os

from sqlalchemy import select

from app.core.db import async_session_factory
from app.core.security import hash_password
from app.models import Division, DivisionStatus, Location, LocationStatus, Service, User, UserRole

FULL_DESCRIPTIONS = {
    "juridique": (
        "Le pôle juridique accompagne les particuliers, entreprises et investisseurs "
        "dans la rédaction, l'analyse et le suivi de leurs engagements contractuels, "
        "ainsi que dans la prévention et la gestion des litiges fonciers."
    ),
    "foncier-immobilier": (
        "Le pôle foncier et immobilier accompagne particuliers, promoteurs et industriels "
        "dans la vérification, la régularisation et le déblocage de leurs dossiers fonciers "
        "et immobiliers, urbains comme industriels."
    ),
    "agropastoral": (
        "Le pôle agropastoral est en cours de développement. Il couvrira à terme les "
        "activités agricoles, l'élevage, le transport de marchandises et le commerce "
        "d'aliments pour bovins."
    ),
}

SERVICE_SUMMARIES = {
    "bail-commercial": "Sécurisation et suivi des baux commerciaux entre bailleurs et locataires.",
    "bail-emphyteotique-industriel": "Structuration des baux emphytéotiques liés à un projet industriel.",
    "partenariats": "Rédaction et relecture des accords entre partenaires commerciaux.",
    "protocoles-accord": "Formalisation d'engagements préalables entre parties prenantes.",
    "prevention-litiges-fonciers": "Identification des risques avant qu'un différend foncier n'apparaisse.",
    "gestion-litiges-fonciers": "Suivi d'un différend foncier déjà engagé, à l'amiable ou en procédure.",
    "conseil-documentaire": "Conseil sur la constitution et la validité des pièces d'un dossier.",
    "assistance-entreprises-investisseurs": "Appui juridique transverse aux entreprises et porteurs de projet.",
    "foncier-urbain": "Démarches foncières liées à un terrain en zone urbaine.",
    "foncier-industriel": "Démarches foncières liées à un terrain à usage industriel.",
    "accompagnement-immobilier": "Suivi d'un projet immobilier, de l'acquisition à la régularisation.",
    "audit-documentaire": "Vérification de la cohérence et de la validité d'un dossier.",
    "verification-conformite": "Contrôle de la conformité d'un terrain ou d'un bien avant engagement.",
    "dossiers-acd": "Suivi d'une demande d'Attestation de Concession Définitive.",
    "dossiers-cmpf": "Suivi d'un dossier de Certificat de Morcellement Précaire et Futur.",
    "deblocage-dossiers": "Appui à la relance d'un dossier en attente ou bloqué.",
    "promoteurs-immobiliers": "Suivi dédié aux porteurs de projets immobiliers.",
    "recherche-terrains-industriels": "Identification de terrains adaptés à un projet industriel.",
    "bail-emphyteotique": "Structuration d'un bail emphytéotique foncier ou immobilier.",
    "projets-business-plans": "Appui à la structuration d'un projet et de son plan d'affaires.",
}

DIVISIONS = [
    {
        "slug": "juridique",
        "name": "Services juridiques",
        "status": DivisionStatus.active,
        "sort_order": 1,
        "short_description": (
            "Sécurisation juridique des activités commerciales, foncières, "
            "immobilières et industrielles."
        ),
        "services": [
            ("bail-commercial", "Accompagnement relatif au bail commercial"),
            ("bail-emphyteotique-industriel", "Accompagnement relatif au bail emphytéotique industriel"),
            ("partenariats", "Rédaction et analyse de partenariats"),
            ("protocoles-accord", "Rédaction et analyse de protocoles d'accord"),
            ("prevention-litiges-fonciers", "Prévention des litiges fonciers"),
            ("gestion-litiges-fonciers", "Accompagnement dans la gestion des litiges fonciers"),
            ("conseil-documentaire", "Conseil et accompagnement documentaire"),
            ("assistance-entreprises-investisseurs", "Assistance aux entreprises et investisseurs"),
        ],
    },
    {
        "slug": "foncier-immobilier",
        "name": "Foncier et immobilier",
        "status": DivisionStatus.active,
        "sort_order": 2,
        "short_description": (
            "Audit, conformité et accompagnement des démarches foncières et immobilières."
        ),
        "services": [
            ("foncier-urbain", "Accompagnement en matière de foncier urbain"),
            ("foncier-industriel", "Accompagnement en matière de foncier industriel"),
            ("accompagnement-immobilier", "Accompagnement immobilier"),
            ("audit-documentaire", "Audit documentaire"),
            ("verification-conformite", "Vérification de conformité"),
            ("dossiers-acd", "Accompagnement pour les dossiers d'ACD"),
            ("dossiers-cmpf", "Accompagnement pour les dossiers de CMPF"),
            ("deblocage-dossiers", "Accompagnement pour le déblocage de dossiers"),
            ("promoteurs-immobiliers", "Accompagnement des promoteurs immobiliers"),
            ("recherche-terrains-industriels", "Recherche de terrains à usage industriel"),
            ("bail-emphyteotique", "Accompagnement relatif au bail emphytéotique"),
            ("projets-business-plans", "Assistance à la préparation de projets et de business plans"),
        ],
    },
    {
        "slug": "agropastoral",
        "name": "Agropastoral",
        "status": DivisionStatus.coming_soon,
        "sort_order": 3,
        "short_description": (
            "Activités agricoles, élevage, transport de marchandises et commerce "
            "d'aliments pour bovins."
        ),
        "services": [],
    },
]

PLANNED_CITIES = [
    "Yamoussoukro", "Abidjan", "San Pedro", "Korhogo", "Daloa", "Gagnoa",
    "Bingerville", "Songon", "Grand-Bassam", "Bonoua", "Soubré", "Méagui",
    "Bouaflé", "Sinfra", "Zuénoula", "Oumé", "Vavoua", "Issia",
]


async def main() -> None:
    async with async_session_factory() as db:
        existing_admin = (
            await db.execute(select(User).where(User.email == "admin@iumc.ci"))
        ).scalar_one_or_none()
        if existing_admin is None:
            password = os.environ.get("SEED_ADMIN_PASSWORD", "ChangerMoi!2026")
            db.add(
                User(
                    name="Administrateur IUMC",
                    email="admin@iumc.ci",
                    password_hash=hash_password(password),
                    role=UserRole.super_admin,
                )
            )
            print("Super admin créé : admin@iumc.ci")

        for data in DIVISIONS:
            division = (
                await db.execute(select(Division).where(Division.slug == data["slug"]))
            ).scalar_one_or_none()
            if division is None:
                division = Division(
                    slug=data["slug"],
                    name=data["name"],
                    status=data["status"],
                    sort_order=data["sort_order"],
                    short_description=data["short_description"],
                    full_description=FULL_DESCRIPTIONS.get(data["slug"]),
                )
                db.add(division)
                await db.flush()
                print(f"Pôle créé : {division.name}")
            elif division.full_description is None:
                division.full_description = FULL_DESCRIPTIONS.get(data["slug"])
            for slug, title in data["services"]:
                existing = (
                    await db.execute(select(Service).where(Service.slug == slug))
                ).scalar_one_or_none()
                if existing is None:
                    db.add(
                        Service(
                            division_id=division.id,
                            slug=slug,
                            title=title,
                            summary=SERVICE_SUMMARIES.get(slug),
                        )
                    )
                elif existing.summary is None:
                    existing.summary = SERVICE_SUMMARIES.get(slug)

        headquarters = (
            await db.execute(
                select(Location).where(Location.status == LocationStatus.headquarters)
            )
        ).scalar_one_or_none()
        if headquarters is None:
            db.add(
                Location(
                    name="Siège IUMC",
                    city="Bouaké",
                    district="Koko",
                    address="Quartier Koko, entre la maternité et la mairie",
                    status=LocationStatus.headquarters,
                )
            )
            for city in PLANNED_CITIES:
                db.add(
                    Location(
                        name=f"IUMC {city}",
                        city=city,
                        status=LocationStatus.planned,
                    )
                )
            print("Implantations créées")

        await db.commit()
        print("Peuplement terminé.")


if __name__ == "__main__":
    asyncio.run(main())
