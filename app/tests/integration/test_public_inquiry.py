"""Integration tests for public student inquiry APIs."""

import pytest

INQUIRY_PAYLOAD = {
    "first_name": "Aarav",
    "middle_name": "Kumar",
    "last_name": "Sharma",
    "gender": "male",
    "father_name": "Rohit Sharma",
    "dob": "2018-04-10",
    "student_mobile": "+919999999999",
    "parent_mobile": "+911234567890",
    "email": "parent@example.com",
    "address": "123 School Road, City",
    "last_school": "ABC Public School",
    "current_class": "Grade 4",
    "admission_for_class": "Grade 5",
    "last_school_percentage": 85.5,
}


def test_public_create_inquiry(client):
    """POST /public/student/inquiry returns inquiry_code and PENDING status."""
    response = client.post("/api/v1/public/student/inquiry", json=INQUIRY_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["inquiry_code"].startswith("INQ")
    assert data["status"] == "PENDING"


def test_public_status_check(client):
    """GET status by inquiry_code returns timeline after create."""
    create_resp = client.post("/api/v1/public/student/inquiry", json=INQUIRY_PAYLOAD)
    inquiry_code = create_resp.json()["data"]["inquiry_code"]

    status_resp = client.get(f"/api/v1/public/student/inquiry/status/{inquiry_code}")
    assert status_resp.status_code == 200
    status_body = status_resp.json()["data"]
    assert status_body["inquiry_code"] == inquiry_code
    assert status_body["status"] == "PENDING"
    assert len(status_body["status_timeline"]) >= 1
    assert status_body["status_timeline"][0]["to_status"] == "PENDING"


def test_public_update_requires_credentials(client):
    """PUT update fails without matching verification fields."""
    create_resp = client.post("/api/v1/public/student/inquiry", json=INQUIRY_PAYLOAD)
    inquiry_code = create_resp.json()["data"]["inquiry_code"]

    bad_update = {
        "inquiry_code": inquiry_code,
        "email": "wrong@example.com",
        "parent_mobile": "+911234567890",
        "first_name": "Updated",
    }
    response = client.put("/api/v1/public/student/inquiry/update", json=bad_update)
    assert response.status_code == 401


def test_public_update_success(client):
    """PUT update succeeds when inquiry_code, email, and parent_mobile match."""
    create_resp = client.post("/api/v1/public/student/inquiry", json=INQUIRY_PAYLOAD)
    inquiry_code = create_resp.json()["data"]["inquiry_code"]
    update_payload = {
        "inquiry_code": inquiry_code,
        "email": INQUIRY_PAYLOAD["email"],
        "parent_mobile": INQUIRY_PAYLOAD["parent_mobile"],
        "first_name": "AaravUpdated",
    }
    response = client.put("/api/v1/public/student/inquiry/update", json=update_payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    # Name is not in public status response; verify via staff-less re-fetch
    status_resp = client.get(f"/api/v1/public/student/inquiry/status/{inquiry_code}")
    assert status_resp.status_code == 200
