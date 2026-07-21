import enum
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum as SaEnum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class DivisionStatus(str, enum.Enum):
    active = "active"
    coming_soon = "coming_soon"
    inactive = "inactive"
    hidden = "hidden"


class ServiceStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class ArticleStatus(str, enum.Enum):
    draft = "draft"
    scheduled = "scheduled"
    published = "published"
    archived = "archived"


class Division(Base):
    """Pôle d'activité au sens du PRD (juridique, foncier-immobilier, agropastoral)."""

    __tablename__ = "division"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    slug: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    image: Mapped[str | None] = mapped_column(String(255))
    icon: Mapped[str | None] = mapped_column(String(100))
    short_description: Mapped[str | None] = mapped_column(Text)
    full_description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[DivisionStatus] = mapped_column(
        SaEnum(DivisionStatus, name="division_status"), default=DivisionStatus.active
    )
    sort_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    services: Mapped[list["Service"]] = relationship(back_populates="division")


class Service(Base):
    __tablename__ = "service"

    id: Mapped[int] = mapped_column(primary_key=True)
    division_id: Mapped[int] = mapped_column(ForeignKey("division.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    image: Mapped[str | None] = mapped_column(String(255))
    audiences: Mapped[list[Any] | None] = mapped_column(JSONB)
    goals: Mapped[list[Any] | None] = mapped_column(JSONB)
    benefits: Mapped[list[Any] | None] = mapped_column(JSONB)
    steps: Mapped[list[Any] | None] = mapped_column(JSONB)
    documents: Mapped[list[Any] | None] = mapped_column(JSONB)
    status: Mapped[ServiceStatus] = mapped_column(
        SaEnum(ServiceStatus, name="service_status"), default=ServiceStatus.active
    )
    seo_title: Mapped[str | None] = mapped_column(String(255))
    seo_description: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    division: Mapped[Division] = relationship(back_populates="services")


class Article(Base):
    __tablename__ = "article"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str | None] = mapped_column(Text)
    image: Mapped[str | None] = mapped_column(String(255))
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    category: Mapped[str | None] = mapped_column(String(100))
    keywords: Mapped[list[Any] | None] = mapped_column(JSONB)
    status: Mapped[ArticleStatus] = mapped_column(
        SaEnum(ArticleStatus, name="article_status"), default=ArticleStatus.draft
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    seo_title: Mapped[str | None] = mapped_column(String(255))
    seo_description: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Faq(Base):
    __tablename__ = "faq"

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(String(500))
    answer: Mapped[str] = mapped_column(Text)
    division_id: Mapped[int | None] = mapped_column(ForeignKey("division.id", ondelete="CASCADE"))
    service_id: Mapped[int | None] = mapped_column(ForeignKey("service.id", ondelete="CASCADE"))
    is_published: Mapped[bool] = mapped_column(default=True)
    sort_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
