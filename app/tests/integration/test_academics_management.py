from datetime import date

from sqlalchemy import select

from app.core.security import hash_password
from app.models.academics import ExaminationResult
from app.models.class_model import Class
from app.models.enums import UserStatus
from app.models.role import Role
from app.models.student import Student
from app.models.subject import ClassSubject, Subject
from app.models.teacher import Teacher
from app.models.user import User

PASSWORD = "ValidPassword@123"


def _create_student(db_session, class_record: Class, code: str, email: str) -> tuple[Student, User]:
    role = db_session.scalar(select(Role).where(Role.code == "STUDENT"))
    user = User(
        first_name="Test",
        last_name="Student",
        email=email,
        password_hash=hash_password(PASSWORD),
        status=UserStatus.ACTIVE.value,
    )
    user.roles.append(role)
    db_session.add(user)
    db_session.flush()
    student = Student(
        user_id=user.id,
        student_code=code,
        first_name=user.first_name,
        last_name=user.last_name,
        date_of_birth=date(2015, 5, 10),
        gender="other",
        email=email,
        class_id=class_record.id,
        current_class_id=class_record.id,
        academic_year=class_record.academic_year,
        roll_number=int(code[-1]),
        status="active",
    )
    db_session.add(student)
    db_session.flush()
    return student, user


def _student_headers(client, email: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": PASSWORD, "portal": "student"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def test_admin_examination_publication_correction_and_student_privacy(
    client,
    db_session,
    auth_headers,
):
    class_record = Class(
        name="Grade 8",
        section="B",
        academic_year="2026-2027",
        capacity=30,
        status="active",
    )
    subject = Subject(code="SCI-8", name="Science", category="Core")
    db_session.add_all([class_record, subject])
    db_session.flush()
    db_session.add(
        ClassSubject(
            class_id=class_record.id,
            subject_id=subject.id,
            subject_type="mandatory",
            is_active=True,
        )
    )
    first_student, first_user = _create_student(
        db_session, class_record, "RPS98001", "student.one@example.test"
    )
    second_student, _ = _create_student(
        db_session, class_record, "RPS98002", "student.two@example.test"
    )
    db_session.commit()

    created = client.post(
        "/api/v1/academics/examinations",
        headers=auth_headers,
        json={
            "name": "Term 1",
            "class_id": class_record.id,
            "examination_type": "term",
            "start_date": "2026-11-02",
            "end_date": "2026-11-13",
            "subjects": [
                {
                    "subject_id": subject.id,
                    "max_marks": 100,
                    "passing_marks": 40,
                    "components": [
                        {
                            "name": "Written",
                            "component_type": "theory",
                            "max_marks": 100,
                            "passing_marks": 40,
                        }
                    ],
                }
            ],
        },
    )
    assert created.status_code == 201
    examination = created.json()["data"]
    examination_id = examination["id"]
    component_id = examination["subjects"][0]["components"][0]["id"]

    scheduled = client.post(
        f"/api/v1/academics/examinations/{examination_id}/schedule",
        headers=auth_headers,
    )
    assert scheduled.status_code == 200
    marks = client.post(
        f"/api/v1/academics/examinations/{examination_id}/marks",
        headers=auth_headers,
        json={
            "marks": [
                {
                    "student_id": first_student.id,
                    "component_id": component_id,
                    "status": "PRESENT",
                    "obtained_marks": 84,
                },
                {
                    "student_id": second_student.id,
                    "component_id": component_id,
                    "status": "PRESENT",
                    "obtained_marks": 39,
                },
            ]
        },
    )
    assert marks.status_code == 200

    published = client.post(
        f"/api/v1/academics/examinations/{examination_id}/publish",
        headers=auth_headers,
    )
    assert published.status_code == 200
    assert published.json()["data"]["status"] == "published"
    result_rows = client.get(
        f"/api/v1/academics/examinations/{examination_id}/results",
        headers=auth_headers,
    )
    assert result_rows.status_code == 200
    results = {row["student_id"]: row for row in result_rows.json()["data"]}
    assert results[first_student.id]["percentage"] == 84
    assert results[first_student.id]["grade"] == "A+"
    assert results[first_student.id]["status"] == "PASS"
    assert results[second_student.id]["status"] == "FAIL"

    student_headers = _student_headers(client, first_user.email)
    private_results = client.get(
        "/api/v1/academics/students/me/results",
        headers=student_headers,
    )
    assert private_results.status_code == 200
    assert len(private_results.json()["data"]) == 1
    assert private_results.json()["data"][0]["examination_id"] == examination_id
    assert private_results.json()["data"][0]["marks"][0]["obtained_marks"] == 84
    assert (
        client.get(
            f"/api/v1/academics/examinations/{examination_id}/results",
            headers=student_headers,
        ).status_code
        == 403
    )

    correction = client.post(
        f"/api/v1/academics/examinations/{examination_id}/corrections",
        headers=auth_headers,
        json={
            "reason": "Verified original score entry",
            "marks": [
                {
                    "student_id": second_student.id,
                    "component_id": component_id,
                    "status": "PRESENT",
                    "obtained_marks": 45,
                }
            ],
        },
    )
    assert correction.status_code == 200
    revised_result = db_session.scalar(
        select(ExaminationResult).where(
            ExaminationResult.examination_id == examination_id,
            ExaminationResult.student_id == second_student.id,
        )
    )
    assert revised_result.percentage == 45
    assert revised_result.grade == "C"
    assert revised_result.result_status == "PASS"


def test_academic_examination_validates_configuration_and_marks(
    client,
    db_session,
    auth_headers,
):
    class_record = Class(
        name="Grade 9",
        section="A",
        academic_year="2026-2027",
        capacity=30,
        status="active",
    )
    subject = Subject(code="MATH-9", name="Mathematics")
    db_session.add_all([class_record, subject])
    db_session.flush()
    db_session.add(ClassSubject(class_id=class_record.id, subject_id=subject.id))
    student, _ = _create_student(db_session, class_record, "RPS99001", "student.nine@example.test")
    db_session.commit()

    invalid_components = client.post(
        "/api/v1/academics/examinations",
        headers=auth_headers,
        json={
            "name": "Invalid component totals",
            "class_id": class_record.id,
            "examination_type": "term",
            "start_date": "2026-12-10",
            "end_date": "2026-12-09",
            "subjects": [
                {
                    "subject_id": subject.id,
                    "max_marks": 50,
                    "passing_marks": 20,
                    "components": [
                        {
                            "name": "Written",
                            "component_type": "theory",
                            "max_marks": 100,
                            "passing_marks": 20,
                        }
                    ],
                }
            ],
        },
    )
    assert invalid_components.status_code == 422

    created = client.post(
        "/api/v1/academics/examinations",
        headers=auth_headers,
        json={
            "name": "Valid exam",
            "class_id": class_record.id,
            "examination_type": "term",
            "start_date": "2026-12-09",
            "end_date": "2026-12-10",
            "subjects": [
                {
                    "subject_id": subject.id,
                    "max_marks": 50,
                    "passing_marks": 20,
                    "components": [
                        {
                            "name": "Written",
                            "component_type": "theory",
                            "max_marks": 50,
                            "passing_marks": 20,
                        }
                    ],
                }
            ],
        },
    )
    assert created.status_code == 201
    examination_id = created.json()["data"]["id"]
    component_id = created.json()["data"]["subjects"][0]["components"][0]["id"]
    assert (
        client.post(
            f"/api/v1/academics/examinations/{examination_id}/schedule",
            headers=auth_headers,
        ).status_code
        == 200
    )

    over_max = client.post(
        f"/api/v1/academics/examinations/{examination_id}/marks",
        headers=auth_headers,
        json={
            "marks": [
                {
                    "student_id": student.id,
                    "component_id": component_id,
                    "status": "PRESENT",
                    "obtained_marks": 51,
                }
            ]
        },
    )
    assert over_max.status_code == 422

    incomplete = client.post(
        f"/api/v1/academics/examinations/{examination_id}/publish",
        headers=auth_headers,
    )
    assert incomplete.status_code == 422


def test_class_curriculum_teacher_assignment_and_student_elective_access(
    client,
    db_session,
    auth_headers,
):
    class_record = Class(
        name="Grade 7",
        section="C",
        academic_year="2026-2027",
        capacity=30,
        status="active",
    )
    mandatory = Subject(code="ENG-7", name="English", category="Languages")
    elective = Subject(code="ART-7", name="Visual Arts", category="Creative")
    inactive = Subject(
        code="OLD-7",
        name="Inactive subject",
        category="Creative",
        is_active=False,
    )
    db_session.add_all([class_record, mandatory, elective, inactive])
    db_session.flush()
    db_session.add_all(
        [
            ClassSubject(class_id=class_record.id, subject_id=mandatory.id),
            ClassSubject(
                class_id=class_record.id,
                subject_id=inactive.id,
                subject_type="elective",
            ),
        ]
    )
    teacher = Teacher(
        employee_no="EMP-ACADEMIC-7",
        first_name="Curriculum",
        last_name="Teacher",
        email="curriculum.teacher@example.test",
        status="active",
    )
    db_session.add(teacher)
    student, student_user = _create_student(
        db_session, class_record, "RPS97001", "student.elective@example.test"
    )
    db_session.commit()

    configure = client.put(
        f"/api/v1/academics/classes/{class_record.id}/subjects/{elective.id}",
        headers=auth_headers,
        json={"subject_type": "elective", "stream": "Creative Arts", "is_active": True},
    )
    assert configure.status_code == 200
    assign_teacher = client.put(
        f"/api/v1/academics/classes/{class_record.id}/subjects/{elective.id}/teacher",
        headers=auth_headers,
        params={"teacher_id": teacher.id},
    )
    assert assign_teacher.status_code == 200

    curriculum = client.get(
        f"/api/v1/academics/classes/{class_record.id}/subjects",
        headers=auth_headers,
    )
    assert curriculum.status_code == 200
    offerings = {item["subject_id"]: item for item in curriculum.json()["data"]}
    assert offerings[mandatory.id]["subject_type"] == "mandatory"
    assert offerings[elective.id]["stream"] == "Creative Arts"
    assert offerings[elective.id]["teacher_id"] == teacher.id

    selection = client.put(
        f"/api/v1/academics/students/{student.id}/electives",
        headers=auth_headers,
        json=[inactive.id],
    )
    assert selection.status_code == 422
    selection = client.put(
        f"/api/v1/academics/students/{student.id}/electives",
        headers=auth_headers,
        json=[elective.id],
    )
    assert selection.status_code == 200
    student_headers = _student_headers(client, student_user.email)
    student_subjects = client.get(
        "/api/v1/academics/students/me/subjects",
        headers=student_headers,
    )
    assert student_subjects.status_code == 200
    subjects = {item["subject_id"]: item for item in student_subjects.json()["data"]}
    assert subjects[mandatory.id]["selected"] is True
    assert subjects[elective.id]["selected"] is True


def test_teacher_cannot_manage_academic_configuration(client, db_session):
    teacher_role = db_session.scalar(select(Role).where(Role.code == "TEACHER"))
    teacher_user = User(
        first_name="Academic",
        last_name="Teacher",
        email="academic.teacher@example.test",
        password_hash=hash_password(PASSWORD),
        status=UserStatus.ACTIVE.value,
    )
    teacher_user.roles.append(teacher_role)
    db_session.add(teacher_user)
    db_session.commit()
    login = client.post(
        "/api/v1/auth/login",
        json={"email": teacher_user.email, "password": PASSWORD, "portal": "teacher"},
    )
    assert login.status_code == 200
    teacher_headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

    response = client.get(
        "/api/v1/academics/classes/1/subjects",
        headers=teacher_headers,
    )
    assert response.status_code == 403
