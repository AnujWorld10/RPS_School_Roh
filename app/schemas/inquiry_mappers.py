"""Map ORM inquiry entities to public and staff API response schemas."""

from app.models.enums import REQUIRED_ADMISSION_DOCUMENTS
from app.models.student_inquiry import StudentInquiry
from app.schemas.inquiries import (
    InquiryStatusHistoryResponse,
    PublicAdmissionDocumentSummary,
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
        student = inquiry.admission.student
        school_class = inquiry.admission.school_class
        admission_summary = PublicAdmissionSummary(
            admission_code=inquiry.admission.admission_code,
            status=inquiry.admission.status,
            documents_uploaded=len(inquiry.admission.documents),
            documents_required=len(REQUIRED_ADMISSION_DOCUMENTS),
            documents=[
                PublicAdmissionDocumentSummary(
                    document_type=document.document_type,
                    verification_status=document.verification_status,
                    rejection_reason=document.rejection_reason,
                )
                for document in inquiry.admission.documents
            ],
            student_code=student.student_code if student else None,
            student_name=(
                " ".join(
                    part
                    for part in (
                        inquiry.first_name,
                        inquiry.middle_name,
                        inquiry.last_name,
                    )
                    if part
                )
                if student
                else None
            ),
            class_name=school_class.name if student and school_class else None,
            section=inquiry.admission.section if student else None,
            academic_year=inquiry.admission.academic_year if student else None,
            roll_number=student.roll_number if student else None,
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
