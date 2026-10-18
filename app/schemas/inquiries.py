"""
Pydantic schemas for student inquiry public and admin APIs.
"""

from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.enums import Gender, InquiryStatus
from app.schemas.common import ORMModel


class PublicInquiryCreateRequest(BaseModel):
    """Request body for POST /api/v1/public/student/inquiry."""

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Applicant student's given name.",
    )
    middle_name: str | None = Field(
        default=None, max_length=100, description="Optional middle name."
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Applicant student's family name.",
    )
    gender: Gender = Field(..., description="Student gender: male, female, or other.")
    father_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Father's or legal guardian's full name.",
    )
    dob: date = Field(
        ...,
        description="Student date of birth (YYYY-MM-DD); cannot be in the future.",
        examples=["2018-04-12"],
    )
    student_mobile: str | None = Field(
        default=None,
        max_length=30,
        description="Optional student contact number.",
    )
    parent_mobile: str = Field(
        ...,
        min_length=5,
        max_length=30,
        description="Parent or guardian phone; also used to verify status lookups.",
    )
    email: EmailStr = Field(
        ...,
        description="Parent or guardian email; also used to verify status lookups.",
    )
    address: str = Field(
        ...,
        min_length=5,
        description="Applicant's residential address.",
    )
    last_school: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the school most recently attended.",
    )
    current_class: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Class or grade currently attended.",
    )
    admission_for_class: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Class or grade requested for admission.",
    )
    last_school_percentage: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Most recent school percentage, from 0 to 100.",
        examples=["87.50"],
    )
    admission_for_class_id: int | None = Field(
        default=None,
        gt=0,
        description="Optional catalog class ID when known; must identify an active class.",
        examples=[1],
    )

    @field_validator(
        "first_name",
        "middle_name",
        "last_name",
        "father_name",
        "student_mobile",
        "parent_mobile",
        "address",
        "last_school",
        "current_class",
        "admission_for_class",
        mode="before",
    )
    @classmethod
    def strip_strings(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("dob")
    @classmethod
    def dob_must_not_be_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return value


class PublicInquiryUpdateRequest(BaseModel):
    """
    Request body for PUT /api/v1/public/student/inquiry/update.

    Parent must prove ownership via inquiry_code + email + parent_mobile.
    """

    inquiry_code: str = Field(
        ...,
        min_length=5,
        max_length=20,
        description="Inquiry tracking code returned at submission.",
        examples=["INQ202600007"],
    )
    email: EmailStr = Field(
        ...,
        description="Email submitted with this inquiry, used to verify ownership.",
    )
    parent_mobile: str = Field(
        ...,
        min_length=5,
        max_length=30,
        description="Parent/guardian mobile submitted with this inquiry, used to verify ownership.",
    )
    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated student given name.",
    )
    middle_name: str | None = Field(
        default=None, max_length=100, description="Updated student middle name."
    )
    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated student family name.",
    )
    gender: Gender | None = Field(
        default=None, description="Updated gender: male, female, or other."
    )
    father_name: str | None = Field(
        default=None,
        max_length=200,
        description="Updated father or legal guardian name.",
    )
    dob: date | None = Field(
        default=None, description="Updated date of birth (YYYY-MM-DD).", examples=["2018-04-12"]
    )
    student_mobile: str | None = Field(
        default=None,
        max_length=30,
        description="Updated student contact number.",
    )
    address: str | None = Field(default=None, description="Updated residential address.")
    last_school: str | None = Field(
        default=None,
        max_length=255,
        description="Updated last school name.",
    )
    current_class: str | None = Field(
        default=None,
        max_length=100,
        description="Updated current class or grade.",
    )
    admission_for_class: str | None = Field(
        default=None,
        max_length=100,
        description="Updated requested class or grade.",
    )
    last_school_percentage: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Updated last-school percentage, from 0 to 100.",
        examples=["87.50"],
    )

    @field_validator("inquiry_code", "parent_mobile", mode="before")
    @classmethod
    def strip_required(cls, value: str) -> str:
        return value.strip().upper() if isinstance(value, str) else value


class InquiryStatusHistoryResponse(ORMModel):
    """One row from inquiry_status_history exposed on status APIs."""

    id: int = Field(..., description="Status-history record ID.")
    from_status: str | None = Field(
        ..., description="Previous status, or null for initial submission."
    )
    to_status: str = Field(..., description="New inquiry status in the admission workflow.")
    change_reason: str | None = Field(
        ...,
        description="Reason recorded for the transition, if any.",
    )
    created_at: datetime = Field(..., description="Timestamp when the status changed.")


class PublicInquiryCreateResponse(BaseModel):
    """Minimal response after successful public inquiry submission."""

    inquiry_code: str = Field(
        ...,
        description="Public tracking code to save and use for status checks.",
        examples=["INQ202600007"],
    )
    status: str = Field(..., description="Initial inquiry status.")
    message: str = Field(
        default="Inquiry submitted successfully. Please save your inquiry ID for tracking.",
        description="Submission confirmation.",
    )


class PublicInterviewSummary(BaseModel):
    """Interview slot shown on public status page."""

    schedule_date: date = Field(
        ..., description="Scheduled interview date.", examples=["2026-11-05"]
    )
    schedule_time: time = Field(
        ..., description="Scheduled interview start time.", examples=["10:30"]
    )
    location: str = Field(..., description="Interview location or meeting details.")
    mode: str = Field(..., description="Interview mode: ONLINE or OFFLINE.")
    result: str = Field(
        ...,
        description="Interview outcome: SCHEDULED, PASSED, FAILED, or ABSENT.",
    )


class PublicAdmissionSummary(BaseModel):
    """Admission progress shown on public status page."""

    admission_code: str | None = Field(
        default=None,
        description="Admission tracking code, if an application exists.",
        examples=["ADM202600055"],
    )
    status: str | None = Field(
        default=None,
        description="Admission workflow status, if an application exists.",
    )
    documents_uploaded: int = Field(
        default=0, description="Number of admission documents uploaded."
    )
    documents_required: int = Field(
        default=6, description="Number of required admission documents."
    )


class PublicInquiryStatusResponse(BaseModel):
    """Parent-facing inquiry status (no internal staff notes)."""

    inquiry_code: str = Field(
        ..., description="Public inquiry tracking code.", examples=["INQ202600007"]
    )
    status: str = Field(..., description="Current admission inquiry status.")
    rejection_reason: str | None = Field(
        default=None,
        description="Parent-visible reason when the inquiry is rejected.",
    )
    admission_for_class: str = Field(..., description="Class or grade requested by the applicant.")
    created_at: datetime = Field(..., description="Inquiry submission timestamp.")
    updated_at: datetime | None = Field(
        default=None,
        description="Most recent inquiry update timestamp.",
    )
    status_timeline: list[InquiryStatusHistoryResponse] = Field(
        default_factory=list,
        description="Status changes in chronological order, oldest first.",
    )
    latest_interview: PublicInterviewSummary | None = Field(
        default=None, description="Latest scheduled interview, if one exists."
    )
    admission: PublicAdmissionSummary | None = Field(
        default=None, description="Admission application progress, if one exists."
    )


class StudentInquiryResponse(ORMModel):
    """Full inquiry record for authenticated staff APIs."""

    id: int = Field(..., description="Internal inquiry record ID.")
    inquiry_code: str = Field(
        ..., description="Public inquiry tracking code.", examples=["INQ202600007"]
    )
    status_timeline: list[InquiryStatusHistoryResponse] = Field(
        default_factory=list, description="Chronological status change history."
    )
    serial_number: int = Field(
        ...,
        description="Monotonic internal sequence used to generate the inquiry code.",
    )
    first_name: str = Field(..., description="Student's given name.")
    middle_name: str | None = Field(..., description="Student's middle name, if provided.")
    last_name: str = Field(..., description="Student's family name.")
    gender: str = Field(..., description="Student gender: male, female, or other.")
    father_name: str = Field(..., description="Father or legal guardian name.")
    date_of_birth: date = Field(..., description="Student date of birth.", examples=["2018-04-12"])
    student_mobile: str | None = Field(..., description="Student contact number, if provided.")
    parent_mobile: str = Field(..., description="Parent/guardian phone number.")
    email: str = Field(..., description="Parent/guardian email address.")
    address: str = Field(..., description="Applicant's residential address.")
    last_school: str = Field(..., description="Most recently attended school.")
    current_class: str = Field(..., description="Class currently attended.")
    admission_for_class: str = Field(..., description="Class requested for admission.")
    last_school_percentage: Decimal | None = Field(
        ..., description="Most recent school percentage, if provided.", examples=["87.50"]
    )
    admission_for_class_id: int | None = Field(
        ..., description="Mapped catalog class ID, if selected.", examples=[1]
    )
    status: str = Field(..., description="Current inquiry workflow status.")
    rejection_reason: str | None = Field(
        default=None,
        description="Rejection reason, if rejected.",
    )
    internal_notes: str | None = Field(
        default=None,
        description="Staff-only notes; not exposed by the public status API.",
    )
    created_at: datetime = Field(..., description="Inquiry creation timestamp.")
    updated_at: datetime | None = Field(default=None, description="Most recent update timestamp.")


class AdminInquiryUpdateRequest(BaseModel):
    """Staff-only field updates (including internal notes and class mapping)."""

    admission_for_class_id: int | None = Field(
        default=None,
        gt=0,
        description="Catalog class ID to associate with this inquiry.",
        examples=[1],
    )
    internal_notes: str | None = Field(
        default=None,
        description="Staff-only notes; not visible in parent status responses.",
    )


class InquiryReviewActionRequest(BaseModel):
    """Body for admin review transition endpoints."""

    notes: str | None = Field(
        default=None,
        description="Optional staff note recorded with the status transition.",
    )


class InquiryRejectRequest(BaseModel):
    """Reject an inquiry with a mandatory parent-visible reason."""

    rejection_reason: str = Field(
        ...,
        min_length=3,
        description="Reason for rejection; shown to the parent.",
    )


class InquiryFilterParams(BaseModel):
    """Query filters for staff inquiry list."""

    status: InquiryStatus | None = Field(
        default=None,
        description=(
            "Filter by workflow status: PENDING, UNDER_REVIEW, PROCESSING, "
            "INTERVIEW_SCHEDULED, INTERVIEW_PASS, INTERVIEW_FAIL, DOCUMENT_PENDING, "
            "DOCUMENT_VERIFICATION, ADMISSION_SUCCESS, or REJECTED."
        ),
    )
    admission_for_class_id: int | None = Field(
        default=None, description="Filter by requested catalog class ID.", examples=[1]
    )
    search: str | None = Field(
        default=None,
        description="Match student name, inquiry code, email, or mobile.",
    )
