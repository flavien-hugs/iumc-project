from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "iumc",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.modules.requests.tasks", "app.modules.users.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Abidjan",
    enable_utc=True,
    # En dev, exécution synchrone dans le processus API (pas de worker requis) ;
    # en production, le worker dédié du compose prend le relais.
    task_always_eager=settings.environment == "development",
)
