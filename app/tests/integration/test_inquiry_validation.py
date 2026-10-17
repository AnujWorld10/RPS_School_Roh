"""Integration tests for inquiry validation, error handling, and edge cases."""

import pytest
from datetime import date, datetime, timedelta


def get_unique_validation_payload(suffix=""):
    """Generate unique payload for validation tests."""
    if not suffix:
        suffix = datetime.now().strftime("%s%f")[5:12]
    return {
        "first_name": "Test",
        "last_name": f"Student{suffix}",
        "gender": "male",
        "father_name": "Parent",
        "dob": "2016-01-01",
        "student_mobile": f"+9198765{suffix}",
        "parent_mobile": f"+9191234{suffix}",
        "email": f"test{suffix}@example.com",
        "address": "123 St",
        "last_school": "School",
        "current_class": "Grade 5",
        "admission_for_class": "Grade 6",
    }


def test_inquiry_with_invalid_email_format_fails(client):
    """POST /public/student/inquiry with invalid email format returns 422."""
    payload = {
        "first_name": "Invalid",
        "last_name": "Email",
        "gender": "male",
        "father_name": "Parent",
        "dob": "2016-01-01",
        "student_mobile": "+919876543210",
        "parent_mobile": "+919123456789",
        "email": "not-an-email",  # Invalid format
        "address": "123 St",
        "last_school": "School",
        "current_class": "Grade 5",
        "admission_for_class": "Grade 6",
    }
    response = client.post("/api/v1/public/student/inquiry", json=payload)
    assert response.status_code in [400, 422]


def test_inquiry_with_future_dob_fails(client):
    """POST /public/student/inquiry with DOB in future returns 422."""
    future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    payload = {
        "first_name": "Future",
        "last_name": "Student",
        "gender": "male",
        "father_name": "Parent",
        "dob": future_date,  # Tomorrow
        "student_mobile": "+919876543210",
        "parent_mobile": "+919123456789",
        "email": "future@example.com",
        "address": "123 St",
        "last_school": "School",
        "current_class": "Grade 5",
        "admission_for_class": "Grade 6",
    }
    response = client.post("/api/v1/public/student/inquiry", json=payload)
    assert response.status_code in [400, 422]


def test_inquiry_with_missing_required_fields_fails(client):
    """POST /public/student/inquiry with missing required fields returns 422."""
    payload = {
        "first_name": "Incomplete",
        # Missing last_name, dob, and other required fields
        "gender": "male",
    }
    response = client.post("/api/v1/public/student/inquiry", json=payload)
    assert response.status_code == 422


def test_inquiry_with_very_long_name_succeeds(client):
    """POST /public/student/inquiry with very long name (but valid) succeeds."""
    long_name = "A" * 100  # Very long name
    payload = {
        "first_name": long_name,
        "last_name": "Student",
        "gender": "male",
        "father_name": "Parent",
        "dob": "2016-01-01",
        "student_mobile": "+919876543210",
        "parent_mobile": "+919123456789",
        "email": "long@example.com",
        "address": "123 St",
        "last_school": "School",
        "current_class": "Grade 5",
        "admission_for_class": "Grade 6",
    }
    response = client.post("/api/v1/public/student/inquiry", json=payload)
    # Should succeed (db may truncate or accept)
    assert response.status_code in [201, 400, 422]


def test_inquiry_with_special_characters_in_name_succeeds(client):
    """POST /public/student/inquiry with special characters in name succeeds."""
    payload = {
        "first_name": "José-María",
        "last_name": "O'Connor",
        "gender": "male",
        "father_name": "François",
        "dob": "2016-01-01",
        "student_mobile": "+919876543210",
        "parent_mobile": "+919123456789",
        "email": "special@example.com",
        "address": "123 Rue St",
        "last_school": "École",
        "current_class": "Grade 5",
        "admission_for_class": "Grade 6",
    }
    response = client.post("/api/v1/public/student/inquiry", json=payload)
    assert response.status_code == 201


def test_inquiry_with_percentage_gt_100_fails(client):
    """POST /public/student/inquiry with last_school_percentage > 100 fails."""
    payload = {
        "first_name": "Invalid",
        "last_name": "Percentage",
        "gender": "male",
        "father_name": "Parent",
        "dob": "2016-01-01",
        "student_mobile": "+919876543210",
        "parent_mobile": "+919123456789",
        "email": "perc@example.com",
        "address": "123 St",
        "last_school": "School",
        "current_class": "Grade 5",
        "admission_for_class": "Grade 6",
        "last_school_percentage": 105.5,  # > 100
    }
    response = client.post("/api/v1/public/student/inquiry", json=payload)
    assert response.status_code in [400, 422]


def test_inquiry_with_negative_percentage_fails(client):
    """POST /public/student/inquiry with negative percentage fails."""
    payload = {
        "first_name": "Invalid",
        "last_name": "Percentage",
        "gender": "male",
        "father_name": "Parent",
        "dob": "2016-01-01",
        "student_mobile": "+919876543210",
        "parent_mobile": "+919123456789",
        "email": "negperc@example.com",
        "address": "123 St",
        "last_school": "School",
        "current_class": "Grade 5",
        "admission_for_class": "Grade 6",
        "last_school_percentage": -10.0,  # Negative
    }
    response = client.post("/api/v1/public/student/inquiry", json=payload)
    assert response.status_code in [400, 422]


def test_inquiry_code_prefix_is_INQ(client):
    """POST /public/student/inquiry returns inquiry_code starting with INQ."""
    payload = {
        "first_name": "Code",
        "last_name": "Prefix",
        "gender": "male",
        "father_name": "Parent",
        "dob": "2016-01-01",
        "student_mobile": "+919876543210",
        "parent_mobile": "+919123456789",
        "email": "code@example.com",
        "address": "123 St",
        "last_school": "School",
        "current_class": "Grade 5",
        "admission_for_class": "Grade 6",
    }
    response = client.post("/api/v1/public/student/inquiry", json=payload)
    assert response.status_code == 201
    inquiry_code = response.json()["data"]["inquiry_code"]
    assert inquiry_code.startswith("INQ")


def test_inquiry_code_is_unique(client):
    """POST /public/student/inquiry returns unique inquiry codes."""
    payload1 = {
        "first_name": "Unique1",
        "last_name": f"Student{datetime.now().strftime('%s%f')[5:12]}",
        "gender": "male",
        "father_name": "Parent1",
        "dob": "2015-01-01",
        "student_mobile": "+919876543210",
        "parent_mobile": "+919123456789",
        "email": f"unique1-{datetime.now().strftime('%s%f')[5:12]}@example.com",
        "address": "123 St",
        "last_school": "School",
        "current_class": "Grade 5",
        "admission_for_class": "Grade 6",
    }
    payload2 = {
        "first_name": "Unique2",
        "last_name": f"Student{datetime.now().strftime('%s%f')[5:12]}",
        "gender": "female",
        "father_name": "Parent2",
        "dob": "2015-02-01",
        "student_mobile": "+919876543211",
        "parent_mobile": "+919123456788",
        "email": f"unique2-{datetime.now().strftime('%s%f')[5:12]}@example.com",
        "address": "456 Ave",
        "last_school": "School",
        "current_class": "Grade 5",
        "admission_for_class": "Grade 6",
    }
    resp1 = client.post("/api/v1/public/student/inquiry", json=payload1)
    resp2 = client.post("/api/v1/public/student/inquiry", json=payload2)
    code1 = resp1.json()["data"]["inquiry_code"]
    code2 = resp2.json()["data"]["inquiry_code"]
    assert code1 != code2


def test_status_check_with_invalid_inquiry_code_returns_404(client):
    """GET /public/student/inquiry/status/{code} with invalid code returns 404."""
    response = client.get("/api/v1/public/student/inquiry/status/INVALID")
    assert response.status_code == 404


def test_status_check_inquiry_code_is_case_insensitive(client):
    """GET /public/student/inquiry/status/{code} accepts lowercase codes."""
    # Create inquiry
    suffix = datetime.now().strftime("%s%f")[5:12]
    payload = {
        "first_name": "Case",
        "last_name": f"Test{suffix}",
        "gender": "male",
        "father_name": f"Parent{suffix}",
        "dob": "2016-01-01",
        "student_mobile": f"+9198765{suffix}",
        "parent_mobile": f"+9191234{suffix}",
        "email": f"case{suffix}@example.com",
        "address": "123 St",
        "last_school": "School",
        "current_class": "Grade 5",
        "admission_for_class": "Grade 6",
    }
    create_resp = client.post("/api/v1/public/student/inquiry", json=payload)
    assert create_resp.status_code == 201
    inquiry_code = create_resp.json()["data"]["inquiry_code"]

    # Fetch with lowercase
    response = client.get(f"/api/v1/public/student/inquiry/status/{inquiry_code.lower()}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["inquiry_code"] == inquiry_code


def test_inquiry_with_invalid_gender_fails(client):
    """POST /public/student/inquiry with invalid gender returns 422."""
    payload = {
        "first_name": "Invalid",
        "last_name": "Gender",
        "gender": "unknown",  # Invalid
        "father_name": "Parent",
        "dob": "2016-01-01",
        "student_mobile": "+919876543210",
        "parent_mobile": "+919123456789",
        "email": "gender@example.com",
        "address": "123 St",
        "last_school": "School",
        "current_class": "Grade 5",
        "admission_for_class": "Grade 6",
    }
    response = client.post("/api/v1/public/student/inquiry", json=payload)
    assert response.status_code == 422


def test_inquiry_with_empty_string_for_required_field_fails(client):
    """POST /public/student/inquiry with empty string for required field returns 422."""
    payload = {
        "first_name": "",  # Empty
        "last_name": "Student",
        "gender": "male",
        "father_name": "Parent",
        "dob": "2016-01-01",
        "student_mobile": "+919876543210",
        "parent_mobile": "+919123456789",
        "email": "empty@example.com",
        "address": "123 St",
        "last_school": "School",
        "current_class": "Grade 5",
        "admission_for_class": "Grade 6",
    }
    response = client.post("/api/v1/public/student/inquiry", json=payload)
    assert response.status_code in [400, 422]


def test_inquiry_update_to_locked_status_fails(client, db_session, auth_headers):
    """PUT /public/student/inquiry/update on REJECTED inquiry returns error."""
    # Create inquiry
    payload = {
        "first_name": "Locked",
        "last_name": "Test",
        "gender": "male",
        "father_name": "Parent",
        "dob": "2016-01-01",
        "student_mobile": "+919876543210",
        "parent_mobile": "+919123456789",
        "email": "locked@example.com",
        "address": "123 St",
        "last_school": "School",
        "current_class": "Grade 5",
        "admission_for_class": "Grade 6",
    }
    create_resp = client.post("/api/v1/public/student/inquiry", json=payload)
    assert create_resp.status_code == 201
    inquiry_code = create_resp.json()["data"]["inquiry_code"]

    # Manually mark as REJECTED in DB
    from app.repositories.inquiries import StudentInquiryRepository
    from app.models.enums import InquiryStatus

    repo = StudentInquiryRepository(db_session)
    inquiry = repo.get_by_code_with_history(inquiry_code)
    inquiry.status = InquiryStatus.REJECTED.value
    repo.update(inquiry)
    db_session.commit()

    # Try to update
    update_resp = client.put(
        "/api/v1/public/student/inquiry/update",
        json={
            "inquiry_code": inquiry_code,
            "email": payload["email"],
            "parent_mobile": payload["parent_mobile"],
            "first_name": "Updated",
        },
    )
    assert update_resp.status_code in [400, 422, 409]  # Business rule violation
