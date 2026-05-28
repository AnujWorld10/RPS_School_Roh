"""
Local file storage helpers for admission document uploads.
"""

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import get_settings
from app.core.exceptions import ValidationException


def save_upload_file(upload: UploadFile, subdirectory: str) -> tuple[str, str]:
    """
    Persist an uploaded file under the configured upload directory.

    Args:
        upload: FastAPI upload instance.
        subdirectory: Folder segment e.g. ``admissions/12``.

    Returns:
        Tuple of (relative_path, original_filename).

    Raises:
        ValidationException: If extension or size is not allowed.
    """
    settings = get_settings()
    if not upload.filename:
        raise ValidationException("File name is required", field="file")

    suffix = Path(upload.filename).suffix.lower()
    if suffix not in settings.allowed_extensions:
        raise ValidationException(
            f"File type not allowed. Allowed: {settings.allowed_upload_extensions}",
            field="file",
        )

    content = upload.file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise ValidationException(
            f"File exceeds maximum size of {settings.max_upload_size_mb} MB",
            field="file",
        )

    target_dir = settings.upload_path / subdirectory
    target_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    target_path = target_dir / stored_name
    target_path.write_bytes(content)

    relative = str(target_path.relative_to(settings.upload_path)).replace("\\", "/")
    return relative, upload.filename
