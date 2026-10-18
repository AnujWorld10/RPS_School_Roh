INQUIRY_PAYLOAD = {
    "first_name": "Phase",
    "last_name": "Four",
    "gender": "female",
    "father_name": "Parent Phase",
    "dob": "2016-01-01",
    "parent_mobile": "+919876543210",
    "email": "phase4@example.com",
    "address": "123 School Road",
    "last_school": "Previous School",
    "current_class": "Grade 4",
    "admission_for_class": "Grade 5",
}


def test_public_admission_form_validation_uses_standard_422_envelope(client):
    inquiry_response = client.post(
        "/api/v1/public/student/inquiry",
        json=INQUIRY_PAYLOAD,
    )
    assert inquiry_response.status_code == 201

    response = client.post(
        "/api/v1/public/student/admission",
        data={
            "inquiry_code": inquiry_response.json()["data"]["inquiry_code"],
            "email": INQUIRY_PAYLOAD["email"],
            "parent_mobile": INQUIRY_PAYLOAD["parent_mobile"],
            "class_id": "0",
            "academic_year": "2026-2027",
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation failed"
    assert body["errors"]
    assert body["errors"][0]["code"] == "VALIDATION_ERROR"


def test_public_admission_form_rejects_invalid_email_with_422(client):
    inquiry_response = client.post(
        "/api/v1/public/student/inquiry",
        json=INQUIRY_PAYLOAD,
    )
    assert inquiry_response.status_code == 201

    response = client.post(
        "/api/v1/public/student/admission",
        data={
            "inquiry_code": inquiry_response.json()["data"]["inquiry_code"],
            "email": "not-an-email",
            "parent_mobile": INQUIRY_PAYLOAD["parent_mobile"],
            "class_id": "2",
            "academic_year": "2026-2027",
        },
    )

    assert response.status_code == 422
    assert response.json()["success"] is False
    assert response.json()["errors"][0]["code"] == "VALIDATION_ERROR"


def test_public_admission_schema_validation_returns_422_envelope(client):
    inquiry_response = client.post(
        "/api/v1/public/student/inquiry",
        json=INQUIRY_PAYLOAD,
    )
    assert inquiry_response.status_code == 201

    response = client.post(
        "/api/v1/public/student/admission",
        data={
            "inquiry_code": inquiry_response.json()["data"]["inquiry_code"],
            "email": INQUIRY_PAYLOAD["email"],
            "parent_mobile": INQUIRY_PAYLOAD["parent_mobile"],
            "class_id": "2",
            "academic_year": "    ",
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation failed"
    assert any("academic_year" in error["field"] for error in body["errors"])
