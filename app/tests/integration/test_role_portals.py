from datetime import date

from sqlalchemy import select

from app.core.security import hash_password
from app.models.audit_log import AuditLog
from app.models.class_model import Class
from app.models.enums import UserStatus
from app.models.role import Role
from app.models.role_portal import Assessment, AssessmentResult, SchoolEvent
from app.models.student import Student
from app.models.student_inquiry import StudentInquiry
from app.models.subject import ClassSubject, Subject, TeacherClassSubject
from app.models.teacher import Teacher
from app.models.user import User


PASSWORD = "ValidPassword@123"


def _create_user(db_session, role_code: str, email: str, phone: str | None = None) -> User:
    role = db_session.scalar(select(Role).where(Role.code == role_code))
    user = User(
        first_name=role_code.title(),
        last_name="Portal",
        email=email,
        phone=phone,
        password_hash=hash_password(PASSWORD),
        status=UserStatus.ACTIVE.value,
    )
    user.roles.append(role)
    db_session.add(user)
    db_session.flush()
    return user


def _login(
    client,
    email: str,
    portal: str,
    password: str = PASSWORD,
) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "portal": portal},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def _school_records(db_session):
    class_record = Class(
        name="Role Portal Grade",
        section="A",
        academic_year="2025-26",
        capacity=30,
        status="active",
    )
    subject = Subject(code="ROLEPORTAL", name="Role Portal Subject", is_active=True)
    db_session.add_all([class_record, subject])
    db_session.flush()
    db_session.add(ClassSubject(class_id=class_record.id, subject_id=subject.id))
    teacher_user = _create_user(db_session, "TEACHER", "teacher-portal@example.test")
    teacher = Teacher(
        user_id=teacher_user.id,
        employee_no="RP-TEACHER-1",
        first_name="Teacher",
        last_name="Portal",
        email="teacher-portal@example.test",
        status="active",
    )
    db_session.add(teacher)
    db_session.flush()
    db_session.add(
        TeacherClassSubject(
            teacher_id=teacher.id,
            class_id=class_record.id,
            subject_id=subject.id,
        )
    )
    db_session.flush()
    return class_record, subject, teacher_user, teacher


def _student(db_session, *, email: str, class_id: int, code: str):
    student = Student(
        student_code=code,
        first_name="Test",
        last_name="Student",
        date_of_birth=date(2015, 1, 1),
        gender="other",
        email=email,
        class_id=class_id,
        current_class_id=class_id,
        academic_year="2025-26",
        roll_number=int(code[-1]),
        status="active",
    )
    db_session.add(student)
    db_session.flush()
    return student


def test_teacher_assignment_assessment_and_timetable_are_scoped_and_audited(
    client,
    db_session,
):
    class_record, subject, teacher_user, teacher = _school_records(db_session)
    student_user = _create_user(db_session, "STUDENT", "student-portal@example.test")
    student = _student(
        db_session,
        email=student_user.email,
        class_id=class_record.id,
        code="RPSTU1",
    )
    other_student = _student(
        db_session,
        email="other-student@example.test",
        class_id=class_record.id,
        code="RPSTU2",
    )
    db_session.commit()
    teacher_headers = _login(client, teacher_user.email, "teacher")
    student_headers = _login(client, student_user.email, "student")

    assignment_response = client.post(
        "/api/v1/assignments",
        headers=teacher_headers,
        json={
            "title": "Fractions",
            "details": "Complete exercises 1-5.",
            "class_id": class_record.id,
            "subject_id": subject.id,
            "due_date": "2026-12-01",
        },
    )
    assert assignment_response.status_code == 201
    assignment_id = assignment_response.json()["data"]["id"]
    assert assignment_response.json()["data"]["assigned_teacher_id"] == teacher.id
    assert client.get("/api/v1/assignments", headers=student_headers).json()["data"] == []

    publish = client.post(
        f"/api/v1/assignments/{assignment_id}/publish",
        headers=teacher_headers,
    )
    assert publish.status_code == 200
    assignments = client.get("/api/v1/assignments", headers=student_headers)
    assert [item["id"] for item in assignments.json()["data"]] == [assignment_id]

    timetable = client.post(
        "/api/v1/timetable",
        headers=teacher_headers,
        json={
            "class_id": class_record.id,
            "subject_id": subject.id,
            "day_of_week": 1,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "academic_year": "2025-26",
        },
    )
    assert timetable.status_code == 201
    conflict = client.post(
        "/api/v1/timetable",
        headers=teacher_headers,
        json={
            "class_id": class_record.id,
            "subject_id": subject.id,
            "day_of_week": 1,
            "start_time": "09:30:00",
            "end_time": "10:30:00",
            "academic_year": "2025-26",
        },
    )
    assert conflict.status_code == 409

    assessment = client.post(
        "/api/v1/assessments",
        headers=teacher_headers,
        json={
            "name": "Unit Test 1",
            "assessment_type": "unit_test",
            "class_id": class_record.id,
            "subject_id": subject.id,
            "assessment_date": "2026-11-20",
            "max_score": 20,
        },
    )
    assert assessment.status_code == 201
    assessment_id = assessment.json()["data"]["id"]
    too_high = client.put(
        f"/api/v1/assessments/{assessment_id}/results/{student.id}",
        headers=teacher_headers,
        json={"score": 21},
    )
    assert too_high.status_code == 422
    absent = client.put(
        f"/api/v1/assessments/{assessment_id}/results/{other_student.id}",
        headers=teacher_headers,
        json={"result_status": "absent"},
    )
    assert absent.status_code == 200
    scored = client.put(
        f"/api/v1/assessments/{assessment_id}/results/{student.id}",
        headers=teacher_headers,
        json={"score": 18, "result_status": "present"},
    )
    assert scored.status_code == 200
    revised_score = client.put(
        f"/api/v1/assessments/{assessment_id}/results/{student.id}",
        headers=teacher_headers,
        json={"score": 17, "result_status": "present"},
    )
    assert revised_score.status_code == 200
    assert client.post(
        f"/api/v1/assessments/{assessment_id}/publish",
        headers=teacher_headers,
    ).status_code == 200
    visible_assessment = client.get(
        f"/api/v1/assessments/{assessment_id}",
        headers=student_headers,
    ).json()["data"]
    assert [item["student_id"] for item in visible_assessment["results"]] == [student.id]

    audit_actions = set(
        db_session.scalars(
            select(AuditLog.action).where(
                AuditLog.actor_user_id == teacher_user.id,
            )
        ).all()
    )
    assert {
        "assignment.create",
        "assignment.published",
        "timetable.create",
        "assessment.create",
        "assessment.result.upsert",
        "assessment.publish",
    }.issubset(audit_actions)
    assert db_session.scalar(
        select(AssessmentResult).where(
            AssessmentResult.assessment_id == assessment_id,
            AssessmentResult.student_id == student.id,
        )
    ).updated_at is not None


def test_parent_scope_and_teacher_event_review(client, db_session):
    class_record, subject, teacher_user, _teacher_record = _school_records(db_session)
    parent_email = "parent-portal@example.test"
    parent_phone = "555-0101"
    parent_user = _create_user(
        db_session,
        "PARENT",
        parent_email,
        phone=parent_phone,
    )
    inquiry = StudentInquiry(
        inquiry_code="INQROLEPORTAL01",
        serial_number=90001,
        duplicate_key=None,
        first_name="Linked",
        last_name="Child",
        gender="other",
        father_name="Guardian",
        date_of_birth=date(2015, 1, 1),
        parent_mobile=parent_phone,
        email=parent_email,
        address="School Road",
        last_school="Previous School",
        current_class="Grade 4",
        admission_for_class="Grade 5",
        status="PENDING",
    )
    db_session.add(inquiry)
    db_session.flush()
    child = Student(
        student_code="RPCHILD1",
        inquiry_id=inquiry.id,
        first_name="Linked",
        last_name="Child",
        date_of_birth=date(2015, 1, 1),
        gender="other",
        class_id=class_record.id,
        current_class_id=class_record.id,
        status="active",
    )
    db_session.add(child)
    other_class = Class(
        name="Unlinked Grade",
        section="B",
        academic_year="2025-26",
        capacity=30,
        status="active",
    )
    db_session.add(other_class)
    db_session.flush()
    db_session.add(ClassSubject(class_id=other_class.id, subject_id=subject.id))
    db_session.flush()
    from app.models.subject import TeacherClassSubject

    db_session.add(
        TeacherClassSubject(
            teacher_id=_teacher_record.id,
            class_id=other_class.id,
            subject_id=subject.id,
        )
    )
    db_session.commit()

    teacher_headers = _login(client, teacher_user.email, "teacher")
    parent_headers = _login(client, parent_user.email, "parent")
    linked_assignment = client.post(
        "/api/v1/assignments",
        headers=teacher_headers,
        json={
            "title": "Linked homework",
            "details": "For the linked child class.",
            "class_id": class_record.id,
            "subject_id": subject.id,
            "due_date": "2026-12-01",
        },
    )
    unrelated_assignment = client.post(
        "/api/v1/assignments",
        headers=teacher_headers,
        json={
            "title": "Other class homework",
            "details": "Must not appear for this parent.",
            "class_id": other_class.id,
            "subject_id": subject.id,
            "due_date": "2026-12-01",
        },
    )
    assert linked_assignment.status_code == unrelated_assignment.status_code == 201
    for assignment_id in (
        linked_assignment.json()["data"]["id"],
        unrelated_assignment.json()["data"]["id"],
    ):
        assert client.post(
            f"/api/v1/assignments/{assignment_id}/publish",
            headers=teacher_headers,
        ).status_code == 200
    parent_assignments = client.get("/api/v1/assignments", headers=parent_headers)
    assert [
        item["id"] for item in parent_assignments.json()["data"]
    ] == [linked_assignment.json()["data"]["id"]]

    event = client.post(
        "/api/v1/events",
        headers=teacher_headers,
        json={
            "title": "School Open Day",
            "description": "Meet the school community.",
            "starts_at": "2026-12-01T09:00:00+05:30",
            "ends_at": "2026-12-01T12:00:00+05:30",
            "audience": "public",
        },
    )
    assert event.status_code == 201
    event_id = event.json()["data"]["id"]
    assert event.json()["data"]["status"] == "pending_review"
    assert client.get("/api/v1/public/events").json()["data"] == []

    admin_headers = _login(
        client,
        "test-admin@school.com",
        "administration",
        password="TestAdmin@123",
    )
    review = client.post(
        f"/api/v1/events/{event_id}/review",
        headers=admin_headers,
        json={"status": "published"},
    )
    assert review.status_code == 200
    assert review.json()["data"]["reviewed_by"] is not None
    assert [item["id"] for item in client.get("/api/v1/public/events").json()["data"]] == [
        event_id
    ]

    assignments = client.get("/api/v1/assignments", headers=parent_headers)
    assert assignments.status_code == 200
    assert db_session.scalar(select(SchoolEvent).where(SchoolEvent.id == event_id)).status == "published"
    audit = db_session.scalar(
        select(AuditLog).where(
            AuditLog.entity_type == "school_event",
            AuditLog.entity_id == event_id,
            AuditLog.action == "event.published",
        )
    )
    assert audit is not None
    assert audit.actor_user_id is not None
    assert audit.old_values == {"status": "pending_review"}
    assert audit.new_values["status"] == "published"


def test_role_specific_login_rejects_mismatched_portal(client, db_session):
    _create_user(db_session, "STUDENT", "portal-mismatch@example.test")
    db_session.commit()
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "portal-mismatch@example.test",
            "password": PASSWORD,
            "portal": "administration",
        },
    )
    assert response.status_code == 401
