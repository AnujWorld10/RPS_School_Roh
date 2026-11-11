from datetime import date, time

from pydantic import BaseModel, Field

from app.core.responses import ResponseMeta


class UpcomingInterviewSummaryItem(BaseModel):
    """A limited, applicant-safe dashboard preview of a scheduled interview."""

    id: int = Field(..., description="Interview schedule ID.")
    inquiry_code: str = Field(..., description="Inquiry code associated with the interview.")
    student_name: str = Field(..., description="Applicant name; returned only with inquiries.read.")
    schedule_date: date = Field(..., description="School-local interview date.")
    schedule_time: time = Field(..., description="School-local interview start time.")
    location: str = Field(..., description="Interview location or meeting details.")
    mode: str = Field(..., description="Interview mode: ONLINE or OFFLINE.")


class DashboardSummaryResponse(BaseModel):
    """Permission-filtered live dashboard metrics; null fields are not authorized."""

    school_timezone: str = Field(..., description="IANA timezone used for interview scheduling.")
    student_count: int | None = Field(default=None, description="Visible student count.")
    teacher_count: int | None = Field(default=None, description="Teacher count.")
    class_count: int | None = Field(default=None, description="Non-deleted class count.")
    subject_count: int | None = Field(default=None, description="Subject catalog count.")
    inquiry_count: int | None = Field(default=None, description="Inquiry count.")
    pending_admission_count: int | None = Field(
        default=None,
        description="Applications in draft, submitted, document_pending, or document_verification.",
    )
    admissions_by_status: dict[str, int] | None = Field(
        default=None,
        description="Inquiry-linked admission application counts grouped by workflow status.",
    )
    upcoming_interview_count: int | None = Field(
        default=None,
        description="Scheduled interviews from the current school-local time onward.",
    )
    upcoming_interviews: list[UpcomingInterviewSummaryItem] | None = Field(
        default=None,
        description="Up to five upcoming interviews; included only with inquiries.read.",
    )


class DashboardSummaryEnvelope(BaseModel):
    success: bool
    message: str
    data: DashboardSummaryResponse
    meta: ResponseMeta
