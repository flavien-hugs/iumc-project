from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import func, select, update

from app.core.db import DbSession, async_session_factory
from app.core.pagination import PageParams, paginate
from app.core.redis import get_redis
from app.models import Notification, User
from app.modules.auth.deps import CurrentUser

router = APIRouter(prefix="/admin/notifications", tags=["admin"])


class NotificationRow(BaseModel):
    id: int
    type: str
    title: str
    resource: str | None
    resource_id: int | None
    is_read: bool
    created_at: datetime


class NotificationPage(BaseModel):
    items: list[NotificationRow]
    total: int
    page: int
    page_size: int
    unread_count: int


def _to_row(item: Notification) -> NotificationRow:
    return NotificationRow(
        id=item.id,
        type=item.type,
        title=item.title,
        resource=item.resource,
        resource_id=item.resource_id,
        is_read=item.is_read,
        created_at=item.created_at,
    )


@router.get("", response_model=NotificationPage)
async def list_notifications(
    db: DbSession, user: CurrentUser, params: PageParams = Depends()
) -> NotificationPage:
    unread_count = (
        await db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user.id, Notification.is_read.is_(False)
            )
        )
    ).scalar_one()
    query = (
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
    )
    rows, total = await paginate(db, query, params)
    return NotificationPage(
        items=[_to_row(row[0]) for row in rows],
        total=total,
        page=params.page,
        page_size=params.page_size,
        unread_count=unread_count,
    )


@router.post("/mark-read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(db: DbSession, user: CurrentUser) -> None:
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user.id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
    await db.commit()


@router.post("/{notification_id}/mark-read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_read(notification_id: int, db: DbSession, user: CurrentUser) -> None:
    notification = await db.get(Notification, notification_id)
    if notification is None or notification.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification introuvable")
    notification.is_read = True
    await db.commit()


async def _is_still_usable(user_id: int) -> bool:
    async with async_session_factory() as session:
        current = await session.get(User, user_id)
        return current is not None and current.is_usable


@router.get("/stream")
async def stream_notifications(request: Request, user: CurrentUser) -> StreamingResponse:
    """Flux SSE (ADR-0016, remplace le polling de l'ADR-0010) : pousse les
    notifications nouvellement créées via un abonnement Redis Pub/Sub, sans
    rejouer l'historique — `GET /admin/notifications` reste la source de
    vérité pour la resynchronisation initiale au chargement du panel."""
    user_id = user.id
    channel = f"notifications:{user_id}"

    async def event_generator():
        pubsub = get_redis().pubsub()
        await pubsub.subscribe(channel)
        try:
            yield "retry: 3000\n\n"
            idle_cycles = 0
            while True:
                if await request.is_disconnected():
                    break
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=15)
                if message and message.get("type") == "message":
                    yield f"data: {message['data']}\n\n"
                    idle_cycles = 0
                    continue
                idle_cycles += 1
                yield ": heartbeat\n\n"
                # Le cookie JWT n'est vérifié qu'à l'ouverture de la connexion ;
                # une suspension/suppression pendant que le flux est ouvert ne
                # coupe donc pas la connexion sans cette revérification
                # périodique (~toutes les 4 battements, 1 min).
                if idle_cycles >= 4:
                    idle_cycles = 0
                    if not await _is_still_usable(user_id):
                        break
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
