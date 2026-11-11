from datetime import UTC, date, datetime
from unittest.mock import MagicMock

from fastapi import status

from app.core.security import hash_password
from app.models.admission import AdmissionDocument, InquiryAdmission
from app.models.class_model import Class
from app.models.enums import (
    AdmissionStatus,
    DocumentType,
    DocumentVerificationStatus,
    StudentStatus,
    TeacherStatus,
    UserStatus,
)
from app.models.role import Role
from app.models.student import Student
from app.models.student_inquiry import StudentInquiry
from app.models.subject import ClassSubject, Subject
from app.models.teacher import Teacher
from app.models.user import User
from app.services.enrollment import EnrollmentService

PASSWORD = "StrongStudent@123"


def _request():
    request = MagicMock()
    request.state.request_id = "student-portal-test"
    request.client = None
    request.headers = {}
    return request


def _admitted_student(db_session, *, code="RPS00001", email="student@example.test"):
    school_class = Class(
        name=f"Portal Grade {code[-1]}",
        section="A",
        academic_year="2026-2027",
        capacity=30,
        status="active",
    )
    inquiry = StudentInquiry(
        inquiry_code=f"INQ-{code}",
        serial_number=int(code[-1]),
        duplicate_key=None,
        first_name="Aarav",
        middle_name="Kumar",
        last_name="Sharma",
        gender="male",
        father_name="Raj Sharma",
        date_of_birth=date(2015, 5, 14),
        student_mobile="9000000001",
        parent_mobile="9000000002",
        email=email,
        address="12 School Road",
        last_school="Previous School",
        current_class="Grade 4",
        admission_for_class="Grade 5",
        status="ADMISSION_SUCCESS",
    )
    db_session.add_all([school_class, inquiry])
    db_session.flush()
    student = Student(
        student_code=code,
        admission_no=code,
        inquiry_id=inquiry.id,
        first_name=inquiry.first_name,
        last_name=inquiry.last_name,
        date_of_birth=inquiry.date_of_birth,
        gender=inquiry.gender,
        email=email,
        phone=inquiry.student_mobile,
        class_id=school_class.id,
        current_class_id=school_class.id,
        academic_year=school_class.academic_year,
        status=StudentStatus.ACTIVE.value,
    )
    db_session.add(student)
    db_session.flush()
    admission = InquiryAdmission(
        admission_code=code,
        inquiry_id=inquiry.id,
        class_id=school_class.id,
        section=school_class.section,
        academic_year=school_class.academic_year,
        status=AdmissionStatus.APPROVED.value,
        student_id=student.id,
        approved_at=datetime.now(UTC),
        permanent_address=inquiry.address,
    )
    db_session.add(admission)
    db_session.commit()
    return student, admission, school_class


def _registration_payload(admission_id="RPS00001", email="student@example.test"):
    return {
        "admission_id": admission_id,
        "email": email,
        "password": PASSWORD,
        "confirm_password": PASSWORD,
    }


def _login(client, student_id="RPS00001", password=PASSWORD):
    return client.post(
        "/api/v1/auth/student/login",
        json={"student_id": student_id, "password": password},
    )


def test_enrollment_assigns_matching_school_wide_student_and_admission_ids(db_session):
    school_class = Class(
        name="Portal Enrollment Grade",
        section="A",
        academic_year="2026-2027",
        capacity=30,
        status="active",
    )
    teacher = Teacher(
        employee_no="PORTAL-TEACHER-1",
        first_name="Class",
        last_name="Teacher",
        email="portal-teacher@example.test",
        status=TeacherStatus.ACTIVE.value,
    )
    subject = Subject(code="PORTAL-SUBJECT", name="Portal Subject", is_active=True)
    db_session.add_all([school_class, teacher, subject])
    db_session.flush()
    school_class.class_teacher_id = teacher.id
    db_session.add(ClassSubject(class_id=school_class.id, subject_id=subject.id))
    inquiry = StudentInquiry(
        inquiry_code="INQ-PORTAL-ENROLL",
        serial_number=90001,
        duplicate_key=None,
        first_name="Aarav",
        last_name="Sharma",
        gender="male",
        father_name="Raj Sharma",
        date_of_birth=date(2015, 5, 14),
        parent_mobile="9000000002",
        email="enrollment@example.test",
        address="12 School Road",
        last_school="Previous School",
        current_class="Grade 4",
        admission_for_class="Grade 5",
        status="DOCUMENT_VERIFICATION",
    )
    db_session.add(inquiry)
    db_session.flush()
    admission = InquiryAdmission(
        admission_code="ADM-PORTAL-ENROLL",
        inquiry_id=inquiry.id,
        class_id=school_class.id,
        section=school_class.section,
        academic_year=school_class.academic_year,
        status=AdmissionStatus.APPROVED.value,
    )
    db_session.add(admission)
    db_session.flush()
    db_session.add_all(
        AdmissionDocument(
            admission_id=admission.id,
            document_type=document_type.value,
            file_name=f"{document_type.value}.pdf",
            file_path=f"{document_type.value}.pdf",
            verification_status=DocumentVerificationStatus.VERIFIED.value,
        )
        for document_type in DocumentType
    )
    db_session.commit()

    enrollment = EnrollmentService(db_session).enroll_student(
        admission.id,
        1,
        _request(),
    )

    assert enrollment.student_code == "RPS00001"
    assert enrollment.admission_code == enrollment.student_code
    student = db_session.get(Student, enrollment.student_id)
    saved_admission = db_session.get(InquiryAdmission, admission.id)
    assert student is not None
    assert student.student_code == student.admission_no == saved_admission.admission_code


def test_student_registration_validates_admission_email_and_single_account(
    client,
    db_session,
):
    _admitted_student(db_session)

    invalid_id = client.post(
        "/api/v1/auth/student/register",
        json=_registration_payload(admission_id="RPS99999"),
    )
    assert invalid_id.status_code == status.HTTP_401_UNAUTHORIZED
    invalid_email = client.post(
        "/api/v1/auth/student/register",
        json=_registration_payload(email="wrong@example.test"),
    )
    assert invalid_email.status_code == status.HTTP_401_UNAUTHORIZED

    registered = client.post(
        "/api/v1/auth/student/register",
        json=_registration_payload(),
    )
    assert registered.status_code == status.HTTP_201_CREATED
    assert registered.json()["data"]["student_id"] == "RPS00001"

    duplicate = client.post(
        "/api/v1/auth/student/register",
        json=_registration_payload(),
    )
    assert duplicate.status_code == status.HTTP_409_CONFLICT
    student = db_session.query(Student).filter_by(student_code="RPS00001").one()
    assert student.user_id is not None
    user = db_session.get(User, student.user_id)
    assert user is not None
    assert user.email == "student@example.test"
    assert [role.code for role in user.roles] == ["STUDENT"]


def test_student_login_profile_and_fees_are_scoped_to_linked_student(client, db_session):
    student, _, school_class = _admitted_student(db_session)
    other_student, _, _ = _admitted_student(
        db_session,
        code="RPS00002",
        email="student@example.test",
    )
    role = db_session.query(Role).filter_by(code="STUDENT").one()
    user = User(
        first_name=student.first_name,
        last_name=student.last_name,
        email="student@example.test",
        password_hash=hash_password(PASSWORD),
        status=UserStatus.ACTIVE.value,
    )
    user.roles.append(role)
    db_session.add(user)
    db_session.flush()
    student.user_id = user.id
    db_session.commit()

    login = _login(client)
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

    profile = client.get("/api/v1/students/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["data"]["student_id"] == student.student_code
    assert profile.json()["data"]["admission_id"] == student.student_code
    assert profile.json()["data"]["class_name"] == school_class.name
    assert profile.json()["data"]["father_name"] == "Raj Sharma"

    listed = client.get("/api/v1/students?page=1&limit=100", headers=headers)
    assert listed.status_code == 200
    assert [record["id"] for record in listed.json()["data"]] == [student.id]
    other_profile = client.get(f"/api/v1/students/{other_student.id}", headers=headers)
    assert other_profile.status_code == status.HTTP_404_NOT_FOUND

    fees = client.get("/api/v1/students/me/fees", headers=headers)
    assert fees.status_code == 200
    fee_data = fees.json()["data"]
    assert fee_data["student_id"] == student.student_code
    assert fee_data["payment_records_available"] is False
    assert fee_data["paid_amount"] is None
    assert fee_data["pending_amount"] is None
    assert fee_data["payment_status"] is None

    pdf = client.get(
        "/api/v1/students/me/fees/monthly/pdf?month=4&year=2026",
        headers=headers,
    )
    assert pdf.status_code == status.HTTP_501_NOT_IMPLEMENTED
    assert pdf.json()["errors"][0]["code"] == "FEE_BILLING_UNAVAILABLE"


def test_student_registration_requires_completed_admission(client, db_session):
    _, admission, _ = _admitted_student(db_session)
    admission.status = AdmissionStatus.SUBMITTED.value
    db_session.commit()

    response = client.post(
        "/api/v1/auth/student/register",
        json=_registration_payload(),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_student_portal_requires_student_authentication(client):
    assert client.get("/api/v1/students/me").status_code == status.HTTP_401_UNAUTHORIZED
    assert _login(client).status_code == status.HTTP_401_UNAUTHORIZED
