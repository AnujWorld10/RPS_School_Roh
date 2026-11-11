from decimal import Decimal
from unittest.mock import MagicMock

from app.core.security import hash_password
from app.models.enums import UserStatus
from app.models.role import Role
from app.models.user import User
from app.schemas.classes import ClassCreateRequest
from app.services.classes import ClassService


def _request():
    request = MagicMock()
    request.state.request_id = "fee-structure-test"
    request.client = None
    request.headers = {}
    return request


def _create_class(db_session, name="Grade 5", year="2026-2027"):
    return ClassService(db_session).create_class(
        ClassCreateRequest(name=name, section="A", academic_year=year, capacity=30),
        1,
        _request(),
    )


def _admission_payload(class_id, year="2026-2027"):
    return {
        "academic_year": year,
        "class_id": class_id,
        "structure_name": "Admission 2026",
        "components": [
            {"fee_name": "Registration", "amount": "100.00"},
            {"fee_name": "Uniform", "amount": "20.00", "is_optional": True},
        ],
    }


def test_admission_fee_structure_crud_and_totals(client, db_session, auth_headers):
    school_class = _create_class(db_session)
    created = client.post(
        "/api/v1/fees/admission-structures",
        json=_admission_payload(school_class.id),
        headers=auth_headers,
    )
    assert created.status_code == 201
    structure = created.json()["data"]
    assert structure["school_class"]["id"] == school_class.id
    assert Decimal(str(structure["mandatory_total"])) == Decimal("100.00")
    assert Decimal(str(structure["optional_total"])) == Decimal("20.00")
    assert Decimal(str(structure["total_amount"])) == Decimal("120.00")

    component_id = structure["components"][0]["id"]
    updated = client.put(
        f"/api/v1/fees/admission-structures/{structure['id']}",
        json={
            "structure_name": "Updated admission",
            "components": [
                {"id": component_id, "amount": "125.00"},
                {"fee_name": "Books", "amount": "80.00"},
            ],
        },
        headers=auth_headers,
    )
    assert updated.status_code == 200
    updated_structure = updated.json()["data"]
    assert updated_structure["structure_name"] == "Updated admission"
    assert len(updated_structure["components"]) == 3
    assert Decimal(str(updated_structure["mandatory_total"])) == Decimal("205.00")
    assert Decimal(str(updated_structure["optional_total"])) == Decimal("20.00")

    listed = client.get(
        f"/api/v1/fees/admission-structures?class_id={school_class.id}&academic_year=2026-2027",
        headers=auth_headers,
    )
    assert listed.status_code == 200
    assert listed.json()["pagination"]["total_records"] == 1
    assert listed.json()["data"][0]["id"] == structure["id"]

    next_class = _create_class(db_session, name="Grade 6")
    moved = client.put(
        f"/api/v1/fees/admission-structures/{structure['id']}",
        json={"class_id": next_class.id},
        headers=auth_headers,
    )
    assert moved.status_code == 200
    assert moved.json()["data"]["class_id"] == next_class.id
    assert moved.json()["data"]["school_class"]["id"] == next_class.id

    status_update = client.patch(
        f"/api/v1/fees/admission-structures/{structure['id']}/status",
        json={"is_active": False},
        headers=auth_headers,
    )
    assert status_update.status_code == 200
    assert status_update.json()["data"]["is_active"] is False

    deleted = client.delete(
        f"/api/v1/fees/admission-structures/{structure['id']}",
        headers=auth_headers,
    )
    assert deleted.status_code == 200
    assert deleted.json()["data"]["is_active"] is False
    fetched = client.get(
        f"/api/v1/fees/admission-structures/{structure['id']}",
        headers=auth_headers,
    )
    assert fetched.status_code == 200


def test_monthly_fee_structure_annualizes_each_billing_frequency(client, db_session, auth_headers):
    school_class = _create_class(db_session)
    response = client.post(
        "/api/v1/fees/monthly-structures",
        json={
            "academic_year": school_class.academic_year,
            "class_id": school_class.id,
            "structure_name": "Recurring charges",
            "components": [
                {
                    "fee_name": "Tuition",
                    "amount": "100.00",
                    "billing_frequency": "MONTHLY",
                },
                {
                    "fee_name": "Transport",
                    "amount": "300.00",
                    "billing_frequency": "QUARTERLY",
                },
                {
                    "fee_name": "Activity",
                    "amount": "500.00",
                    "billing_frequency": "ONE_TIME",
                    "is_optional": True,
                },
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    structure = response.json()["data"]
    assert Decimal(str(structure["mandatory_annual_total"])) == Decimal("2400.00")
    assert Decimal(str(structure["optional_annual_total"])) == Decimal("500.00")
    assert Decimal(str(structure["mandatory_monthly_equivalent"])) == Decimal("200.00")
    assert Decimal(str(structure["total_annual_amount"])) == Decimal("2900.00")

    listed = client.get(
        "/api/v1/fees/monthly-structures?is_active=true&page=1&limit=1",
        headers=auth_headers,
    )
    assert listed.status_code == 200
    assert listed.json()["pagination"]["limit"] == 1
    assert listed.json()["pagination"]["total_records"] == 1


def test_fee_structures_reject_invalid_classes_duplicates_and_component_updates(
    client,
    db_session,
    auth_headers,
):
    school_class = _create_class(db_session)
    mismatched_year = client.post(
        "/api/v1/fees/admission-structures",
        json=_admission_payload(school_class.id, year="2025-2026"),
        headers=auth_headers,
    )
    assert mismatched_year.status_code == 422

    missing_class = client.post(
        "/api/v1/fees/admission-structures",
        json=_admission_payload(999999),
        headers=auth_headers,
    )
    assert missing_class.status_code == 404

    created = client.post(
        "/api/v1/fees/admission-structures",
        json=_admission_payload(school_class.id),
        headers=auth_headers,
    )
    assert created.status_code == 201
    structure_id = created.json()["data"]["id"]

    duplicate = client.post(
        "/api/v1/fees/admission-structures",
        json=_admission_payload(school_class.id),
        headers=auth_headers,
    )
    assert duplicate.status_code == 409

    foreign_component = client.put(
        f"/api/v1/fees/admission-structures/{structure_id}",
        json={"components": [{"id": 999999, "amount": "10.00"}]},
        headers=auth_headers,
    )
    assert foreign_component.status_code == 404
    unchanged = client.get(
        f"/api/v1/fees/admission-structures/{structure_id}",
        headers=auth_headers,
    )
    assert unchanged.status_code == 200
    assert Decimal(str(unchanged.json()["data"]["components"][0]["amount"])) == Decimal("100.00")


def test_accountant_can_manage_fees_but_cannot_delete(client, db_session):
    role = db_session.query(Role).filter(Role.code == "ACCOUNTANT").one()
    user = User(
        first_name="Fee",
        last_name="Accountant",
        email="fee-accountant@example.test",
        password_hash=hash_password("ValidPassword@123"),
        status=UserStatus.ACTIVE.value,
    )
    user.roles.append(role)
    db_session.add(user)
    db_session.commit()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "ValidPassword@123"},
    )
    assert login.status_code == 200
    token = login.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    school_class = _create_class(db_session)
    created = client.post(
        "/api/v1/fees/admission-structures",
        json=_admission_payload(school_class.id),
        headers=headers,
    )
    assert created.status_code == 201

    deleted = client.delete(
        f"/api/v1/fees/admission-structures/{created.json()['data']['id']}",
        headers=headers,
    )
    assert deleted.status_code == 403
