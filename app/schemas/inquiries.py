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

    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    gender: Gender
    father_name: str = Field(..., min_length=1, max_length=200)
    dob: date = Field(..., description="Student date of birth")
    student_mobile: str | None = Field(default=None, max_length=30)
    parent_mobile: str = Field(..., min_length=5, max_length=30)
    email: EmailStr
    address: str = Field(..., min_length=5)
    last_school: str = Field(..., min_length=1, max_length=255)
    current_class: str = Field(..., min_length=1, max_length=100)
    admission_for_class: str = Field(..., min_length=1, max_length=100)
    last_school_percentage: Decimal | None = Field(default=None, ge=0, le=100)
    admission_for_class_id: int | None = Field(
        default=None,
        gt=0,
        description="Optional FK when client knows catalog class id",
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


class PublicInquiryUpdateRequest(BaseModel):
    """
    Request body for PUT /api/v1/public/student/inquiry/update.

    Parent must prove ownership via inquiry_code + email + parent_mobile.
    """

    inquiry_code: str = Field(..., min_length=5, max_length=20)
    email: EmailStr
    parent_mobile: str = Field(..., min_length=5, max_length=30)
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    gender: Gender | None = None
    father_name: str | None = Field(default=None, max_length=200)
    dob: date | None = None
    student_mobile: str | None = Field(default=None, max_length=30)
    address: str | None = None
    last_school: str | None = Field(default=None, max_length=255)
    current_class: str | None = Field(default=None, max_length=100)
    admission_for_class: str | None = Field(default=None, max_length=100)
    last_school_percentage: Decimal | None = Field(default=None, ge=0, le=100)

    @field_validator("inquiry_code", "parent_mobile", mode="before")
    @classmethod
    def strip_required(cls, value: str) -> str:
        return value.strip().upper() if isinstance(value, str) else value


class InquiryStatusHistoryResponse(ORMModel):
    """One row from inquiry_status_history exposed on status APIs."""

    id: int
    from_status: str | None
    to_status: str
    change_reason: str | None
    created_at: datetime


class PublicInquiryCreateResponse(BaseModel):
    """Minimal response after successful public inquiry submission."""

    inquiry_code: str
    status: str
    message: str = "Inquiry submitted successfully. Please save your inquiry ID for tracking."


class PublicInterviewSummary(BaseModel):
    """Interview slot shown on public status page."""

    schedule_date: date
    schedule_time: time
    location: str
    mode: str
    result: str


class PublicAdmissionSummary(BaseModel):
    """Admission progress shown on public status page."""

    admission_code: str | None = None
    status: str | None = None
    documents_uploaded: int = 0
    documents_required: int = 6


class PublicInquiryStatusResponse(BaseModel):
    """Parent-facing inquiry status (no internal staff notes)."""

    inquiry_code: str
    status: str
    rejection_reason: str | None = None
    admission_for_class: str
    created_at: datetime
    updated_at: datetime | None = None
    status_timeline: list[InquiryStatusHistoryResponse] = Field(
        default_factory=list,
        description="Chronological status changes",
    )
    latest_interview: PublicInterviewSummary | None = None
    admission: PublicAdmissionSummary | None = None


class StudentInquiryResponse(ORMModel):
    """Full inquiry record for authenticated staff APIs."""

    id: int
    inquiry_code: str
    status_timeline: list[InquiryStatusHistoryResponse] = Field(default_factory=list)
    serial_number: int
    first_name: str
    middle_name: str | None
    last_name: str
    gender: str
    father_name: str
    date_of_birth: date
    student_mobile: str | None
    parent_mobile: str
    email: str
    address: str
    last_school: str
    current_class: str
    admission_for_class: str
    last_school_percentage: Decimal | None
    admission_for_class_id: int | None
    status: str
    rejection_reason: str | None = None
    internal_notes: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class AdminInquiryUpdateRequest(BaseModel):
    """Staff-only field updates (including internal notes and class mapping)."""

    admission_for_class_id: int | None = Field(default=None, gt=0)
    internal_notes: str | None = None


class InquiryReviewActionRequest(BaseModel):
    """Body for admin review transition endpoints."""

    notes: str | None = Field(default=None, description="Optional staff note stored on history")


class InquiryRejectRequest(BaseModel):
    """Reject an inquiry with a mandatory parent-visible reason."""

    rejection_reason: str = Field(..., min_length=3)


class InquiryFilterParams(BaseModel):
    """Query filters for staff inquiry list."""

    status: InquiryStatus | None = None
    admission_for_class_id: int | None = None
    search: str | None = Field(default=None, description="Match name, code, email, or mobile")
