import datetime as dt
import re
import unicodedata

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from app.core.db import DbSession
from app.core.pagination import Page, PageParams, paginate
from app.core.sanitize import sanitize_html
from app.models import Division, DivisionStatus, Service, ServiceStatus, User, UserRole
from app.modules.audit.service import log_action
from app.modules.auth.deps import CurrentUser, require_roles

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    # Gestion des contenus : super admin et administrateur de contenu (PRD section 12.2).
    dependencies=[Depends(require_roles(UserRole.super_admin, UserRole.content_admin))],
)


def _slugify(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text).strip("-").lower()
    return slug or "item"


async def _unique_slug(db: DbSession, model: type, title: str) -> str:
    base = _slugify(title)
    slug = base
    suffix = 2
    while (
        await db.execute(select(model.id).where(model.slug == slug))
    ).scalar_one_or_none() is not None:
        slug = f"{base}-{suffix}"
        suffix += 1
    return slug


class ServiceRow(BaseModel):
    id: int
    title: str
    slug: str
    status: str
    deleted_at: dt.datetime | None


class DivisionRow(BaseModel):
    id: int
    name: str
    slug: str
    status: str
    sort_order: int
    services: list[ServiceRow]


class DivisionUpdate(BaseModel):
    status: DivisionStatus


class ServiceCreate(BaseModel):
    division_id: int
    title: str


class ServiceUpdate(BaseModel):
    title: str | None = None
    status: ServiceStatus | None = None


@router.get("/divisions", response_model=list[DivisionRow])
async def list_divisions(db: DbSession) -> list[DivisionRow]:
    divisions = (
        (
            await db.execute(
                select(Division)
                .options(selectinload(Division.services))
                .order_by(Division.sort_order)
            )
        )
        .scalars()
        .all()
    )
    return [
        DivisionRow(
            id=division.id,
            name=division.name,
            slug=division.slug,
            status=division.status.value,
            sort_order=division.sort_order,
            services=[
                ServiceRow(
                    id=service.id, title=service.title, slug=service.slug,
                    status=service.status.value, deleted_at=service.deleted_at,
                )
                for service in sorted(division.services, key=lambda item: item.title)
            ],
        )
        for division in divisions
    ]


@router.patch("/divisions/{division_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_division(
    division_id: int, payload: DivisionUpdate, db: DbSession, user: CurrentUser
) -> None:
    division = await db.get(Division, division_id)
    if division is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pôle introuvable")
    division.status = payload.status
    log_action(
        db, user.id, "status_change", resource="division", resource_id=division.id,
        details={"status": payload.status.value},
    )
    await db.commit()


@router.post("/services", response_model=ServiceRow, status_code=status.HTTP_201_CREATED)
async def create_service(payload: ServiceCreate, db: DbSession, user: CurrentUser) -> ServiceRow:
    title = payload.title.strip()
    if not title:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Le titre est requis")
    division = await db.get(Division, payload.division_id)
    if division is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pôle introuvable")
    service = Service(
        division_id=division.id, title=title, slug=await _unique_slug(db, Service, title),
    )
    db.add(service)
    await db.flush()
    log_action(db, user.id, "create", resource="service", resource_id=service.id)
    await db.commit()
    return ServiceRow(
        id=service.id, title=service.title, slug=service.slug,
        status=service.status.value, deleted_at=service.deleted_at,
    )


@router.patch("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_service(
    service_id: int, payload: ServiceUpdate, db: DbSession, user: CurrentUser
) -> None:
    service = await db.get(Service, service_id)
    if service is None or service.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Service introuvable")
    details: dict[str, str] = {}
    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Le titre est requis")
        service.title = title
        details["title"] = title
    if payload.status is not None:
        service.status = payload.status
        details["status"] = payload.status.value
    if details:
        log_action(
            db, user.id, "update", resource="service", resource_id=service.id, details=details,
        )
        await db.commit()


@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(service_id: int, db: DbSession, user: CurrentUser) -> None:
    """Suppression logique : `service.service_id` est référencé en `RESTRICT`
    par les demandes déjà soumises (historique), un hard delete casserait ces
    lignes. Le service est aussi désactivé pour disparaître immédiatement du
    site public, sans attendre une éventuelle restauration."""
    service = await db.get(Service, service_id)
    if service is None or service.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Service introuvable")
    service.deleted_at = dt.datetime.now(dt.UTC)
    service.status = ServiceStatus.inactive
    log_action(db, user.id, "delete", resource="service", resource_id=service.id)
    await db.commit()


@router.post("/services/{service_id}/restore", status_code=status.HTTP_204_NO_CONTENT)
async def restore_service(service_id: int, db: DbSession, user: CurrentUser) -> None:
    service = await db.get(Service, service_id)
    if service is None or service.deleted_at is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Service supprimé introuvable")
    service.deleted_at = None
    log_action(db, user.id, "restore", resource="service", resource_id=service.id)
    await db.commit()


# ---------------------------------------------------------------------------
# Articles (PRD section 10.6 / CDC section 8.8)
# ---------------------------------------------------------------------------

from app.models import Article, ArticleStatus


class ArticleRow(BaseModel):
    id: int
    title: str
    slug: str
    category: str | None
    status: str
    summary: str | None
    body: str | None
    author_id: int | None
    author_name: str | None
    published_at: dt.datetime | None
    updated_at: dt.datetime


class ArticleCreate(BaseModel):
    title: str
    category: str | None = None
    summary: str | None = None
    body: str | None = None
    status: ArticleStatus = ArticleStatus.draft


class ArticleUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    summary: str | None = None
    body: str | None = None
    status: ArticleStatus | None = None


def _article_row(article: Article, author_name: str | None = None) -> ArticleRow:
    return ArticleRow(
        id=article.id,
        title=article.title,
        slug=article.slug,
        category=article.category,
        status=article.status.value,
        summary=article.summary,
        body=article.body,
        author_id=article.author_id,
        author_name=author_name,
        published_at=article.published_at,
        updated_at=article.updated_at,
    )


@router.get("/articles", response_model=Page[ArticleRow])
async def list_articles(
    db: DbSession,
    q: str | None = None,
    status_filter: ArticleStatus | None = None,
    category: str | None = None,
    author_id: int | None = None,
    params: PageParams = Depends(),
) -> Page[ArticleRow]:
    query = select(Article, User.name).outerjoin(User, Article.author_id == User.id)
    if status_filter is not None:
        query = query.where(Article.status == status_filter)
    if category:
        query = query.where(Article.category == category)
    if author_id is not None:
        query = query.where(Article.author_id == author_id)
    if q:
        pattern = f"%{q.strip()}%"
        query = query.where(or_(Article.title.ilike(pattern), Article.summary.ilike(pattern)))
    query = query.order_by(Article.updated_at.desc())
    rows, total = await paginate(db, query, params)
    return Page(
        items=[_article_row(article, author_name) for article, author_name in rows],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


@router.post("/articles", response_model=ArticleRow, status_code=status.HTTP_201_CREATED)
async def create_article(payload: ArticleCreate, db: DbSession, user: CurrentUser) -> ArticleRow:
    article = Article(
        title=payload.title,
        slug=await _unique_slug(db, Article, payload.title),
        category=payload.category,
        summary=sanitize_html(payload.summary),
        body=sanitize_html(payload.body),
        status=payload.status,
        author_id=user.id,
        published_at=dt.datetime.now(dt.UTC) if payload.status == ArticleStatus.published else None,
    )
    db.add(article)
    await db.flush()
    log_action(db, user.id, "create", resource="article", resource_id=article.id)
    await db.commit()
    return _article_row(article, user.name)


@router.patch("/articles/{article_id}", response_model=ArticleRow)
async def update_article(
    article_id: int, payload: ArticleUpdate, db: DbSession, user: CurrentUser
) -> ArticleRow:
    article = await db.get(Article, article_id)
    if article is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Article introuvable")
    if payload.title is not None:
        article.title = payload.title
    if payload.category is not None:
        article.category = payload.category
    if payload.summary is not None:
        article.summary = sanitize_html(payload.summary)
    if payload.body is not None:
        article.body = sanitize_html(payload.body)
    if payload.status is not None:
        if payload.status == ArticleStatus.published and article.published_at is None:
            article.published_at = dt.datetime.now(dt.UTC)
        article.status = payload.status
    log_action(db, user.id, "update", resource="article", resource_id=article.id)
    await db.commit()
    # Voir le commentaire équivalent dans locations/router_admin.py : sans ce
    # refresh, la lecture de `updated_at` (colonne à onupdate serveur) après
    # un UPDATE plante en async (MissingGreenlet).
    await db.refresh(article)
    return _article_row(article)


@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(article_id: int, db: DbSession, user: CurrentUser) -> None:
    article = await db.get(Article, article_id)
    if article is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Article introuvable")
    log_action(db, user.id, "delete", resource="article", resource_id=article_id)
    await db.delete(article)
    await db.commit()


# ---------------------------------------------------------------------------
# FAQ (PRD section 10.9 / CDC section 8.9)
# ---------------------------------------------------------------------------

from app.models import Faq


class FaqRow(BaseModel):
    id: int
    question: str
    answer: str
    division_id: int | None
    service_id: int | None
    is_published: bool
    sort_order: int


class FaqCreate(BaseModel):
    question: str
    answer: str
    division_id: int | None = None
    service_id: int | None = None
    is_published: bool = True
    sort_order: int = 0


class FaqUpdate(BaseModel):
    question: str | None = None
    answer: str | None = None
    division_id: int | None = None
    service_id: int | None = None
    is_published: bool | None = None
    sort_order: int | None = None


def _faq_row(faq: Faq) -> FaqRow:
    return FaqRow(
        id=faq.id,
        question=faq.question,
        answer=faq.answer,
        division_id=faq.division_id,
        service_id=faq.service_id,
        is_published=faq.is_published,
        sort_order=faq.sort_order,
    )


@router.get("/faqs", response_model=Page[FaqRow])
async def list_faqs(
    db: DbSession,
    q: str | None = None,
    is_published: bool | None = None,
    params: PageParams = Depends(),
) -> Page[FaqRow]:
    query = select(Faq)
    if is_published is not None:
        query = query.where(Faq.is_published == is_published)
    if q:
        pattern = f"%{q.strip()}%"
        query = query.where(or_(Faq.question.ilike(pattern), Faq.answer.ilike(pattern)))
    query = query.order_by(Faq.sort_order, Faq.id)
    rows, total = await paginate(db, query, params)
    return Page(
        items=[_faq_row(row[0]) for row in rows],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


@router.post("/faqs", response_model=FaqRow, status_code=status.HTTP_201_CREATED)
async def create_faq(payload: FaqCreate, db: DbSession, user: CurrentUser) -> FaqRow:
    faq = Faq(**{**payload.model_dump(), "answer": sanitize_html(payload.answer)})
    db.add(faq)
    await db.flush()
    log_action(db, user.id, "create", resource="faq", resource_id=faq.id)
    await db.commit()
    return _faq_row(faq)


@router.patch("/faqs/{faq_id}", response_model=FaqRow)
async def update_faq(
    faq_id: int, payload: FaqUpdate, db: DbSession, user: CurrentUser
) -> FaqRow:
    faq = await db.get(Faq, faq_id)
    if faq is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(faq, field, sanitize_html(value) if field == "answer" else value)
    log_action(db, user.id, "update", resource="faq", resource_id=faq.id)
    await db.commit()
    return _faq_row(faq)
