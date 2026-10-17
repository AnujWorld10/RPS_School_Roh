from io import BytesIO
from types import SimpleNamespace

import pytest
from fastapi import UploadFile

from app.core.exceptions import ValidationException
from app.utils import file_storage


def test_oversized_upload_is_rejected_after_bounded_read(monkeypatch, tmp_path):
    max_bytes = 1024 * 1024
    upload = UploadFile(filename="document.pdf", file=BytesIO(b"x" * (max_bytes + 10)))
    settings = SimpleNamespace(
        allowed_extensions={".pdf"},
        allowed_upload_extensions="pdf",
        max_upload_size_mb=1,
        upload_path=tmp_path,
    )
    monkeypatch.setattr(file_storage, "get_settings", lambda: settings)

    with pytest.raises(ValidationException):
        file_storage.save_upload_file(upload, "admissions/1")

    assert upload.file.tell() == max_bytes + 1
