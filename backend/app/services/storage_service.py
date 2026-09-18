"""
Storage Service.

Handles saving uploaded files to a temporary working directory and
deleting them once processing completes, per AUTO_DELETE_UPLOADS.
The application does not require or implement any persistent storage
of raw identity document images — only derived metadata (extracted
fields, scores, explanations) is kept in the database.
"""
from __future__ import annotations

import logging
import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}


def ensure_upload_dir() -> Path:
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return settings.UPLOAD_DIR


def validate_extension(filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
        )


def save_upload(file: UploadFile) -> Path:
    validate_extension(file.filename or "")
    upload_dir = ensure_upload_dir()
    unique_name = f"{uuid.uuid4().hex}_{Path(file.filename).name}"
    dest = upload_dir / unique_name

    with dest.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    size_mb = dest.stat().st_size / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_MB:
        dest.unlink(missing_ok=True)
        raise ValueError(f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_MB} MB.")

    return dest


def save_demo_file(source_path: Path) -> Path:
    """
    Copy a bundled demo file into a unique working subdirectory, preserving
    its original filename exactly. Demo scenarios are matched by exact
    filename (see services/demo_data.py, ocr_service.py, tampering_service.py),
    so a UUID *prefix* on the filename itself would break that lookup;
    using a UUID subdirectory instead keeps filenames stable while still
    avoiding collisions between concurrent demo runs.
    """
    upload_dir = ensure_upload_dir()
    unique_subdir = upload_dir / uuid.uuid4().hex
    unique_subdir.mkdir(parents=True, exist_ok=True)
    dest = unique_subdir / source_path.name
    shutil.copy(source_path, dest)
    return dest


def delete_file(path: Path | str) -> bool:
    """Delete a file (and its unique parent subdirectory, if empty) when
    AUTO_DELETE_UPLOADS is enabled. Returns True if the file was deleted."""
    if not settings.AUTO_DELETE_UPLOADS:
        return False
    try:
        p = Path(path)
        p.unlink(missing_ok=True)
        parent = p.parent
        if parent != settings.UPLOAD_DIR and parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to delete temp upload %s: %s", path, exc)
        return False
