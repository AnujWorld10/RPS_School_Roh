from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.pagination import PaginationParams
from app.models.admission import InquiryAdmission
from app.models.enums import AdmissionStatus, InquiryStatus, InterviewResult
from app.models.interview import InterviewSchedule
from app.models.student_inquiry import StudentInquiry
from app.models.user import User
from app.schemas.dashboard import DashboardSummaryResponse, UpcomingInterviewSummaryItem
from app.services.classes import ClassService
from app.services.inquiries import InquiryService
from app.services.students import StudentService
from app.services.subjects import SubjectService
from app.services.teachers import TeacherService

PENDING_ADMISSION_STATUSES = (
    AdmissionStatus.DRAFT.value,
    AdmissionStatus.SUBMITTED.value,
    AdmissionStatus.DOCUMENT_PENDING.value,
    AdmissionStatus.DOCUMENT_VERIFICATION.value,
)


class DashboardService:
    """Build read-only dashboard metrics from existing authorized school data."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()

    def get_summary(self, user: User) -> DashboardSummaryResponse:
        permissions = {
            permission.code
            for role in user.roles
            if role.is_active
            for permission in role.permissions
        }
        response = DashboardSummaryResponse(school_timezone=self.settings.school_timezone)
        params = PaginationParams(page=1, limit=1, sort_by="id", sort_order="desc")

        if "students.read" in permissions:
            response.student_count = StudentService(self.session).list_students(params, user).total
        if "teachers.read" in permissions:
            response.teacher_count = TeacherService(self.session).list_teachers(params).total
        if "classes.read" in permissions:
            response.class_count = ClassService(self.session).list_classes(params).total
        if "subjects.read" in permissions:
            response.subject_count = SubjectService(self.session).list(params).total
        if "inquiries.read" in permissions:
            response.inquiry_count = InquiryService(self.session).list_inquiries(params).total
        if "admissions.read" in permissions:
            response.admissions_by_status = self._admission_counts()
            response.pending_admission_count = sum(
                response.admissions_by_status[status] for status in PENDING_ADMISSION_STATUSES
            )
        if "interviews.read" in permissions:
            response.upcoming_interview_count, upcoming = self._upcoming_interviews()
            if "inquiries.read" in permissions:
                response.upcoming_interviews = upcoming

        return response

    def _admission_counts(self) -> dict[str, int]:
        counts = {status.value: 0 for status in AdmissionStatus}
        rows = self.session.execute(
            select(InquiryAdmission.status, func.count(InquiryAdmission.id)).group_by(
                InquiryAdmission.status
            )
        )
        for status, count in rows:
            if status in counts:
                counts[status] = count
        return counts

    def _upcoming_interviews(self) -> tuple[int, list[UpcomingInterviewSummaryItem]]:
        now = datetime.now(ZoneInfo(self.settings.school_timezone))
        local_time = now.time().replace(tzinfo=None)
        schedule_filters = (
            InterviewSchedule.result == InterviewResult.SCHEDULED.value,
            StudentInquiry.status == InquiryStatus.INTERVIEW_SCHEDULED.value,
            or_(
                InterviewSchedule.schedule_date > now.date(),
                and_(
                    InterviewSchedule.schedule_date == now.date(),
                    InterviewSchedule.schedule_time >= local_time,
                ),
            ),
        )
        base_query = (
            select(InterviewSchedule)
            .join(StudentInquiry, StudentInquiry.id == InterviewSchedule.inquiry_id)
            .where(*schedule_filters)
        )
        count = self.session.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        rows = self.session.execute(
            select(
                InterviewSchedule.id,
                StudentInquiry.inquiry_code,
                StudentInquiry.first_name,
                StudentInquiry.last_name,
                InterviewSchedule.schedule_date,
                InterviewSchedule.schedule_time,
                InterviewSchedule.location,
                InterviewSchedule.mode,
            )
            .join(StudentInquiry, StudentInquiry.id == InterviewSchedule.inquiry_id)
            .where(*schedule_filters)
            .order_by(
                InterviewSchedule.schedule_date,
                InterviewSchedule.schedule_time,
                InterviewSchedule.id,
            )
            .limit(5)
        )
        upcoming = [
            UpcomingInterviewSummaryItem(
                id=row.id,
                inquiry_code=row.inquiry_code,
                student_name=f"{row.first_name} {row.last_name}".strip(),
                schedule_date=row.schedule_date,
                schedule_time=row.schedule_time,
                location=row.location,
                mode=row.mode,
            )
            for row in rows
        ]
        return count, upcoming
