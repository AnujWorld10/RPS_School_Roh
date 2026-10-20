from datetime import date, time
from io import BytesIO
from unittest.mock import MagicMock

import pytest
from fastapi import UploadFile
from sqlalchemy import inspect as sqlalchemy_inspect
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import BusinessRuleException, ConflictException, NotFoundException
from app.core.pagination import PaginationParams
from app.core.security import hash_password
from app.models.admission import AdmissionDocument, InquiryAdmission
from app.models.class_model import Class
from app.models.enums import (
    AdmissionStatus,
    DocumentType,
    DocumentVerificationStatus,
    InquiryStatus,
    InterviewMode,
    InterviewResult,
    InterviewResultUpdate,
    StudentStatus,
    TeacherStatus,
    UserStatus,
)
from app.models.interview import InterviewSchedule
from app.models.role import Role
from app.models.student import Student
from app.models.student_inquiry import StudentInquiry
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.user import User
from app.repositories.inquiries import StudentInquiryRepository
from app.repositories.inquiry_admissions import InquiryAdmissionRepository
from app.repositories.students import StudentRepository
from app.schemas.classes import ClassUpdateRequest
from app.schemas.inquiries import PublicInquiryCreateRequest
from app.schemas.interviews import InterviewResultUpdateRequest
from app.schemas.students import StudentClassAssignRequest
from app.schemas.teachers import SubjectAssignRequest
from app.services.classes import ClassService
from app.services.enrollment import EnrollmentService
from app.services.inquiries import InquiryService
from app.services.inquiry_admissions import InquiryAdmissionService
from app.services.interviews import InterviewService
from app.services.students import StudentService
from app.services.teachers import TeacherService
from app.utils.inquiry_ids import generate_inquiry_identifiers, inquiry_identity_key


def _request():
    request = MagicMock()
    request.state.request_id = "phase2-test"
    request.client = None
    request.headers = {}
    return request


def _inquiry(
    db_session,
    *,
    status: str = InquiryStatus.PENDING.value,
    identity: tuple[str, str, str] = ("Avery", "Morgan", "Jordan Morgan"),
):
    inquiry_code, serial_number = generate_inquiry_identifiers(db_session)
    first_name, last_name, father_name = identity
    inquiry = StudentInquiry(
        inquiry_code=inquiry_code,
        serial_number=serial_number,
        duplicate_key=inquiry_identity_key(
            first_name,
            last_name,
            father_name,
            date(2015, 5, 14),
        ),
        first_name=first_name,
        last_name=last_name,
        father_name=father_name,
        date_of_birth=date(2015, 5, 14),
        gender="female",
        parent_mobile="5550001000",
        email=f"{serial_number}@example.test",
        address="10 School Road",
        last_school="Previous School",
        current_class="Grade 4",
        admission_for_class="Grade 5",
        status=status,
    )
    db_session.add(inquiry)
    db_session.flush()
    return inquiry


def _create_user_with_role(db_session, email: str, role_code: str) -> User:
    role = db_session.query(Role).filter(Role.code == role_code).one()
    user = User(
        first_name="Phase",
        last_name="Two",
        email=email,
        password_hash=hash_password("ValidPassword@123"),
        status=UserStatus.ACTIVE.value,
    )
    user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    return user


def test_inquiry_lifecycle_transitions_commit_and_validate(db_session):
    inquiry = _inquiry(db_session)
    db_session.commit()
    service = InquiryService(db_session)
    request = _request()

    assert service.start_review(inquiry.id, 1, request, None).status == "UNDER_REVIEW"
    assert service.mark_processing(inquiry.id, 1, request, None).status == "PROCESSING"
    assert (
        service.transition_status(
            inquiry.id,
            InquiryStatus.INTERVIEW_SCHEDULED.value,
            1,
            request,
        ).status
        == "INTERVIEW_SCHEDULED"
    )
    assert (
        service.transition_status(
            inquiry.id,
            InquiryStatus.INTERVIEW_PASS.value,
            1,
            request,
        ).status
        == "INTERVIEW_PASS"
    )

    with pytest.raises(BusinessRuleException):
        service.transition_status(inquiry.id, "NOT_A_STATUS", 1, request)
    with pytest.raises(BusinessRuleException, match="Rejection reason is required"):
        service.transition_status(inquiry.id, InquiryStatus.REJECTED.value, 1, request)

    rejected = service.transition_status(
        inquiry.id,
        InquiryStatus.REJECTED.value,
        1,
        request,
        rejection_reason="Not eligible",
    )
    assert rejected.status == InquiryStatus.REJECTED.value
    assert rejected.duplicate_key is None


def test_scheduled_interview_can_transition_to_failed(db_session):
    inquiry = _inquiry(db_session, status=InquiryStatus.INTERVIEW_SCHEDULED.value)
    db_session.commit()

    failed = InquiryService(db_session).transition_status(
        inquiry.id,
        InquiryStatus.INTERVIEW_FAIL.value,
        1,
        _request(),
    )

    assert failed.status == InquiryStatus.INTERVIEW_FAIL.value
    assert failed.duplicate_key is None


@pytest.mark.parametrize(
    ("result", "expected_status"),
    [
        (InterviewResultUpdate.PASSED, InquiryStatus.INTERVIEW_PASS),
        (InterviewResultUpdate.FAILED, InquiryStatus.INTERVIEW_FAIL),
    ],
)
def test_record_interview_result_updates_inquiry_atomically(
    db_session,
    result,
    expected_status,
):
    inquiry = _inquiry(db_session, status=InquiryStatus.INTERVIEW_SCHEDULED.value)
    interview = InterviewSchedule(
        inquiry_id=inquiry.id,
        schedule_date=date.today(),
        schedule_time=time(10, 0),
        location="School",
        mode=InterviewMode.OFFLINE.value,
        result=InterviewResult.SCHEDULED.value,
    )
    db_session.add(interview)
    db_session.commit()

    updated = InterviewService(db_session).record_result(
        interview.id,
        InterviewResultUpdateRequest(result=result),
        1,
        _request(),
    )

    assert updated.result == result.value
    assert inquiry.status == expected_status.value


def test_inquiry_and_admission_lists_eager_load_serialized_collections(db_session):
    inquiry = _inquiry(db_session)
    school_class = Class(
        name="Phase Three Eager Loading",
        section="C",
        academic_year="2026-2027",
        capacity=20,
        status="active",
    )
    db_session.add(school_class)
    db_session.flush()
    admission = InquiryAdmission(
        admission_code="ADM-PHASE3-EAGER",
        inquiry_id=inquiry.id,
        class_id=school_class.id,
        academic_year=school_class.academic_year,
        status=AdmissionStatus.DOCUMENT_PENDING.value,
    )
    db_session.add(admission)
    db_session.flush()
    db_session.add(
        AdmissionDocument(
            admission_id=admission.id,
            document_type=DocumentType.PROGRESS_REPORT.value,
            file_name="progress.pdf",
            file_path="progress.pdf",
            verification_status=DocumentVerificationStatus.PENDING.value,
        )
    )
    student = Student(
        student_code="STU-PHASE3-EAGER",
        first_name="Eager",
        last_name="Student",
        date_of_birth=date(2015, 1, 1),
        gender="female",
        class_id=school_class.id,
        current_class_id=school_class.id,
        academic_year=school_class.academic_year,
        status=StudentStatus.ACTIVE.value,
    )
    db_session.add(student)
    db_session.commit()

    inquiries = StudentInquiryRepository(db_session).list_filtered(PaginationParams())
    admissions = InquiryAdmissionRepository(db_session).list_filtered(PaginationParams())
    students = StudentRepository(db_session).list_filtered(PaginationParams())

    loaded_inquiry = next(item for item in inquiries.items if item.id == inquiry.id)
    loaded_admission = next(item for item in admissions.items if item.id == admission.id)
    assert {"status_history", "interviews"}.isdisjoint(
        sqlalchemy_inspect(loaded_inquiry).unloaded
    )
    assert "documents" not in sqlalchemy_inspect(loaded_admission).unloaded
    loaded_student = next(item for item in students.items if item.id == student.id)
    assert "current_class" not in sqlalchemy_inspect(loaded_student).unloaded


def test_public_duplicate_detection_rejects_normalized_identity(db_session):
    _inquiry(db_session)
    db_session.commit()
    payload = PublicInquiryCreateRequest(
        first_name=" aVERY ",
        last_name="MORGAN",
        gender="female",
        father_name="jordan   morgan",
        dob=date(2015, 5, 14),
        parent_mobile="5550002000",
        email="different@example.com",
        address="20 Another Road",
        last_school="Different School",
        current_class="Grade 4",
        admission_for_class="Grade 5",
    )

    with pytest.raises(ConflictException):
        InquiryService(db_session).create_public_inquiry(payload, _request())


def test_database_unique_key_closes_duplicate_submission_race(db_session):
    _inquiry(db_session)
    db_session.commit()
    duplicate = StudentInquiry(
        inquiry_code="INQ-PHASE2-RACE",
        serial_number=999991,
        duplicate_key=inquiry_identity_key(
            "AVERY",
            "MORGAN",
            "JORDAN MORGAN",
            date(2015, 5, 14),
        ),
        first_name="AVERY",
        last_name="MORGAN",
        father_name="JORDAN MORGAN",
        date_of_birth=date(2015, 5, 14),
        gender="female",
        parent_mobile="5550002000",
        email="race@example.test",
        address="20 Another Road",
        last_school="Different School",
        current_class="Grade 4",
        admission_for_class="Grade 5",
        status=InquiryStatus.PENDING.value,
    )
    db_session.add(duplicate)

    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_class_rename_uses_existing_academic_year(db_session):
    school_class = Class(
        name="Phase Two Rename",
        section="Z",
        academic_year="2026-2027",
        capacity=20,
        status="active",
    )
    db_session.add(school_class)
    db_session.commit()

    updated = ClassService(db_session).update_class(
        school_class.id,
        ClassUpdateRequest(name="Phase Two Renamed"),
        1,
        _request(),
    )

    assert updated.name == "Phase Two Renamed"
    assert updated.academic_year == "2026-2027"


def test_principal_can_start_inquiry_review(client, db_session):
    principal = _create_user_with_role(
        db_session,
        "phase2-principal@example.test",
        "PRINCIPAL",
    )
    inquiry = _inquiry(db_session)
    db_session.commit()
    login = client.post(
        "/api/v1/auth/login",
        json={"email": principal.email, "password": "ValidPassword@123"},
    )
    assert login.status_code == 200
    result = client.post(
        f"/api/v1/inquiries/{inquiry.id}/review/start",
        headers={
            "Authorization": f"Bearer {login.json()['data']['access_token']}",
        },
    )
    assert result.status_code == 200
    assert result.json()["data"]["status"] == InquiryStatus.UNDER_REVIEW.value


def test_document_replacement_revokes_approval_and_requires_reverification(
    db_session,
    monkeypatch,
):
    inquiry = _inquiry(db_session, status=InquiryStatus.DOCUMENT_VERIFICATION.value)
    school_class = Class(
        name="Phase Two Admissions",
        section="A",
        academic_year="2026-2027",
        capacity=30,
        status="active",
    )
    db_session.add(school_class)
    db_session.flush()
    admission = InquiryAdmission(
        admission_code="ADM-PHASE2-REPLACE",
        inquiry_id=inquiry.id,
        class_id=school_class.id,
        academic_year=school_class.academic_year,
        status=AdmissionStatus.APPROVED.value,
        approved_by=None,
    )
    db_session.add(admission)
    db_session.flush()
    document = AdmissionDocument(
        admission_id=admission.id,
        document_type=DocumentType.PROGRESS_REPORT.value,
        file_name="old.pdf",
        file_path="old.pdf",
        verification_status=DocumentVerificationStatus.VERIFIED.value,
    )
    db_session.add(document)
    db_session.commit()
    monkeypatch.setattr(
        "app.services.inquiry_admissions.save_upload_file",
        lambda file, subdirectory: ("new.pdf", file.filename),
    )

    updated = InquiryAdmissionService(db_session).upload_document(
        admission.id,
        DocumentType.PROGRESS_REPORT.value,
        UploadFile(filename="new.pdf", file=BytesIO(b"replacement")),
        _request(),
    )

    assert updated.verification_status == DocumentVerificationStatus.PENDING.value
    assert admission.status == AdmissionStatus.DOCUMENT_PENDING.value
    assert admission.approved_by is None
    assert admission.approved_at is None
    assert inquiry.status == InquiryStatus.DOCUMENT_PENDING.value


def test_enrollment_revalidates_documents_inside_transaction(db_session):
    inquiry = _inquiry(db_session, status=InquiryStatus.DOCUMENT_VERIFICATION.value)
    school_class = Class(
        name="Phase Two Missing Documents",
        section="B",
        academic_year="2026-2027",
        capacity=30,
        status="active",
    )
    db_session.add(school_class)
    db_session.flush()
    admission = InquiryAdmission(
        admission_code="ADM-P2-MISSING-DOCS",
        inquiry_id=inquiry.id,
        class_id=school_class.id,
        academic_year=school_class.academic_year,
        status=AdmissionStatus.APPROVED.value,
    )
    db_session.add(admission)
    db_session.flush()
    db_session.add(
        AdmissionDocument(
            admission_id=admission.id,
            document_type=DocumentType.PROGRESS_REPORT.value,
            file_name="report.pdf",
            file_path="report.pdf",
            verification_status=DocumentVerificationStatus.VERIFIED.value,
        )
    )
    db_session.commit()

    with pytest.raises(BusinessRuleException, match="All required documents"):
        EnrollmentService(db_session).enroll_student(admission.id, 1, _request())


def test_student_class_assignment_updates_authoritative_and_legacy_fields(db_session):
    school_class = db_session.query(Class).filter(Class.deleted_at.is_(None)).first()
    assert school_class is not None
    student = Student(
        student_code="STU-PHASE2-CLASS",
        first_name="Class",
        last_name="Assignment",
        date_of_birth=date(2015, 1, 1),
        gender="female",
        status=StudentStatus.PROSPECTIVE.value,
    )
    db_session.add(student)
    db_session.commit()
    teacher = Teacher(
        employee_no="PHASE2-CLASS-TEACHER",
        first_name="Class",
        last_name="Teacher",
        email="phase2-class-teacher@example.test",
        status=TeacherStatus.ACTIVE.value,
    )
    subject = Subject(code="PHASE2-CLASS-SUBJECT", name="Class Subject")
    db_session.add_all([teacher, subject])
    db_session.commit()
    class_service = ClassService(db_session)
    class_service.assign_class_teacher(school_class.id, teacher.id, 1, _request())
    class_service.assign_subject(school_class.id, subject.id, 1, _request())

    updated = StudentService(db_session).assign_class(
        student.id,
        StudentClassAssignRequest(
            class_id=school_class.id,
            academic_year=school_class.academic_year,
        ),
        1,
        _request(),
    )

    assert updated.class_id == school_class.id
    assert updated.current_class_id == school_class.id
    assert updated.academic_year == school_class.academic_year
    assert updated.status == StudentStatus.ACTIVE.value


def test_assigning_nonexistent_subject_returns_not_found(db_session):
    teacher = Teacher(
        employee_no="PHASE2-SUBJECT",
        first_name="Subject",
        last_name="Assignment",
        email="subject-assignment@example.test",
        status=TeacherStatus.ACTIVE.value,
    )
    db_session.add(teacher)
    db_session.flush()

    with pytest.raises(NotFoundException, match="subject not found"):
        TeacherService(db_session).assign_subject(
            teacher.id,
            SubjectAssignRequest(subject_id=99999),
            1,
            _request(),
        )
