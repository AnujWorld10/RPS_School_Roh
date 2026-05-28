"""Map ORM inquiry entities to public and staff API response schemas."""

from app.models.enums import REQUIRED_ADMISSION_DOCUMENTS
from app.models.student_inquiry import StudentInquiry
from app.schemas.inquiries import (
    InquiryStatusHistoryResponse,
    PublicAdmissionSummary,
    PublicInquiryStatusResponse,
    PublicInterviewSummary,
    StudentInquiryResponse,
)
from app.schemas.interviews import InterviewResponse


def to_public_status_response(inquiry: StudentInquiry) -> PublicInquiryStatusResponse:
    """Build parent-facing status payload (excludes internal_notes and internal id)."""
    timeline = [
        InquiryStatusHistoryResponse.model_validate(row) for row in inquiry.status_history
    ]
    latest_interview = None
    if inquiry.interviews:
        latest = sorted(
            inquiry.interviews,
            key=lambda i: (i.schedule_date, i.schedule_time),
            reverse=True,
        )[0]
        latest_interview = PublicInterviewSummary(
            schedule_date=latest.schedule_date,
            schedule_time=latest.schedule_time,
            location=latest.location,
            mode=latest.mode,
            result=latest.result,
        )
    admission_summary = None
    if inquiry.admission:
        admission_summary = PublicAdmissionSummary(
            admission_code=inquiry.admission.admission_code,
            status=inquiry.admission.status,
            documents_uploaded=len(inquiry.admission.documents),
            documents_required=len(REQUIRED_ADMISSION_DOCUMENTS),
        )
    return PublicInquiryStatusResponse(
        inquiry_code=inquiry.inquiry_code,
        status=inquiry.status,
        rejection_reason=inquiry.rejection_reason,
        admission_for_class=inquiry.admission_for_class,
        created_at=inquiry.created_at,
        updated_at=inquiry.updated_at,
        status_timeline=timeline,
        latest_interview=latest_interview,
        admission=admission_summary,
    )


def to_staff_inquiry_response(inquiry: StudentInquiry) -> dict:
    """Serialize full inquiry for authenticated staff endpoints."""
    timeline = [
        InquiryStatusHistoryResponse.model_validate(row)
        for row in getattr(inquiry, "status_history", [])
    ]
    payload = StudentInquiryResponse.model_validate(inquiry).model_dump()
    payload["status_timeline"] = [item.model_dump() for item in timeline]
    if getattr(inquiry, "interviews", None):
        payload["interviews"] = [
            InterviewResponse.model_validate(i).model_dump() for i in inquiry.interviews
        ]
    return payload
