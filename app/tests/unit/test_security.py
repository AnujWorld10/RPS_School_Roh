from types import SimpleNamespace

import pytest

from app.core.exceptions import ValidationException
from app.core.permissions import ROLE_PERMISSION_MAP
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    validate_password_strength,
    verify_password,
)
from app.services.auth import _collect_roles_and_permissions


def test_password_hash_and_verify():
    hashed = hash_password("StrongPassword@123")
    assert verify_password("StrongPassword@123", hashed)
    assert not verify_password("WrongPassword@123", hashed)


def test_password_strength_validation():
    with pytest.raises(ValidationException):
        validate_password_strength("weak")


def test_access_token_is_compact_and_contains_required_claims():
    token = create_access_token(user_id=123456789)
    payload = decode_token(token)

    assert len(token) <= 200
    assert payload["sub"] == "123456789"
    assert payload["jti"]
    assert "exp" in payload
    assert "type" not in payload
    assert "email" not in payload
    assert "roles" not in payload
    assert "permissions" not in payload


def test_inactive_role_permissions_are_not_granted():
    inactive_role = SimpleNamespace(
        code="DISABLED_ROLE",
        is_active=False,
        permissions=[SimpleNamespace(code="students.delete")],
    )
    user = SimpleNamespace(roles=[inactive_role])

    assert _collect_roles_and_permissions(user) == ([], [])


def test_teacher_salary_permissions_are_limited_to_finance_and_admin_roles():
    assert "teachers.salary.read" not in ROLE_PERMISSION_MAP["TEACHER"]
    assert "teachers.salary.read" in ROLE_PERMISSION_MAP["ACCOUNTANT"]
    assert "teachers.salary.read" in ROLE_PERMISSION_MAP["ADMIN"]
