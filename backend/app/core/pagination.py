"""Pagination générique pour les listes du panel (offset/limit)."""

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class PageParams:
    """Dépendance FastAPI : `page=Depends(PageParams)` dans un endpoint."""

    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
    ) -> None:
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


async def paginate(db: AsyncSession, query: Select, params: PageParams) -> tuple[list, int]:
    """Exécute `query` avec offset/limit et retourne (lignes, total).

    Le total est calculé en enveloppant `query` dans une sous-requête plutôt
    qu'en substituant ses colonnes par `count(*)` : sur un select à entité
    unique sans `.join()` explicite, `with_only_columns` n'a plus aucune
    colonne d'où déduire le FROM et le laisse tomber silencieusement,
    produisant un `SELECT count(*)` sans table (qui vaut 1, pas 0 ni le vrai
    total). Compter depuis une sous-requête reste correct quelle que soit la
    forme de `query`.
    """
    count_query = select(func.count()).select_from(query.order_by(None).subquery())
    total = (await db.execute(count_query)).scalar_one()
    rows = (
        await db.execute(query.offset(params.offset).limit(params.page_size))
    ).all()
    return rows, total
