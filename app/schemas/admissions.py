"""Pydantic schemas for inquiry-linked admission and documents."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import DocumentType
from app.schemas.common import ORMModel


class InquiryAdmissionCreateRequest(BaseModel):
    """Submit admission application after interview pass (staff or verified parent)."""

    class_id: int = Field(..., gt=0, description="Target class from catalog")
    section: str | None = Field(default=None, max_length=20)
    academic_year: str = Field(..., min_length=4, max_length=20)
    permanent_address: str | None = None
    temporary_address: str | None = None
    nationality: str | None = Field(default=None, max_length=100)
    disability: str | None = Field(default=None, max_length=255)
    blood_group: str | None = Field(default=None, max_length=10)
    reason_for_school_change: str | None = None
    notes: str | None = None


class InquiryAdmissionUpdateRequest(BaseModel):
    """Update draft/submitted admission details."""

    class_id: int | None = Field(default=None, gt=0)
    section: str | None = None
    academic_year: str | None = None
    permanent_address: str | None = None
    temporary_address: str | None = None
    nationality: str | None = None
    disability: str | None = None
    blood_group: str | None = None
    reason_for_school_change: str | None = None
    notes: str | None = None


class AdmissionDocumentResponse(ORMModel):
    """One uploaded document with verification state."""

    id: int
    admission_id: int
    document_type: str
    file_name: str
    file_path: str
    verification_status: str
    rejection_reason: str | None = None
    verified_at: datetime | None = None


class InquiryAdmissionResponse(ORMModel):
    """Full admission application for staff APIs."""

    id: int
    admission_code: str
    inquiry_id: int
    class_id: int
    section: str | None
    academic_year: str
    status: str
    permanent_address: str | None
    temporary_address: str | None
    nationality: str | None
    disability: str | None
    blood_group: str | None
    reason_for_school_change: str | None
    rejection_reason: str | None
    notes: str | None
    student_id: int | None
    documents: list[AdmissionDocumentResponse] = Field(default_factory=list)


# Legacy student-based admission (backward compatible)
class AdmissionCreateRequest(BaseModel):
    class_id: int = Field(..., gt=0)
    academic_year: str = Field(..., min_length=4, max_length=20)
    notes: str | None = None


class AdmissionUpdateRequest(BaseModel):
    class_id: int | None = Field(default=None, gt=0)
    academic_year: str | None = Field(default=None, min_length=4, max_length=20)
    notes: str | None = None


class AdmissionResponse(ORMModel):
    id: int
    student_id: int | None = None
    class_id: int
    academic_year: str
    status: str
    rejection_reason: str | None = None
    notes: str | None = None


class DocumentVerifyRequest(BaseModel):
    """Staff verification of a single document."""

    rejection_reason: str | None = Field(
        default=None,
        description="Required when rejecting a document",
    )


class RequiredDocumentsResponse(BaseModel):
    """Checklist of required document types."""

    required: list[str] = Field(default_factory=lambda: sorted(DocumentType))
