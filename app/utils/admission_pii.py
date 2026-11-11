"""Encryption helpers for sensitive admission data."""

import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from app.core.config import get_settings
from app.core.exceptions import AppException


def _admission_fernet() -> Fernet:
    settings = get_settings()
    key = settings.admission_pii_encryption_key
    if key is not None:
        return Fernet(key.get_secret_value().encode())
    if not settings.jwt_secret_key:
        raise ValueError("JWT_SECRET_KEY is not configured")

    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"rps-school/admission-pii/v1",
    ).derive(settings.jwt_secret_key.encode())
    return Fernet(base64.urlsafe_b64encode(derived_key))


def encrypt_aadhaar(value: str) -> str:
    """Encrypt Aadhaar with the dedicated key or a domain-separated JWT-key derivation."""
    try:
        return _admission_fernet().encrypt(value.encode()).decode()
    except (OSError, ValueError) as exc:
        raise AppException(
            "Admission Aadhaar encryption is not configured.",
            code="ADMISSION_PII_NOT_CONFIGURED",
            status_code=503,
        ) from exc


def masked_aadhaar(last_four: str | None) -> str | None:
    """Format the separately stored last four digits for staff display."""
    return f"XXXX XXXX {last_four}" if last_four else None
