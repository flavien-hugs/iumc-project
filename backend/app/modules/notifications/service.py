"""Publication Redis Pub/Sub des notifications (ADR-0016).

À appeler après le `commit()` de la transaction qui a créé la notification
(jamais avant : on ne veut pas notifier un client d'une ligne qui pourrait
encore être annulée par un rollback)."""

import json

from app.core.redis import get_redis
from app.modules.notifications.models import Notification


def notification_payload(notification: Notification) -> dict:
    return {
        "id": notification.id,
        "type": notification.type,
        "title": notification.title,
        "resource": notification.resource,
        "resource_id": notification.resource_id,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat(),
    }


async def publish_notification(notification: Notification) -> None:
    payload = notification_payload(notification)
    await get_redis().publish(f"notifications:{notification.user_id}", json.dumps(payload))
