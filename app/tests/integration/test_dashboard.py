from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.core.config import get_settings
from app.models.admission import InquiryAdmission
from app.models.enums import AdmissionStatus, InquiryStatus, InterviewResult
from app.models.interview import InterviewSchedule
from app.models.student import Student
from app.models.student_inquiry import StudentInquiry


def create_inquiry(client, db_session, name: str) -> StudentInquiry:
    payload = {
        "first_name": name,
        "last_name": "Dashboard",
        "gender": "female",
        "father_name": f"Parent {name}",
        "dob": "2017-01-02",
        "parent_mobile": f"+9198765432{len(name):02d}",
        "email": f"{name.lower()}@example.com",
        "address": "1 School Road",
        "last_school": "Previous School",
        "current_class": "Grade 3",
        "admission_for_class": "Grade 4",
    }
    response = client.post("/api/v1/public/student/inquiry", json=payload)
    assert response.status_code == 201
    inquiry = (
        db_session.query(StudentInquiry)
        .filter_by(inquiry_code=response.json()["data"]["inquiry_code"])
        .one()
    )
    return inquiry


def test_dashboard_summary_returns_live_status_counts_and_timezone_aware_upcoming_interviews(
    client,
    db_session,
    auth_headers,
):
    for index, admission_status in enumerate(AdmissionStatus):
        inquiry = create_inquiry(client, db_session, f"Applicant{index}")
        db_session.add(
            InquiryAdmission(
                admission_code=f"ADM2026{index:05d}",
                inquiry_id=inquiry.id,
                class_id=1,
                academic_year="2026-2027",
                status=admission_status.value,
            )
        )

    timezone = ZoneInfo(get_settings().school_timezone)
    today = datetime.now(timezone).date()
    upcoming_inquiry = create_inquiry(client, db_session, "FutureInterview")
    upcoming_inquiry.status = InquiryStatus.INTERVIEW_SCHEDULED.value
    db_session.add(
        InterviewSchedule(
            inquiry_id=upcoming_inquiry.id,
            schedule_date=today + timedelta(days=1),
            schedule_time=time(10, 30),
            location="Room 101",
            mode="OFFLINE",
            result=InterviewResult.SCHEDULED.value,
        )
    )
    past_inquiry = create_inquiry(client, db_session, "PastInterview")
    past_inquiry.status = InquiryStatus.INTERVIEW_SCHEDULED.value
    db_session.add(
        InterviewSchedule(
            inquiry_id=past_inquiry.id,
            schedule_date=today - timedelta(days=1),
            schedule_time=time(10, 30),
            location="Room 102",
            mode="ONLINE",
            result=InterviewResult.SCHEDULED.value,
        )
    )
    db_session.flush()

    response = client.get("/api/v1/dashboard/summary", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    summary = body["data"]
    assert summary["school_timezone"] == get_settings().school_timezone
    assert summary["inquiry_count"] == len(AdmissionStatus) + 2
    assert summary["pending_admission_count"] == 4
    assert summary["admissions_by_status"] == {status.value: 1 for status in AdmissionStatus}
    assert summary["upcoming_interview_count"] == 1
    assert len(summary["upcoming_interviews"]) == 1
    assert summary["upcoming_interviews"][0]["inquiry_code"] == upcoming_inquiry.inquiry_code
    assert summary["upcoming_interviews"][0]["student_name"] == "FutureInterview Dashboard"


def test_dashboard_summary_omits_metrics_and_applicant_details_without_permissions(
    client,
    db_session,
    auth_headers,
):
    own_email = "limited-student@example.com"
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": own_email,
            "password": "StudentPass@123",
            "first_name": "Limited",
            "last_name": "Student",
            "role_codes": ["STUDENT"],
        },
        headers=auth_headers,
    )
    assert register.status_code == 201
    login = client.post(
        "/api/v1/auth/login",
        json={"email": own_email, "password": "StudentPass@123"},
    )
    assert login.status_code == 200
    student_headers = {
        "Authorization": f"Bearer {login.json()['data']['access_token']}",
    }
    db_session.add_all(
        [
            Student(
                student_code="STU202600001",
                first_name="Owned",
                last_name="Student",
                date_of_birth=date(2016, 1, 1),
                gender="female",
                email=own_email,
                status="active",
            ),
            Student(
                student_code="STU202600002",
                first_name="Other",
                last_name="Student",
                date_of_birth=date(2016, 1, 1),
                gender="male",
                email="another-student@example.com",
                status="active",
            ),
        ]
    )
    db_session.flush()

    response = client.get("/api/v1/dashboard/summary", headers=student_headers)

    assert response.status_code == 200
    summary = response.json()["data"]
    assert summary["student_count"] == 1
    assert summary["teacher_count"] is None
    assert summary["class_count"] is None
    assert summary["inquiry_count"] is None
    assert summary["pending_admission_count"] is None
    assert summary["upcoming_interview_count"] is None
    assert summary["upcoming_interviews"] is None


def test_dashboard_summary_requires_at_least_one_relevant_read_permission(client):
    response = client.get("/api/v1/dashboard/summary")

    assert response.status_code in (401, 403)
