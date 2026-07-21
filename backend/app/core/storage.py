"""Abstraction de stockage des fichiers (ADR-0006).

Implémentation locale pour le MVP ; la signature des fonctions ne présuppose
pas le disque local, la bascule vers MinIO/S3 remplacera ce module sans
changer les appelants.
"""

import re
import uuid
from pathlib import Path

from app.core.config import settings


_SAFE_RELATIVE_PATH = re.compile(r"^[a-z_]+/[a-f0-9]{32}\.[a-z0-9]{2,5}$")


def _root() -> Path:
    root = Path(settings.storage_local_path)
    root.mkdir(parents=True, exist_ok=True)
    return root


def save_bytes(data: bytes, subdir: str, extension: str) -> str:
    """Écrit le contenu sous un nom opaque et retourne le chemin relatif."""
    filename = f"{uuid.uuid4().hex}.{extension.lower().lstrip('.')}"
    directory = _root() / subdir
    directory.mkdir(parents=True, exist_ok=True)
    (directory / filename).write_bytes(data)
    return f"{subdir}/{filename}"


def is_safe_path(relative_path: str) -> bool:
    """Un chemin est acceptable seulement s'il a la forme produite par save_bytes
    (empêche toute traversée de répertoire via une valeur fournie par le client)."""
    return bool(_SAFE_RELATIVE_PATH.match(relative_path))


def full_path(relative_path: str) -> Path | None:
    if not is_safe_path(relative_path):
        return None
    path = _root() / relative_path
    return path if path.is_file() else None


def delete_file(relative_path: str) -> None:
    path = full_path(relative_path)
    if path is not None:
        path.unlink(missing_ok=True)
