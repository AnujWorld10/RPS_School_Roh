from datetime import date

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from starlette.requests import Request

from app.core.config import Settings
from app.core.exceptions import TokenInvalidException
from app.core.security import hash_password
from app.models.enums import UserStatus
from app.models.role import Role
from app.models.student import Student
from app.models.student_inquiry import StudentInquiry
from app.models.user import User
from app.services.auth import AuthService


def _request() -> Request:
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/api/v1/auth/test",
            "raw_path": b"/api/v1/auth/test",
            "query_string": b"",
            "headers": [],
            "client": ("testclient", 1234),
            "server": ("testserver", 80),
            "state": {},
        }
    )


def _create_user(db_session, email: str, role_code: str, phone: str | None = None) -> User:
    role = db_session.scalar(select(Role).where(Role.code == role_code))
    assert role is not None
    user = User(
        first_name="Access",
        last_name="Test",
        email=email,
        phone=phone,
        password_hash=hash_password("ValidPassword@123"),
        status=UserStatus.ACTIVE.value,
    )
    user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _create_inquiry(
    db_session,
    inquiry_code: str,
    serial_number: int,
    email: str,
    parent_mobile: str,
) -> StudentInquiry:
    inquiry = StudentInquiry(
        inquiry_code=inquiry_code,
        serial_number=serial_number,
        first_name="Child",
        last_name="Test",
        gender="female",
        father_name="Parent Test",
        date_of_birth=date(2015, 1, 1),
        parent_mobile=parent_mobile,
        email=email,
        address="1 School Road",
        last_school="Previous School",
        current_class="Grade 4",
        admission_for_class="Grade 5",
        status="PENDING",
    )
    db_session.add(inquiry)
    db_session.flush()
    return inquiry


def _create_student(
    db_session,
    student_code: str,
    email: str,
    phone: str | None,
    inquiry_id: int | None = None,
) -> Student:
    student = Student(
        student_code=student_code,
        inquiry_id=inquiry_id,
        first_name="Child",
        last_name=student_code,
        date_of_birth=date(2015, 1, 1),
        gender="female",
        email=email,
        phone=phone,
        status="active",
    )
    db_session.add(student)
    db_session.flush()
    return student


def _login(client, user: User) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "ValidPassword@123"},
    )
    assert response.status_code == 200
    return response.json()["data"]


@pytest.mark.parametrize("role_code", ["ADMIN", "SUPER_ADMIN"])
def test_admin_cannot_assign_equal_or_higher_role(client, db_session, role_code):
    admin = _create_user(db_session, "phase1-admin@example.com", "ADMIN")
    tokens = _login(client, admin)

    response = client.post(
        "/api/v1/auth/register",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={
            "first_name": "Escalation",
            "last_name": "Attempt",
            "email": f"phase1-escalation-{role_code.lower()}@example.com",
            "password": "ValidPassword@123",
            "role_codes": [role_code],
        },
    )

    assert response.status_code == 403


def test_admin_can_assign_a_lower_authority_role(client, db_session):
    admin = _create_user(db_session, "phase1-lower-role@example.com", "ADMIN")
    tokens = _login(client, admin)

    response = client.post(
        "/api/v1/auth/register",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={
            "first_name": "Teacher",
            "last_name": "Account",
            "email": "phase1-teacher@example.com",
            "password": "ValidPassword@123",
            "role_codes": ["TEACHER"],
        },
    )

    assert response.status_code == 201
    assert response.json()["data"]["roles"] == ["TEACHER"]


def test_super_admin_can_assign_an_admin_role(client, auth_headers):
    response = client.post(
        "/api/v1/auth/register",
        headers=auth_headers,
        json={
            "first_name": "New",
            "last_name": "Administrator",
            "email": "phase1-new-admin@example.com",
            "password": "ValidPassword@123",
            "role_codes": ["ADMIN"],
        },
    )

    assert response.status_code == 201
    assert response.json()["data"]["roles"] == ["ADMIN"]


def test_logout_cannot_revoke_another_users_refresh_token(client, db_session):
    first_user = _create_user(db_session, "phase1-first@example.com", "ADMIN")
    second_user = _create_user(db_session, "phase1-second@example.com", "ADMIN")
    first_tokens = _login(client, first_user)
    second_tokens = _login(client, second_user)

    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {second_tokens['access_token']}"},
        json={"refresh_token": first_tokens["refresh_token"]},
    )

    assert response.status_code == 401
    still_valid = client.post(
        "/api/v1/auth/refresh-token",
        json={"refresh_token": first_tokens["refresh_token"]},
    )
    assert still_valid.status_code == 200


def test_student_can_list_and_read_only_owned_students(client, db_session):
    student_user = _create_user(
        db_session,
        "phase1-student@example.com",
        "STUDENT",
        "+15550000001",
    )
    owned = _create_student(
        db_session,
        "STU-PHASE1-OWNED",
        student_user.email,
        student_user.phone,
    )
    other = _create_student(
        db_session,
        "STU-PHASE1-OTHER",
        "unrelated@example.com",
        "+15550000002",
    )
    db_session.commit()
    tokens = _login(client, student_user)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    listing = client.get("/api/v1/students", headers=headers)
    assert listing.status_code == 200
    assert [item["id"] for item in listing.json()["data"]] == [owned.id]

    own_detail = client.get(f"/api/v1/students/{owned.id}", headers=headers)
    other_detail = client.get(
        f"/api/v1/students/{other.id}",
        headers=headers,
    )
    assert own_detail.status_code == 200
    assert other_detail.status_code == 404


def test_parent_can_list_only_students_linked_to_matching_parent_contacts(
    client,
    db_session,
):
    parent_email = "phase1-parent@example.com"
    parent_phone = "+15550000003"
    parent = _create_user(db_session, parent_email, "PARENT", parent_phone)
    inquiry = _create_inquiry(db_session, "INQ-PHASE1-OWN", 93001, parent_email, parent_phone)
    child = _create_student(
        db_session,
        "STU-PHASE1-CHILD",
        "child@example.com",
        "+15550000004",
        inquiry.id,
    )
    _create_student(
        db_session,
        "STU-PHASE1-NOT-CHILD",
        "another-child@example.com",
        "+15550000005",
    )
    db_session.commit()
    tokens = _login(client, parent)

    listing = client.get(
        "/api/v1/students",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert listing.status_code == 200
    assert [item["id"] for item in listing.json()["data"]] == [child.id]


def test_parent_without_phone_has_no_student_access(client, db_session):
    parent = _create_user(db_session, "phase1-parent-no-phone@example.com", "PARENT")
    student = _create_student(
        db_session,
        "STU-PHASE1-NO-PHONE",
        parent.email,
        "+15550000006",
    )
    db_session.commit()
    tokens = _login(client, parent)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    listing = client.get("/api/v1/students", headers=headers)
    detail = client.get(f"/api/v1/students/{student.id}", headers=headers)

    assert listing.status_code == 200
    assert listing.json()["data"] == []
    assert detail.status_code == 404


def test_logout_rejects_unknown_and_already_revoked_refresh_tokens(db_session):
    user = _create_user(db_session, "phase1-logout@example.com", "ADMIN")
    service = AuthService(db_session)

    with pytest.raises(TokenInvalidException):
        service.logout("not-a-stored-token", user.id, _request())


@pytest.mark.parametrize(
    ("debug", "secret"),
    [
        (True, "a-random-production-key-that-is-long-enough-123456"),
        (False, "change-me-in-production-use-long-random-string"),
        (False, "short-secret"),
    ],
)
def test_production_settings_reject_debug_or_placeholder_jwt(debug, secret):
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            app_env="production",
            debug=debug,
            database_url="mysql+pymysql://user:pass@localhost/school",
            jwt_secret_key=secret,
        )


def test_production_settings_accept_strong_unique_jwt_secret():
    settings = Settings(
        _env_file=None,
        app_env="production",
        debug=False,
        database_url="mysql+pymysql://user:pass@localhost/school",
        jwt_secret_key="a-random-production-key-that-is-long-enough-123456",
    )

    assert settings.app_env == "production"
    assert settings.debug is False
