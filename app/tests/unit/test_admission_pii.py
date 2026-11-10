import base64
from types import SimpleNamespace

import pytest
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from app.core.exceptions import AppException
from app.utils import admission_pii


def test_encrypt_aadhaar_uses_configured_dedicated_key(monkeypatch):
    key = Fernet.generate_key()
    monkeypatch.setattr(
        admission_pii,
        "get_settings",
        lambda: SimpleNamespace(
            admission_pii_encryption_key=SimpleNamespace(
                get_secret_value=lambda: key.decode(),
            ),
            jwt_secret_key="stable-jwt-application-secret",
        ),
    )

    encrypted = admission_pii.encrypt_aadhaar("012345678901")

    assert Fernet(key).decrypt(encrypted.encode()) == b"012345678901"


def test_encrypt_aadhaar_fails_closed_when_no_key_is_configured(monkeypatch):
    settings_without_key = SimpleNamespace(
        admission_pii_encryption_key=None,
        jwt_secret_key="",
    )
    monkeypatch.setattr(admission_pii, "get_settings", lambda: settings_without_key)

    with pytest.raises(AppException) as error:
        admission_pii.encrypt_aadhaar("012345678901")
    assert error.value.code == "ADMISSION_PII_NOT_CONFIGURED"


def test_encrypt_aadhaar_uses_stable_key_derived_from_jwt_secret(monkeypatch):
    settings_without_admission_key = SimpleNamespace(
        admission_pii_encryption_key=None,
        jwt_secret_key="stable-jwt-application-secret",
    )
    monkeypatch.setattr(
        admission_pii,
        "get_settings",
        lambda: settings_without_admission_key,
    )

    encrypted = admission_pii.encrypt_aadhaar("012345678901")
    encrypted_again = admission_pii.encrypt_aadhaar("012345678901")

    assert _decrypt_with_derived_key(encrypted, settings_without_admission_key.jwt_secret_key) == (
        b"012345678901"
    )
    assert _decrypt_with_derived_key(
        encrypted_again,
        settings_without_admission_key.jwt_secret_key,
    ) == b"012345678901"


def _decrypt_with_derived_key(ciphertext: str, secret: str) -> bytes:
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"rps-school/admission-pii/v1",
    ).derive(secret.encode())
    return Fernet(base64.urlsafe_b64encode(derived_key)).decrypt(ciphertext.encode())
