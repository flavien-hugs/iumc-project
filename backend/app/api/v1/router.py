from fastapi import APIRouter

from app.modules.audit.router import router as audit_router
from app.modules.auth.router import router as auth_router
from app.modules.contact.router import router as contact_router
from app.modules.contact.router_admin import router as contact_admin_router
from app.modules.content.router_admin import router as content_admin_router
from app.modules.content.router_public import router as content_public_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.locations.router_admin import router as locations_admin_router
from app.modules.locations.router_public import router as locations_public_router
from app.modules.media.router import admin_router as media_admin_router
from app.modules.media.router import public_router as media_public_router
from app.modules.notifications.router import router as notifications_router
from app.modules.requests.router_admin import router as requests_admin_router
from app.modules.requests.router_public import router as requests_public_router
from app.modules.settings.router import router as settings_router
from app.modules.settings.router_public import router as settings_public_router
from app.modules.users.router import router as users_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(dashboard_router)
router.include_router(requests_admin_router)
router.include_router(requests_public_router)
router.include_router(notifications_router)
router.include_router(users_router)
router.include_router(audit_router)
router.include_router(contact_admin_router)
router.include_router(content_admin_router)
router.include_router(content_public_router)
router.include_router(media_admin_router)
router.include_router(media_public_router)
router.include_router(settings_router)
router.include_router(settings_public_router)
router.include_router(locations_admin_router)
router.include_router(locations_public_router)
router.include_router(contact_router)


@router.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
