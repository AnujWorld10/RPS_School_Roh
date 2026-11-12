from datetime import date, datetime, timedelta
from decimal import Decimal

from app.core.config import get_settings
from app.models.admission import InquiryAdmission
from app.models.class_model import Class
from app.models.enums import (
    AdmissionStatus,
    ClassStatus,
    DocumentType,
    DocumentVerificationStatus,
    InquiryStatus,
    StudentStatus,
)
from app.models.student import Student
from app.models.student_inquiry import StudentInquiry


def test_student_lifecycle_from_public_inquiry_to_student_portal(
    client,
    db_session,
    auth_headers,
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(get_settings(), "upload_dir", str(tmp_path))

    requested_class = Class(
        name="Grade 6",
        section="A",
        academic_year="2026-2027",
        capacity=30,
        status=ClassStatus.ACTIVE.value,
    )
    enrollment_class = Class(
        name="Grade 6",
        section="B",
        academic_year="2025-2026",
        capacity=30,
        status=ClassStatus.ACTIVE.value,
    )
    db_session.add_all([requested_class, enrollment_class])
    db_session.commit()

    inquiry_payload = {
        "first_name": "Aanya",
        "middle_name": "Priya",
        "last_name": "Mehta",
        "gender": "female",
        "father_name": "Rohan Mehta",
        "dob": "2015-09-22",
        "student_mobile": "+919876543210",
        "parent_mobile": "+919876543211",
        "email": "aanya.mehta.lifecycle@example.com",
        "address": "24 Lake View Road, Roh",
        "last_school": "Green Valley Public School",
        "current_class": "Grade 5",
        "admission_for_class": "Grade 6",
        "last_school_percentage": 88.75,
    }
    created = client.post("/api/v1/public/student/inquiry", json=inquiry_payload)
    assert created.status_code == 201, created.text
    created_data = created.json()["data"]
    assert set(created_data) == {"inquiry_code", "status", "message"}
    assert isinstance(created_data["inquiry_code"], str)
    assert created_data["inquiry_code"].startswith("INQ")
    assert created_data["status"] == InquiryStatus.PENDING.value
    inquiry_code = created_data["inquiry_code"]

    parent_headers = {
        "X-Parent-Email": inquiry_payload["email"],
        "X-Parent-Mobile": inquiry_payload["parent_mobile"],
    }
    initial_status_response = client.get(
        f"/api/v1/public/student/inquiry/status/{inquiry_code}",
        headers=parent_headers,
    )
    assert initial_status_response.status_code == 200
    initial_status = initial_status_response.json()["data"]
    assert initial_status["student_name"] == "Aanya Priya Mehta"
    assert initial_status["status"] == InquiryStatus.PENDING.value
    assert isinstance(initial_status["created_at"], str)
    assert isinstance(initial_status["status_timeline"], list)
    assert initial_status["status_timeline"][0]["from_status"] is None
    assert initial_status["status_timeline"][0]["to_status"] == InquiryStatus.PENDING.value
    assert initial_status["admission"] is None

    updated = client.put(
        "/api/v1/public/student/inquiry/update",
        json={
            "inquiry_code": inquiry_code,
            "email": inquiry_payload["email"],
            "parent_mobile": inquiry_payload["parent_mobile"],
            "first_name": "Anaya",
            "last_school_percentage": 89.25,
        },
    )
    assert updated.status_code == 200, updated.text
    updated_data = updated.json()["data"]
    assert updated_data["student_name"] == "Anaya Priya Mehta"
    assert updated_data["admission_for_class"] == "Grade 6"

    inquiry = (
        db_session.query(StudentInquiry)
        .filter_by(inquiry_code=inquiry_code)
        .one()
    )
    assert inquiry.first_name == "Anaya"
    assert inquiry.middle_name == "Priya"
    assert inquiry.last_name == "Mehta"
    assert inquiry.gender == "female"
    assert inquiry.father_name == "Rohan Mehta"
    assert inquiry.date_of_birth == date(2015, 9, 22)
    assert inquiry.student_mobile == "+919876543210"
    assert inquiry.parent_mobile == "+919876543211"
    assert inquiry.email == "aanya.mehta.lifecycle@example.com"
    assert inquiry.address == "24 Lake View Road, Roh"
    assert inquiry.last_school == "Green Valley Public School"
    assert inquiry.current_class == "Grade 5"
    assert inquiry.admission_for_class == "Grade 6"
    assert inquiry.last_school_percentage == Decimal("89.25")
    assert inquiry.status == InquiryStatus.PENDING.value

    staff_list = client.get(
        "/api/v1/inquiries",
        params={"search": inquiry_code, "page": 1, "limit": 10},
        headers=auth_headers,
    )
    assert staff_list.status_code == 200, staff_list.text
    staff_items = staff_list.json()["data"]
    assert len(staff_items) == 1
    assert isinstance(staff_items[0]["id"], int)
    assert staff_items[0]["inquiry_code"] == inquiry_code
    staff_detail = client.get(
        f"/api/v1/inquiries/{inquiry.id}",
        headers=auth_headers,
    )
    assert staff_detail.status_code == 200, staff_detail.text
    assert staff_detail.json()["data"]["email"] == inquiry_payload["email"]

    review_started = client.post(
        f"/api/v1/inquiries/{inquiry.id}/review/start",
        headers=auth_headers,
        json={"notes": "Initial document and eligibility review."},
    )
    assert review_started.status_code == 200, review_started.text
    assert review_started.json()["data"]["status"] == InquiryStatus.UNDER_REVIEW.value
    review_processed = client.post(
        f"/api/v1/inquiries/{inquiry.id}/review/process",
        headers=auth_headers,
        json={"notes": "Eligible to schedule an admission interview."},
    )
    assert review_processed.status_code == 200, review_processed.text
    assert review_processed.json()["data"]["status"] == InquiryStatus.PROCESSING.value

    interview_date = date.today() + timedelta(days=14)
    scheduled = client.post(
        f"/api/v1/interviews/inquiries/{inquiry.id}/schedule",
        headers=auth_headers,
        json={
            "schedule_date": interview_date.isoformat(),
            "schedule_time": "10:30",
            "location": "RPS School, Admissions Office",
            "mode": "OFFLINE",
            "interviewer_teacher_id": None,
            "remarks": "Bring previous-school records.",
        },
    )
    assert scheduled.status_code == 201, scheduled.text
    interview_data = scheduled.json()["data"]
    assert isinstance(interview_data["id"], int)
    assert interview_data["inquiry_id"] == inquiry.id
    assert interview_data["schedule_date"] == interview_date.isoformat()
    assert interview_data["schedule_time"].startswith("10:30")
    assert interview_data["location"] == "RPS School, Admissions Office"
    assert interview_data["mode"] == "OFFLINE"
    assert interview_data["interviewer_teacher_id"] is None
    assert interview_data["result"] == "SCHEDULED"

    interview_result = client.post(
        f"/api/v1/interviews/{interview_data['id']}/result",
        headers=auth_headers,
        json={"result": "PASSED", "remarks": "Admission requirements met."},
    )
    assert interview_result.status_code == 200, interview_result.text
    assert interview_result.json()["data"]["result"] == "PASSED"
    eligible_status = client.get(
        f"/api/v1/public/student/inquiry/status/{inquiry_code}",
        headers=parent_headers,
    )
    eligible_data = eligible_status.json()["data"]
    assert eligible_data["status"] == InquiryStatus.INTERVIEW_PASS.value
    assert eligible_data["latest_interview"]["result"] == "PASSED"
    assert eligible_data["latest_interview"]["location"] == "RPS School, Admissions Office"

    public_classes = client.get("/api/v1/public/student/classes")
    assert public_classes.status_code == 200, public_classes.text
    matching_classes = [
        item for item in public_classes.json()["data"]
        if item["id"] == requested_class.id
    ]
    assert matching_classes == [{
        "id": requested_class.id,
        "name": "Grade 6",
        "section": "A",
        "academic_year": "2026-2027",
    }]

    admission_form = {
        "inquiry_code": inquiry_code,
        "email": inquiry_payload["email"],
        "parent_mobile": inquiry_payload["parent_mobile"],
        "class_id": str(requested_class.id),
        "academic_year": "2026-2027",
        "permanent_address": "26 Lake View Road, Roh",
        "student_aadhaar": "123456789012",
        "parent_aadhaar": "234567890123",
        "last_school_marks": "445.5",
        "last_school_percentage": "89.25",
        "last_school_id_or_roll_number": "GVPS-2025-061",
    }
    invalid_percentage = client.post(
        "/api/v1/public/student/admission",
        data={**admission_form, "last_school_percentage": "100.01"},
    )
    assert invalid_percentage.status_code == 422
    invalid_aadhaar = client.post(
        "/api/v1/public/student/admission",
        data={**admission_form, "student_aadhaar": "12345"},
    )
    assert invalid_aadhaar.status_code == 422

    submitted = client.post("/api/v1/public/student/admission", data=admission_form)
    assert submitted.status_code == 201, submitted.text
    submitted_data = submitted.json()["data"]
    assert set(submitted_data) == {"admission_code", "status"}
    assert isinstance(submitted_data["admission_code"], str)
    assert submitted_data["status"] == AdmissionStatus.SUBMITTED.value
    admission = (
        db_session.query(InquiryAdmission)
        .filter_by(inquiry_id=inquiry.id)
        .one()
    )
    assert admission.class_id == requested_class.id
    assert admission.section is None
    assert admission.academic_year == "2026-2027"
    assert admission.permanent_address == "26 Lake View Road, Roh"
    assert admission.student_aadhaar_last4 == "9012"
    assert admission.parent_aadhaar_last4 == "0123"
    assert admission.student_aadhaar_encrypted != admission_form["student_aadhaar"]
    assert admission.parent_aadhaar_encrypted != admission_form["parent_aadhaar"]
    assert isinstance(admission.last_school_marks, Decimal)
    assert admission.last_school_marks == Decimal("445.50")
    assert isinstance(admission.last_school_percentage, Decimal)
    assert admission.last_school_percentage == Decimal("89.25")
    assert admission.last_school_id_or_roll_number == "GVPS-2025-061"
    assert admission.student_id is None

    duplicate_submission = client.post(
        "/api/v1/public/student/admission",
        data=admission_form,
    )
    assert duplicate_submission.status_code == 409

    required_documents = {
        DocumentType.PROGRESS_REPORT.value,
        DocumentType.TRANSFER_CERTIFICATE.value,
        DocumentType.STUDENT_AADHAR.value,
        DocumentType.PARENT_AADHAR.value,
    }
    for document_type in sorted(required_documents):
        uploaded = client.post(
            "/api/v1/public/student/admission/documents",
            data={
                "inquiry_code": inquiry_code,
                "email": inquiry_payload["email"],
                "parent_mobile": inquiry_payload["parent_mobile"],
                "document_type": document_type,
            },
            files={
                "file": (
                    f"{document_type}.pdf",
                    b"%PDF-1.4 synthetic lifecycle test file",
                    "application/pdf",
                )
            },
        )
        assert uploaded.status_code == 201, uploaded.text
        uploaded_data = uploaded.json()["data"]
        assert uploaded_data["document_type"] == document_type
        assert uploaded_data["verification_status"] == DocumentVerificationStatus.PENDING.value
        assert "file_path" not in uploaded_data
    assert len(required_documents) == 4

    parent_status = client.get(
        f"/api/v1/public/student/inquiry/status/{inquiry_code}",
        headers=parent_headers,
    ).json()["data"]
    assert parent_status["status"] == InquiryStatus.DOCUMENT_PENDING.value
    assert parent_status["admission"]["status"] == AdmissionStatus.SUBMITTED.value
    assert parent_status["admission"]["documents_uploaded"] == 4
    assert parent_status["admission"]["documents_required"] == 4
    assert {
        document["document_type"]
        for document in parent_status["admission"]["documents"]
    } == required_documents

    admission_detail = client.get(
        f"/api/v1/inquiry-admissions/{admission.id}",
        headers=auth_headers,
    )
    assert admission_detail.status_code == 200, admission_detail.text
    admission_data = admission_detail.json()["data"]
    assert admission_data["class_name"] == "Grade 6"
    assert admission_data["inquiry_id"] == inquiry.id
    assert admission_data["class_id"] == requested_class.id
    assert admission_data["section"] is None
    assert admission_data["academic_year"] == "2026-2027"
    assert admission_data["status"] == AdmissionStatus.SUBMITTED.value
    assert admission_data["permanent_address"] == "26 Lake View Road, Roh"
    assert admission_data["student_aadhaar_masked"] == "XXXX XXXX 9012"
    assert admission_data["parent_aadhaar_masked"] == "XXXX XXXX 0123"
    assert isinstance(admission_data["last_school_marks"], (int, float))
    assert admission_data["last_school_marks"] == 445.5
    assert isinstance(admission_data["last_school_percentage"], (int, float))
    assert admission_data["last_school_percentage"] == 89.25
    assert admission_data["last_school_id_or_roll_number"] == "GVPS-2025-061"
    assert admission_data["temporary_address"] is None
    assert admission_data["nationality"] is None
    assert admission_data["disability"] is None
    assert admission_data["blood_group"] is None
    assert admission_data["reason_for_school_change"] is None
    assert admission_data["rejection_reason"] is None
    assert admission_data["notes"] is None
    assert admission_data["student_id"] is None
    assert "student_aadhaar_encrypted" not in admission_data
    assert "parent_aadhaar_encrypted" not in admission_data
    assert {
        document["document_type"]
        for document in admission_data["documents"]
    } == required_documents
    assert all(
        document["verification_status"] == DocumentVerificationStatus.PENDING.value
        for document in admission_data["documents"]
    )
    assert all(
        set(document) == {
            "id",
            "admission_id",
            "document_type",
            "file_name",
            "verification_status",
            "rejection_reason",
            "verified_at",
        }
        for document in admission_data["documents"]
    )

    for document in admission_data["documents"]:
        verified = client.post(
            f"/api/v1/documents/{document['id']}/verify",
            params={"verified": True},
            headers=auth_headers,
        )
        assert verified.status_code == 200, verified.text
        verified_data = verified.json()["data"]
        assert verified_data["document_type"] == document["document_type"]
        assert verified_data["verification_status"] == DocumentVerificationStatus.VERIFIED.value
        assert isinstance(verified_data["verified_at"], str)

    admission_after_verification = client.get(
        f"/api/v1/inquiry-admissions/{admission.id}",
        headers=auth_headers,
    ).json()["data"]
    assert admission_after_verification["status"] == AdmissionStatus.DOCUMENT_VERIFICATION.value
    assert inquiry.status == InquiryStatus.DOCUMENT_VERIFICATION.value
    approved = client.post(
        f"/api/v1/inquiry-admissions/{admission.id}/approve",
        headers=auth_headers,
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["data"]["status"] == AdmissionStatus.APPROVED.value

    enrolled = client.post(
        f"/api/v1/inquiry-admissions/{admission.id}/enroll",
        headers=auth_headers,
        json={"class_id": enrollment_class.id},
    )
    assert enrolled.status_code == 201, enrolled.text
    enrollment_data = enrolled.json()["data"]
    assert isinstance(enrollment_data["student_id"], int)
    assert enrollment_data["student_code"].startswith("RPS")
    assert enrollment_data["admission_id"] == admission.id
    assert enrollment_data["admission_code"] == enrollment_data["student_code"]
    assert enrollment_data["inquiry_code"] == inquiry_code
    assert enrollment_data["class_id"] == enrollment_class.id
    assert enrollment_data["section"] == "B"
    assert enrollment_data["academic_year"] == "2025-2026"
    assert isinstance(enrollment_data["roll_number"], int)
    assert enrollment_data["roll_number"] > 0

    enrolled_student = db_session.get(Student, enrollment_data["student_id"])
    db_session.refresh(admission)
    assert enrolled_student is not None
    assert isinstance(enrolled_student.date_of_birth, date)
    assert enrolled_student.student_code == enrollment_data["student_code"]
    assert enrolled_student.first_name == "Anaya"
    assert enrolled_student.last_name == "Mehta"
    assert enrolled_student.email == inquiry_payload["email"]
    assert enrolled_student.phone == inquiry_payload["student_mobile"]
    assert enrolled_student.class_id == enrollment_class.id
    assert enrolled_student.current_class_id == enrollment_class.id
    assert enrolled_student.academic_year == "2025-2026"
    assert enrolled_student.roll_number == enrollment_data["roll_number"]
    assert enrolled_student.status == StudentStatus.ACTIVE.value
    assert admission.class_id == enrollment_class.id
    assert admission.section == "B"
    assert admission.academic_year == "2025-2026"
    assert admission.student_id == enrolled_student.id
    assert admission.status == AdmissionStatus.APPROVED.value

    final_parent_status_response = client.get(
        f"/api/v1/public/student/inquiry/status/{inquiry_code}",
        headers=parent_headers,
    )
    assert final_parent_status_response.status_code == 200
    final_parent_status = final_parent_status_response.json()["data"]
    assert final_parent_status["status"] == InquiryStatus.ADMISSION_SUCCESS.value
    assert final_parent_status["admission"]["student_code"] == enrollment_data["student_code"]
    assert final_parent_status["admission"]["student_name"] == "Anaya Priya Mehta"
    assert final_parent_status["admission"]["class_name"] == "Grade 6"
    assert final_parent_status["admission"]["section"] == "B"
    assert final_parent_status["admission"]["academic_year"] == "2025-2026"
    assert final_parent_status["admission"]["roll_number"] == enrollment_data["roll_number"]

    registration_payload = {
        "admission_id": enrollment_data["student_code"].lower(),
        "email": inquiry_payload["email"],
        "password": "StrongStudent@123",
        "confirm_password": "StrongStudent@123",
    }
    weak_password = client.post(
        "/api/v1/auth/student/register",
        json={
            **registration_payload,
            "password": "weakpassword123",
            "confirm_password": "weakpassword123",
        },
    )
    assert weak_password.status_code == 422
    mismatched_password = client.post(
        "/api/v1/auth/student/register",
        json={**registration_payload, "confirm_password": "DifferentStudent@123"},
    )
    assert mismatched_password.status_code == 422
    registered = client.post(
        "/api/v1/auth/student/register",
        json=registration_payload,
    )
    assert registered.status_code == 201, registered.text
    registered_data = registered.json()["data"]
    assert set(registered_data) == {"student_id", "email"}
    assert registered_data["student_id"] == enrollment_data["student_code"]
    assert registered_data["email"] == inquiry_payload["email"]

    invalid_login = client.post(
        "/api/v1/auth/student/login",
        json={
            "student_id": enrollment_data["student_code"],
            "password": "WrongStudent@123",
        },
    )
    assert invalid_login.status_code == 401
    login = client.post(
        "/api/v1/auth/student/login",
        json={
            "student_id": enrollment_data["student_code"],
            "password": registration_payload["password"],
        },
    )
    assert login.status_code == 200, login.text
    login_data = login.json()["data"]
    assert set(login_data) == {
        "access_token",
        "refresh_token",
        "token_type",
        "expires_in",
    }
    assert isinstance(login_data["access_token"], str)
    assert isinstance(login_data["refresh_token"], str)
    assert login_data["token_type"].lower() == "bearer"
    assert isinstance(login_data["expires_in"], int)
    assert login_data["expires_in"] > 0
    student_headers = {"Authorization": f"Bearer {login_data['access_token']}"}

    profile_response = client.get("/api/v1/students/me", headers=student_headers)
    assert profile_response.status_code == 200, profile_response.text
    profile = profile_response.json()["data"]
    assert set(profile) == {
        "student_id",
        "admission_id",
        "first_name",
        "middle_name",
        "last_name",
        "father_name",
        "mother_name",
        "date_of_birth",
        "gender",
        "class_name",
        "section",
        "academic_year",
        "email",
        "phone",
        "address",
        "admission_date",
        "student_photo_url",
        "status",
    }
    assert profile["student_id"] == enrollment_data["student_code"]
    assert profile["admission_id"] == enrollment_data["student_code"]
    assert profile["first_name"] == "Anaya"
    assert profile["middle_name"] == "Priya"
    assert profile["last_name"] == "Mehta"
    assert profile["father_name"] == "Rohan Mehta"
    assert profile["mother_name"] is None
    assert profile["date_of_birth"] == "2015-09-22"
    assert profile["gender"] == "female"
    assert profile["class_name"] == "Grade 6"
    assert profile["section"] == "B"
    assert profile["academic_year"] == "2025-2026"
    assert profile["email"] == inquiry_payload["email"]
    assert profile["phone"] == inquiry_payload["student_mobile"]
    assert profile["address"] == "26 Lake View Road, Roh"
    assert isinstance(profile["admission_date"], str)
    datetime.fromisoformat(profile["admission_date"])
    assert profile["student_photo_url"] is None
    assert profile["status"] == StudentStatus.ACTIVE.value
