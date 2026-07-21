"""Lecture publique des contenus administrables (site vitrine, SSR)."""

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from app.core.db import DbSession
from app.core.pagination import Page, PageParams, paginate
from app.models import (
    Article,
    ArticleStatus,
    Division,
    DivisionStatus,
    Faq,
    ServiceStatus,
    User,
)

router = APIRouter(tags=["public-content"])

VISIBLE_DIVISION_STATUSES = (DivisionStatus.active, DivisionStatus.coming_soon)


class PublicService(BaseModel):
    id: int
    slug: str
    title: str
    summary: str | None
    description: str | None


class PublicDivision(BaseModel):
    id: int
    slug: str
    name: str
    status: str
    short_description: str | None
    full_description: str | None
    services: list[PublicService]


class PublicArticleSummary(BaseModel):
    slug: str
    title: str
    category: str | None
    summary: str | None
    published_at: dt.datetime | None


class PublicArticleDetail(PublicArticleSummary):
    body: str | None
    author_name: str | None


class PublicFaq(BaseModel):
    question: str
    answer: str
    division_id: int | None
    service_id: int | None


@router.get("/divisions", response_model=list[PublicDivision])
async def list_public_divisions(db: DbSession) -> list[PublicDivision]:
    divisions = (
        (
            await db.execute(
                select(Division)
                .options(selectinload(Division.services))
                .where(Division.status.in_(VISIBLE_DIVISION_STATUSES))
                .order_by(Division.sort_order)
            )
        )
        .scalars()
        .all()
    )
    return [
        PublicDivision(
            id=division.id,
            slug=division.slug,
            name=division.name,
            status=division.status.value,
            short_description=division.short_description,
            full_description=division.full_description,
            services=[
                PublicService(
                    id=service.id,
                    slug=service.slug,
                    title=service.title,
                    summary=service.summary,
                    description=service.description,
                )
                for service in sorted(division.services, key=lambda item: item.title)
                if service.status == ServiceStatus.active
            ],
        )
        for division in divisions
    ]


@router.get("/articles", response_model=Page[PublicArticleSummary])
async def list_public_articles(
    db: DbSession,
    q: str | None = None,
    category: str | None = None,
    params: PageParams = Depends(),
) -> Page[PublicArticleSummary]:
    query = select(Article).where(Article.status == ArticleStatus.published)
    if category:
        query = query.where(Article.category == category)
    if q:
        pattern = f"%{q.strip()}%"
        query = query.where(or_(Article.title.ilike(pattern), Article.summary.ilike(pattern)))
    query = query.order_by(Article.published_at.desc())
    rows, total = await paginate(db, query, params)
    return Page(
        items=[
            PublicArticleSummary(
                slug=article.slug,
                title=article.title,
                category=article.category,
                summary=article.summary,
                published_at=article.published_at,
            )
            for (article,) in rows
        ],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


@router.get("/article-categories", response_model=list[str])
async def list_public_article_categories(db: DbSession) -> list[str]:
    """Catégories distinctes des articles publiés (filtres de la page Actualités)."""
    rows = (
        await db.execute(
            select(Article.category)
            .where(
                Article.status == ArticleStatus.published,
                Article.category.is_not(None),
                Article.category != "",
            )
            .distinct()
            .order_by(Article.category)
        )
    ).scalars()
    return list(rows)


@router.get("/articles/{slug}", response_model=PublicArticleDetail)
async def get_public_article(slug: str, db: DbSession) -> PublicArticleDetail:
    row = (
        await db.execute(
            select(Article, User.name)
            .outerjoin(User, Article.author_id == User.id)
            .where(Article.slug == slug, Article.status == ArticleStatus.published)
        )
    ).first()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Article introuvable")
    article, author_name = row
    return PublicArticleDetail(
        slug=article.slug,
        title=article.title,
        category=article.category,
        summary=article.summary,
        published_at=article.published_at,
        body=article.body,
        author_name=author_name,
    )


@router.get("/faqs", response_model=list[PublicFaq])
async def list_public_faqs(db: DbSession) -> list[PublicFaq]:
    faqs = (
        (
            await db.execute(
                select(Faq).where(Faq.is_published.is_(True)).order_by(Faq.sort_order, Faq.id)
            )
        )
        .scalars()
        .all()
    )
    return [
        PublicFaq(
            question=faq.question,
            answer=faq.answer,
            division_id=faq.division_id,
            service_id=faq.service_id,
        )
        for faq in faqs
    ]
