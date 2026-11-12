"""Pydantic schemas for inquiry-linked admission and documents."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.models.enums import DocumentType, REQUIRED_ADMISSION_DOCUMENTS
from app.schemas.common import ORMModel


class InquiryAdmissionCreateRequest(BaseModel):
    """Submit admission application after interview pass (staff or verified parent)."""

    class_id: int = Field(..., gt=0, description="Target class catalog ID.", examples=[1])
    section: str | None = Field(
        default=None,
        max_length=20,
        description="Class section assigned by staff during enrollment.",
    )
    academic_year: str = Field(
        ...,
        min_length=4,
        max_length=20,
        description="Academic year for admission.",
        examples=["2026-2027"],
    )
    permanent_address: str | None = Field(
        default=None,
        description="Applicant's permanent residential address.",
    )
    student_aadhaar: str | None = Field(
        default=None,
        description="Student Aadhaar number; encrypted at rest and never returned by the API.",
    )
    parent_aadhaar: str | None = Field(
        default=None,
        description=(
            "Parent/guardian Aadhaar number; encrypted at rest and never returned by the API."
        ),
    )
    last_school_marks: Decimal | None = Field(
        default=None, ge=0, le=999999.99, description="Marks obtained at the previous school."
    )
    last_school_percentage: Decimal | None = Field(
        default=None, ge=0, le=100, description="Previous-school percentage, from 0 to 100."
    )
    last_school_id_or_roll_number: str | None = Field(
        default=None,
        max_length=100,
        description="Student ID or roll number from the previous school.",
    )
    temporary_address: str | None = Field(
        default=None,
        description="Applicant's current address if different.",
    )
    nationality: str | None = Field(
        default=None, max_length=100, description="Applicant's nationality."
    )
    disability: str | None = Field(
        default=None,
        max_length=255,
        description="Disability information relevant to school support, if any.",
        examples=["Requires wheelchair access"],
    )
    blood_group: str | None = Field(
        default=None,
        max_length=10,
        description="Applicant's blood group, if known.",
        examples=["O+"],
    )
    reason_for_school_change: str | None = Field(
        default=None, description="Reason for changing schools."
    )
    notes: str | None = Field(
        default=None,
        description="Additional admission application notes.",
    )

    @field_validator(
        "section",
        "academic_year",
        "permanent_address",
        "last_school_id_or_roll_number",
        "temporary_address",
        "nationality",
        "disability",
        "blood_group",
        "reason_for_school_change",
        "notes",
        mode="before",
    )
    @classmethod
    def strip_form_strings(cls, value: str | None) -> str | None:
        return value.strip() if isinstance(value, str) else value


class PublicInquiryAdmissionCreateRequest(InquiryAdmissionCreateRequest):
    """Public admission form fields that must be supplied by the parent."""

    student_aadhaar: str = Field(
        ...,
        min_length=12,
        max_length=12,
        pattern=r"^[0-9]{12}$",
        description="Student Aadhaar number; encrypted at rest and never returned by the API.",
    )
    parent_aadhaar: str = Field(
        ...,
        min_length=12,
        max_length=12,
        pattern=r"^[0-9]{12}$",
        description=(
            "Parent/guardian Aadhaar number; encrypted at rest and never returned by the API."
        ),
    )
    last_school_marks: Decimal = Field(
        ..., ge=0, le=999999.99, description="Marks obtained at the previous school."
    )
    last_school_percentage: Decimal = Field(
        ..., ge=0, le=100, description="Previous-school percentage, from 0 to 100."
    )
    last_school_id_or_roll_number: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Student ID or roll number from the previous school.",
    )


class InquiryAdmissionUpdateRequest(BaseModel):
    """Update draft/submitted admission details."""

    class_id: int | None = Field(
        default=None, gt=0, description="Updated target class catalog ID.", examples=[1]
    )
    section: str | None = Field(default=None, description="Updated requested class section.")
    academic_year: str | None = Field(
        default=None, description="Updated academic year.", examples=["2026-2027"]
    )
    permanent_address: str | None = Field(
        default=None,
        description="Updated permanent residential address.",
    )
    temporary_address: str | None = Field(
        default=None,
        description="Updated current address, if different.",
    )
    nationality: str | None = Field(default=None, description="Updated nationality.")
    disability: str | None = Field(
        default=None,
        description="Updated disability/support information.",
        examples=["Requires wheelchair access"],
    )
    blood_group: str | None = Field(
        default=None, description="Updated blood group, if known.", examples=["O+"]
    )
    reason_for_school_change: str | None = Field(
        default=None,
        description="Updated reason for changing schools.",
    )
    notes: str | None = Field(
        default=None,
        description="Updated additional application notes.",
    )


class AdmissionDocumentResponse(ORMModel):
    """One uploaded document with verification state."""

    id: int = Field(..., description="Internal document record ID.")
    admission_id: int = Field(..., description="ID of the related admission application.")
    document_type: str = Field(
        ...,
        description=(
            "Document category: progress_report, transfer_certificate, migration_certificate, "
            "character_certificate, student_aadhar (student Aadhaar), or "
            "parent_aadhar (parent Aadhaar)."
        ),
    )
    file_name: str = Field(..., description="Uploaded file name.")
    verification_status: str = Field(
        ..., description="Verification state: PENDING, VERIFIED, or REJECTED."
    )
    rejection_reason: str | None = Field(
        default=None,
        description="Reason the document was rejected, if applicable.",
    )
    verified_at: datetime | None = Field(
        default=None,
        description="Timestamp when the document was verified.",
    )


class PublicAdmissionDocumentUploadResponse(BaseModel):
    """Safe upload confirmation returned to the parent."""

    document_type: str
    verification_status: str
    rejection_reason: str | None = None
    verified_at: datetime | None = None


class InquiryAdmissionResponse(ORMModel):
    """Full admission application for staff APIs."""

    id: int = Field(..., description="Internal admission record ID.")
    admission_code: str = Field(
        ...,
        description="Business identifier for the admission application.",
        examples=["ADM202600055"],
    )
    inquiry_id: int = Field(..., description="ID of the originating inquiry.")
    class_id: int = Field(..., description="Target class catalog ID.", examples=[1])
    class_name: str | None = Field(default=None, description="Target class name.")
    section: str | None = Field(..., description="Assigned or requested section.")
    academic_year: str = Field(
        ..., description="Academic year for admission.", examples=["2026-2027"]
    )
    status: str = Field(
        ...,
        description=(
            "Admission state: draft, submitted, document_pending, document_verification, "
            "approved, or rejected."
        ),
    )
    permanent_address: str | None = Field(
        ...,
        description="Permanent residential address, if provided.",
    )
    student_aadhaar_masked: str | None = Field(
        default=None, description="Masked student Aadhaar number; full value is never returned."
    )
    parent_aadhaar_masked: str | None = Field(
        default=None, description="Masked parent Aadhaar number; full value is never returned."
    )
    last_school_marks: Decimal | None = Field(
        default=None, description="Marks obtained at the previous school."
    )
    last_school_percentage: Decimal | None = Field(
        default=None, description="Previous-school percentage."
    )
    last_school_id_or_roll_number: str | None = Field(
        default=None, description="Student ID or roll number from the previous school."
    )
    temporary_address: str | None = Field(
        ..., description="Temporary/current address, if provided."
    )
    nationality: str | None = Field(..., description="Applicant nationality, if provided.")
    disability: str | None = Field(
        ...,
        description="Disability/support information, if provided.",
        examples=["Requires wheelchair access"],
    )
    blood_group: str | None = Field(..., description="Blood group, if provided.", examples=["O+"])
    reason_for_school_change: str | None = Field(
        ...,
        description="Reason for changing schools, if provided.",
    )
    rejection_reason: str | None = Field(
        ...,
        description="Rejection reason, if the application was rejected.",
    )
    notes: str | None = Field(
        ...,
        description="Additional admission application notes.",
    )
    student_id: int | None = Field(
        ..., description="Enrolled student ID, once enrollment is complete."
    )
    documents: list[AdmissionDocumentResponse] = Field(
        default_factory=list, description="Documents uploaded for this application."
    )


# Legacy student-based admission (backward compatible)
class AdmissionCreateRequest(BaseModel):
    class_id: int = Field(..., gt=0, description="Target class catalog ID.", examples=[1])
    academic_year: str = Field(
        ...,
        min_length=4,
        max_length=20,
        description="Academic year for admission.",
        examples=["2026-2027"],
    )
    notes: str | None = Field(
        default=None,
        description="Optional staff notes.",
    )


class AdmissionUpdateRequest(BaseModel):
    class_id: int | None = Field(
        default=None, gt=0, description="Updated target class catalog ID.", examples=[1]
    )
    academic_year: str | None = Field(
        default=None,
        min_length=4,
        max_length=20,
        description="Updated academic year.",
        examples=["2026-2027"],
    )
    notes: str | None = Field(
        default=None,
        description="Updated staff notes.",
    )


class AdmissionResponse(ORMModel):
    id: int = Field(..., description="Internal admission record ID.")
    student_id: int | None = Field(default=None, description="Linked student ID, if enrolled.")
    class_id: int = Field(..., description="Target class catalog ID.", examples=[1])
    academic_year: str = Field(
        ..., description="Academic year for admission.", examples=["2026-2027"]
    )
    status: str = Field(..., description="Admission workflow status.")
    rejection_reason: str | None = Field(
        default=None,
        description="Reason for rejection, if applicable.",
    )
    notes: str | None = Field(
        default=None,
        description="Additional staff notes.",
    )


class DocumentVerifyRequest(BaseModel):
    """Staff verification of a single document."""

    rejection_reason: str | None = Field(
        default=None,
        description=(
            "Reason for rejecting the document; required when verification status is set to "
            "REJECTED."
        ),
    )


class RequiredDocumentsResponse(BaseModel):
    """Checklist of required document types."""

    required: list[str] = Field(
        default_factory=lambda: sorted(REQUIRED_ADMISSION_DOCUMENTS),
        description=(
            "Required document categories: progress_report, transfer_certificate, "
            "student_aadhar, and parent_aadhar. Migration and character certificates are optional."
        ),
    )
