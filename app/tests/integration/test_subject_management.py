from datetime import date
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import (
    BusinessRuleException,
    ConflictException,
)
from app.core.security import hash_password
from app.models.enums import StudentStatus, TeacherStatus, UserStatus
from app.models.role import Role
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.user import User
from app.schemas.classes import ClassCreateRequest
from app.schemas.students import StudentClassAssignRequest, StudentUpdateRequest
from app.schemas.subjects import (
    SubjectCreateRequest,
    TeacherClassSubjectAssignRequest,
)
from app.services.classes import ClassService
from app.services.students import StudentService
from app.services.subjects import SubjectService
from app.services.teachers import TeacherService


def _request():
    request = MagicMock()
    request.state.request_id = "subject-management-test"
    request.client = None
    request.headers = {}
    return request


def _create_subject(db_session, code="MATH", name="Mathematics"):
    return SubjectService(db_session).create(
        SubjectCreateRequest(code=code, name=name),
        1,
        _request(),
    )


def _create_class(db_session, name="Grade 5", year="2026-2027"):
    return ClassService(db_session).create_class(
        ClassCreateRequest(name=name, section="A", academic_year=year, capacity=30),
        1,
        _request(),
    )


def _create_teacher(db_session, employee_no="EMP-SUBJECT-1"):
    teacher = Teacher(
        employee_no=employee_no,
        first_name="Subject",
        last_name="Teacher",
        email=f"{employee_no.lower()}@example.test",
        status=TeacherStatus.ACTIVE.value,
    )
    db_session.add(teacher)
    db_session.commit()
    return teacher


def test_subject_crud_and_deactivation_are_audited(client, auth_headers):
    created = client.post(
        "/api/v1/subjects",
        json={"code": " math ", "name": " Mathematics "},
        headers=auth_headers,
    )
    assert created.status_code == 201
    subject = created.json()["data"]
    assert subject["code"] == "MATH"
    assert subject["name"] == "Mathematics"
    assert subject["is_active"] is True

    listed = client.get("/api/v1/subjects?active=true", headers=auth_headers)
    assert listed.status_code == 200
    assert listed.json()["data"][0]["id"] == subject["id"]

    duplicate = client.post(
        "/api/v1/subjects",
        json={"code": "MATH", "name": "Duplicate Mathematics"},
        headers=auth_headers,
    )
    assert duplicate.status_code == 409

    updated = client.put(
        f"/api/v1/subjects/{subject['id']}",
        json={"name": "Math"},
        headers=auth_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["name"] == "Math"
    fetched = client.get(f"/api/v1/subjects/{subject['id']}", headers=auth_headers)
    assert fetched.status_code == 200
    assert fetched.json()["data"]["name"] == "Math"

    deactivated = client.delete(
        f"/api/v1/subjects/{subject['id']}",
        headers=auth_headers,
    )
    assert deactivated.status_code == 200
    assert deactivated.json()["data"]["is_active"] is False

    activated = client.post(
        f"/api/v1/subjects/{subject['id']}/activate",
        headers=auth_headers,
    )
    assert activated.status_code == 200
    assert activated.json()["data"]["is_active"] is True


def test_subject_management_requires_authentication(client):
    response = client.post(
        "/api/v1/subjects",
        json={"code": "SCI", "name": "Science"},
    )
    assert response.status_code == 401


def test_subject_management_permission_is_not_granted_to_teacher_role(client, db_session):
    role = db_session.query(Role).filter(Role.code == "TEACHER").one()
    user = User(
        first_name="Subject",
        last_name="Reader",
        email="subject-reader@example.test",
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
    response = client.post(
        "/api/v1/subjects",
        json={"code": "SCI", "name": "Science"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_class_readiness_requires_class_teacher_and_active_subjects(db_session):
    school_class = _create_class(db_session)
    teacher = _create_teacher(db_session)
    subject = _create_subject(db_session)
    service = ClassService(db_session)

    readiness = service.academic_readiness(school_class.id)
    assert readiness.ready is False
    assert "No class teacher is assigned." in readiness.issues
    assert "No active subject is assigned to the class." in readiness.issues

    service.assign_class_teacher(school_class.id, teacher.id, 1, _request())
    service.assign_subject(school_class.id, subject.id, 1, _request())
    readiness = service.academic_readiness(school_class.id)
    assert readiness.ready is True
    assert readiness.active_subject_ids == [subject.id]


def test_class_teacher_is_unique_and_can_be_replaced(db_session):
    first_class = _create_class(db_session)
    second_class = _create_class(db_session, name="Grade 6")
    first_teacher = _create_teacher(db_session)
    second_teacher = _create_teacher(db_session, employee_no="EMP-SUBJECT-2")
    service = ClassService(db_session)

    service.assign_class_teacher(first_class.id, first_teacher.id, 1, _request())
    with pytest.raises(ConflictException, match="only one class"):
        service.assign_class_teacher(second_class.id, first_teacher.id, 1, _request())
    assert service.get_class(second_class.id).class_teacher_id is None

    service.assign_class_teacher(
        first_class.id,
        second_teacher.id,
        1,
        _request(),
        replace=True,
    )
    assert service.get_class(first_class.id).class_teacher_id == second_teacher.id


def test_class_subject_duplicate_and_deactivation_guards(db_session):
    school_class = _create_class(db_session)
    subject = _create_subject(db_session)
    classes = ClassService(db_session)
    classes.assign_subject(school_class.id, subject.id, 1, _request())

    with pytest.raises(ConflictException, match="already assigned"):
        classes.assign_subject(school_class.id, subject.id, 1, _request())
    with pytest.raises(BusinessRuleException, match="Remove this subject"):
        SubjectService(db_session).deactivate(subject.id, 1, _request())
    assert SubjectService(db_session).get(subject.id).is_active is True

    classes.remove_subject(school_class.id, subject.id, 1, _request())
    assert SubjectService(db_session).deactivate(subject.id, 1, _request()).is_active is False


def test_teacher_class_subject_requires_class_offering_and_prevents_duplicates(db_session):
    school_class = _create_class(db_session)
    teacher = _create_teacher(db_session)
    subject = _create_subject(db_session)
    teachers = TeacherService(db_session)
    assignment = TeacherClassSubjectAssignRequest(
        class_id=school_class.id,
        subject_id=subject.id,
    )

    with pytest.raises(BusinessRuleException, match="offering"):
        teachers.assign_class_subject(teacher.id, assignment, 1, _request())
    assert teachers.list_class_subjects(teacher.id) == []

    ClassService(db_session).assign_subject(school_class.id, subject.id, 1, _request())
    teachers.assign_class_subject(teacher.id, assignment, 1, _request())
    with pytest.raises(ConflictException, match="already assigned"):
        teachers.assign_class_subject(teacher.id, assignment, 1, _request())

    readiness = teachers.academic_readiness(teacher.id)
    assert readiness["ready"] is True
    assert readiness["assignments"][0]["subject_id"] == subject.id


def test_students_require_ready_class_and_inherit_its_active_subjects(db_session):
    school_class = _create_class(db_session)
    subject = _create_subject(db_session)
    teacher = _create_teacher(db_session)
    student = Student(
        student_code="STU-SUBJECT-1",
        first_name="Avery",
        last_name="Student",
        date_of_birth=date(2015, 5, 14),
        gender="female",
        status=StudentStatus.PROSPECTIVE.value,
    )
    db_session.add(student)
    db_session.commit()
    student_service = StudentService(db_session)
    enrollment = StudentClassAssignRequest(
        class_id=school_class.id,
        academic_year=school_class.academic_year,
    )

    with pytest.raises(BusinessRuleException, match="not ready"):
        student_service.assign_class(student.id, enrollment, 1, _request())

    classes = ClassService(db_session)
    classes.assign_class_teacher(school_class.id, teacher.id, 1, _request())
    classes.assign_subject(school_class.id, subject.id, 1, _request())
    assigned = student_service.assign_class(student.id, enrollment, 1, _request())
    assert assigned.class_id == school_class.id
    admin_user = db_session.get(User, 1)
    assert admin_user is not None
    assert [
        item.id for item in student_service.list_student_subjects(student.id, admin_user)
    ] == [subject.id]


def test_student_update_can_assign_ready_class_and_update_profile(db_session):
    school_class = _create_class(db_session)
    teacher = _create_teacher(db_session)
    subject = _create_subject(db_session)
    classes = ClassService(db_session)
    classes.assign_class_teacher(school_class.id, teacher.id, 1, _request())
    classes.assign_subject(school_class.id, subject.id, 1, _request())
    student = Student(
        student_code="STU-SUBJECT-UPDATE",
        first_name="Before",
        last_name="Update",
        date_of_birth=date(2015, 5, 14),
        gender="female",
        status=StudentStatus.PROSPECTIVE.value,
    )
    db_session.add(student)
    db_session.commit()
    service = StudentService(db_session)

    profile_updated = service.update_student(
        student.id,
        StudentUpdateRequest(first_name="After"),
        1,
        _request(),
    )
    assert profile_updated.first_name == "After"
    assert profile_updated.class_id is None

    class_updated = service.update_student(
        student.id,
        StudentUpdateRequest(current_class_id=school_class.id),
        1,
        _request(),
    )
    assert class_updated.class_id == school_class.id
    assert class_updated.current_class_id == school_class.id
    assert class_updated.academic_year == school_class.academic_year


def test_active_student_prevents_removing_class_subject(db_session):
    school_class = _create_class(db_session)
    teacher = _create_teacher(db_session)
    subject = _create_subject(db_session)
    classes = ClassService(db_session)
    classes.assign_class_teacher(school_class.id, teacher.id, 1, _request())
    classes.assign_subject(school_class.id, subject.id, 1, _request())
    db_session.add(
        Student(
            student_code="STU-SUBJECT-2",
            first_name="Jordan",
            last_name="Student",
            date_of_birth=date(2015, 5, 14),
            gender="other",
            class_id=school_class.id,
            current_class_id=school_class.id,
            academic_year=school_class.academic_year,
            status=StudentStatus.ACTIVE.value,
        )
    )
    db_session.commit()

    with pytest.raises(BusinessRuleException, match="active students"):
        classes.remove_subject(school_class.id, subject.id, 1, _request())
    assert classes.class_subjects.has_offering(school_class.id, subject.id)
