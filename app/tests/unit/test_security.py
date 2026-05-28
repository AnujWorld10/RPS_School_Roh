from app.core.security import hash_password, verify_password, validate_password_strength
from app.core.exceptions import ValidationException
import pytest


def test_password_hash_and_verify():
    hashed = hash_password("StrongPassword@123")
    assert verify_password("StrongPassword@123", hashed)
    assert not verify_password("WrongPassword@123", hashed)


def test_password_strength_validation():
    with pytest.raises(ValidationException):
        validate_password_strength("weak")
