from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select

from app.core.config import get_settings
from app.core.db import DbSession
from app.core.pagination import Page, PageParams, paginate
from app.core.storage import delete_file, full_path, save_bytes
from app.models import MediaFile, UserRole
from app.modules.audit.service import log_action
from app.modules.auth.deps import CurrentUser, require_roles

settings = get_settings()

# Formats autorisés dans la médiathèque (CDC section 8.11).
ALLOWED_MEDIA_EXTENSIONS = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
    "svg": "image/svg+xml",
    "pdf": "application/pdf",
}

admin_router = APIRouter(
    prefix="/admin/media",
    tags=["admin"],
    dependencies=[Depends(require_roles(UserRole.super_admin, UserRole.content_admin))],
)

# Service public des fichiers de la médiathèque (images du site).
public_router = APIRouter(tags=["media"])


class MediaRow(BaseModel):
    id: int
    name: str
    path: str
    mime_type: str
    size: int
    created_at: datetime


def _to_row(media: MediaFile) -> MediaRow:
    return MediaRow(
        id=media.id,
        name=media.name,
        path=media.path,
        mime_type=media.mime_type,
        size=media.size,
        created_at=media.created_at,
    )


@admin_router.get("", response_model=Page[MediaRow])
async def list_media(db: DbSession, params: PageParams = Depends()) -> Page[MediaRow]:
    query = select(MediaFile).order_by(MediaFile.created_at.desc())
    rows, total = await paginate(db, query, params)
    return Page(
        items=[_to_row(row[0]) for row in rows],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


@admin_router.post("", response_model=MediaRow, status_code=status.HTTP_201_CREATED)
async def upload_media(file: UploadFile, db: DbSession, user: CurrentUser) -> MediaRow:
    extension = Path(file.filename or "").suffix.lstrip(".").lower()
    if extension not in ALLOWED_MEDIA_EXTENSIONS:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Format non autorisé (JPG, PNG, WebP, SVG ou PDF)",
        )
    data = await file.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Fichier trop volumineux (maximum {settings.max_upload_mb} Mo)",
        )
    relative_path = save_bytes(data, "media", extension)
    media = MediaFile(
        name=file.filename or relative_path,
        path=relative_path,
        mime_type=ALLOWED_MEDIA_EXTENSIONS[extension],
        size=len(data),
        uploaded_by=user.id,
    )
    db.add(media)
    await db.flush()
    log_action(db, user.id, "create", resource="media_file", resource_id=media.id)
    await db.commit()
    return _to_row(media)


@admin_router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(media_id: int, db: DbSession, user: CurrentUser) -> None:
    media = await db.get(MediaFile, media_id)
    if media is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fichier introuvable")
    delete_file(media.path)
    await db.delete(media)
    log_action(db, user.id, "delete", resource="media_file", resource_id=media_id)
    await db.commit()


@public_router.get("/media/{media_id}/file")
async def serve_media(media_id: int, db: DbSession) -> FileResponse:
    media = await db.get(MediaFile, media_id)
    if media is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fichier introuvable")
    path = full_path(media.path)
    if path is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fichier introuvable")
    return FileResponse(path, media_type=media.mime_type, filename=media.name)
