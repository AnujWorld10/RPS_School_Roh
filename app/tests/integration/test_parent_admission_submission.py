from datetime import date
from time import time_ns

from cryptography.fernet import Fernet

from app.core.config import get_settings
from app.models.admission import InquiryAdmission
from app.models.class_model import Class
from app.models.enums import (
    ClassStatus,
    DocumentType,
    InquiryStatus,
)
from app.models.student_inquiry import StudentInquiry
from app.utils.admission_pii import encrypt_aadhaar


def _admission_candidate(db_session, client):
    suffix = str(time_ns())
    inquiry = StudentInquiry(
        inquiry_code=f"INQ{suffix[-10:]}",
        serial_number=int(suffix[-9:]),
        duplicate_key=None,
        first_name="Aarav",
        last_name="Sharma",
        gender="male",
        father_name="Raj Sharma",
        date_of_birth=date(2015, 5, 14),
        parent_mobile="9000000002",
        email=f"parent-{suffix}@example.com",
        address="12 School Road",
        last_school="Previous School",
        current_class="Grade 4",
        admission_for_class="Grade 5",
        status=InquiryStatus.INTERVIEW_PASS.value,
    )
    school_class = Class(
        name="Grade 5",
        section="A",
        academic_year="2026-2027",
        capacity=30,
        status=ClassStatus.ACTIVE.value,
    )
    db_session.add_all([inquiry, school_class])
    db_session.commit()

    response = client.post(
        "/api/v1/public/student/admission",
        data={
            "inquiry_code": inquiry.inquiry_code,
            "email": inquiry.email,
            "parent_mobile": inquiry.parent_mobile,
            "class_id": school_class.id,
            "academic_year": school_class.academic_year,
            "student_aadhaar": "012345678901",
            "parent_aadhaar": "987654321098",
            "last_school_marks": "450",
            "last_school_percentage": "90.5",
            "last_school_id_or_roll_number": "PREV-ROLL-12",
        },
    )
    assert response.status_code == 201, response.text
    admission = (
        db_session.query(InquiryAdmission)
        .filter(InquiryAdmission.inquiry_id == inquiry.id)
        .one()
    )
    assert admission.section is None
    return inquiry, school_class, admission


def test_parent_submits_encrypted_details_documents_and_receives_admission_letter(
    client,
    db_session,
    auth_headers,
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(get_settings(), "upload_dir", str(tmp_path))
    inquiry, school_class, admission = _admission_candidate(db_session, client)
    aadhaar_key = get_settings().admission_pii_encryption_key.get_secret_value().encode()
    assert admission.student_aadhaar_encrypted != "012345678901"
    assert (
        Fernet(aadhaar_key).decrypt(admission.student_aadhaar_encrypted.encode())
        == b"012345678901"
    )
    assert admission.parent_aadhaar_encrypted != "987654321098"
    assert admission.student_aadhaar_last4 == "8901"
    assert admission.parent_aadhaar_last4 == "1098"
    assert admission.last_school_marks == 450
    assert admission.last_school_percentage == 90.5
    assert admission.last_school_id_or_roll_number == "PREV-ROLL-12"

    staff_view = client.get(
        f"/api/v1/inquiry-admissions/{admission.id}",
        headers=auth_headers,
    )
    assert staff_view.status_code == 200
    staff_data = staff_view.json()["data"]
    assert staff_data["student_aadhaar_masked"] == "XXXX XXXX 8901"
    assert staff_data["parent_aadhaar_masked"] == "XXXX XXXX 1098"
    assert "student_aadhaar_encrypted" not in staff_data
    assert "parent_aadhaar_encrypted" not in staff_data

    credentials = {
        "inquiry_code": inquiry.inquiry_code,
        "email": inquiry.email,
        "parent_mobile": inquiry.parent_mobile,
    }
    document_id = None
    for document_type in (
        DocumentType.PROGRESS_REPORT,
        DocumentType.TRANSFER_CERTIFICATE,
        DocumentType.STUDENT_AADHAR,
        DocumentType.PARENT_AADHAR,
    ):
        uploaded = client.post(
            "/api/v1/public/student/admission/documents",
            data={**credentials, "document_type": document_type.value},
            files={
                "file": (
                    f"{document_type.value}.pdf",
                    b"%PDF-1.4 test document",
                    "application/pdf",
                )
            },
        )
        assert uploaded.status_code == 201, uploaded.text
        assert "file_path" not in uploaded.json()["data"]
        if document_type is DocumentType.PROGRESS_REPORT:
            document_id = (
                db_session.query(InquiryAdmission)
                .filter(InquiryAdmission.id == admission.id)
                .one()
                .documents[0]
                .id
            )

    optional_upload = client.post(
        "/api/v1/public/student/admission/documents",
        data={**credentials, "document_type": DocumentType.MIGRATION_CERTIFICATE.value},
        files={"file": ("migration.pdf", b"%PDF-1.4 optional", "application/pdf")},
    )
    assert optional_upload.status_code == 201, optional_upload.text

    assert document_id is not None
    file_response = client.get(
        f"/api/v1/documents/{document_id}/file",
        headers=auth_headers,
    )
    assert file_response.status_code == 200
    assert file_response.headers["content-type"] == "application/pdf"
    assert file_response.headers["content-disposition"] == "inline"

    for document in admission.documents:
        if document.document_type == DocumentType.MIGRATION_CERTIFICATE.value:
            continue
        verified = client.post(
            f"/api/v1/documents/{document.id}/verify",
            params={"verified": True},
            headers=auth_headers,
        )
        assert verified.status_code == 200, verified.text

    approved = client.post(
        f"/api/v1/inquiry-admissions/{admission.id}/approve",
        headers=auth_headers,
    )
    assert approved.status_code == 200, approved.text
    enrollment_section = Class(
        name=school_class.name,
        section="B",
        academic_year="2025-2026",
        capacity=30,
        status=ClassStatus.ACTIVE.value,
    )
    db_session.add(enrollment_section)
    db_session.commit()
    enrolled = client.post(
        f"/api/v1/inquiry-admissions/{admission.id}/enroll",
        headers=auth_headers,
        json={"class_id": enrollment_section.id},
    )
    assert enrolled.status_code == 201, enrolled.text
    student_code = enrolled.json()["data"]["student_code"]
    assert enrolled.json()["data"]["section"] == "B"
    assert enrolled.json()["data"]["class_id"] == enrollment_section.id
    assert enrolled.json()["data"]["academic_year"] == "2025-2026"

    status_response = client.get(
        f"/api/v1/public/student/inquiry/status/{inquiry.inquiry_code}",
        headers={
            "X-Parent-Email": inquiry.email,
            "X-Parent-Mobile": inquiry.parent_mobile,
        },
    )
    assert status_response.status_code == 200
    public_status = status_response.json()["data"]
    assert public_status["status"] == InquiryStatus.ADMISSION_SUCCESS.value
    assert public_status["admission"]["student_code"] == student_code
    assert public_status["admission"]["class_name"] == school_class.name
    assert public_status["admission"]["section"] == "B"
    assert public_status["admission"]["academic_year"] == "2025-2026"
    assert "012345678901" not in str(public_status)
    assert "987654321098" not in str(public_status)

    letter = client.get(
        f"/api/v1/public/student/inquiry/status/{inquiry.inquiry_code}/admission-letter",
        headers={
            "X-Parent-Email": inquiry.email,
            "X-Parent-Mobile": inquiry.parent_mobile,
        },
    )
    assert letter.status_code == 200
    assert letter.headers["content-type"] == "application/pdf"
    assert letter.content.startswith(b"%PDF")
    assert b"012345678901" not in letter.content
    assert b"987654321098" not in letter.content


def test_admission_aadhaar_requires_twelve_digit_strings(client, db_session):
    inquiry, school_class, _ = _admission_candidate(db_session, client)
    duplicate_inquiry = StudentInquiry(
        inquiry_code=f"INQ{time_ns() % 10**10:010d}",
        serial_number=int(time_ns() % 10**9),
        duplicate_key=None,
        first_name="Mira",
        last_name="Sharma",
        gender="female",
        father_name="Raj Sharma",
        date_of_birth=date(2016, 6, 15),
        parent_mobile="9000000003",
        email=f"second-{time_ns()}@example.com",
        address="13 School Road",
        last_school="Previous School",
        current_class="Grade 4",
        admission_for_class="Grade 5",
        status=InquiryStatus.INTERVIEW_PASS.value,
    )
    db_session.add(duplicate_inquiry)
    db_session.commit()
    response = client.post(
        "/api/v1/public/student/admission",
        data={
            "inquiry_code": duplicate_inquiry.inquiry_code,
            "email": duplicate_inquiry.email,
            "parent_mobile": duplicate_inquiry.parent_mobile,
            "class_id": school_class.id,
            "academic_year": school_class.academic_year,
            "student_aadhaar": "1234",
            "parent_aadhaar": "987654321098",
            "last_school_marks": "450",
            "last_school_percentage": "90",
            "last_school_id_or_roll_number": "PREV-ROLL-13",
        },
    )
    assert response.status_code == 422
    assert inquiry.id != duplicate_inquiry.id
    assert encrypt_aadhaar("012345678901") != "012345678901"
