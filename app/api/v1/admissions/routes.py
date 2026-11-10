"""
Admission APIs: inquiry-driven flow (phase 2) and legacy student-based routes.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.core.config import get_settings
from app.core.exceptions import NotFoundException
from app.core.pagination import PaginationParams, pagination_params
from app.core.responses import paginated_response, success_response
from app.db.session import get_db
from app.models.user import User
from app.schemas.admissions import (
    AdmissionDocumentResponse,
    AdmissionResponse,
    DocumentVerifyRequest,
    InquiryAdmissionCreateRequest,
    InquiryAdmissionResponse,
    InquiryAdmissionUpdateRequest,
    RequiredDocumentsResponse,
)
from app.schemas.common import RejectionRequest
from app.services.admissions import AdmissionService
from app.services.enrollment import EnrollmentService
from app.services.inquiry_admissions import InquiryAdmissionService
from app.utils.admission_pii import masked_aadhaar

router = APIRouter()


def _admission_response(admission) -> dict:
    """Serialize inquiry admission including documents."""
    data = InquiryAdmissionResponse.model_validate(admission).model_dump()
    data["documents"] = [
        AdmissionDocumentResponse.model_validate(d).model_dump()
        for d in getattr(admission, "documents", [])
    ]
    data["student_aadhaar_masked"] = masked_aadhaar(admission.student_aadhaar_last4)
    data["parent_aadhaar_masked"] = masked_aadhaar(admission.parent_aadhaar_last4)
    data["class_name"] = admission.school_class.name if admission.school_class else None
    return data


# --- Phase 2: inquiry-linked admissions ---


@router.get("/inquiry-admissions")
def list_inquiry_admissions(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("admissions.read"))],
    params: Annotated[PaginationParams, Depends(pagination_params)],
    status: str | None = Query(
        default=None,
        description=(
            "Filter by admission state: draft, submitted, document_pending, "
            "document_verification, approved, or rejected."
        ),
    ),
    academic_year: str | None = Query(
        default=None,
        description="Filter by academic year.",
        examples=["2026-2027"],
    ),
):
    result = InquiryAdmissionService(db).list_admissions(params, status, academic_year)
    data = [_admission_response(item) for item in result.items]
    return paginated_response(
        "Admissions fetched successfully",
        data,
        result.page,
        result.limit,
        result.total,
        request,
    )


@router.post(
    "/inquiries/{inquiry_id}/admission",
    status_code=status.HTTP_201_CREATED,
    summary="Create admission from inquiry (after interview pass)",
)
def create_inquiry_admission(
    inquiry_id: int,
    payload: InquiryAdmissionCreateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("admissions.create"))],
):
    admission = InquiryAdmissionService(db).create_from_inquiry(
        inquiry_id, payload, current_user.id, request
    )
    return success_response(
        "Admission created successfully",
        _admission_response(admission),
        request,
    )


@router.get("/inquiry-admissions/{admission_id}")
def get_inquiry_admission(
    admission_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("admissions.read"))],
):
    admission = InquiryAdmissionService(db).get_admission(admission_id)
    return success_response(
        "Admission fetched successfully",
        _admission_response(admission),
        request,
    )


@router.put("/inquiry-admissions/{admission_id}")
def update_inquiry_admission(
    admission_id: int,
    payload: InquiryAdmissionUpdateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("admissions.update"))],
):
    admission = InquiryAdmissionService(db).update_admission(
        admission_id, payload, current_user.id, request
    )
    return success_response(
        "Admission updated successfully",
        _admission_response(admission),
        request,
    )


@router.post("/documents/{document_id}/verify")
def verify_document(
    document_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("admissions.verify_documents"))],
    verified: bool = Query(
        default=True,
        description="Set true to verify the document or false to reject it.",
    ),
    body: DocumentVerifyRequest | None = None,
):
    doc = InquiryAdmissionService(db).verify_document(
        document_id,
        verified,
        current_user.id,
        request,
        rejection_reason=body.rejection_reason if body else None,
    )
    return success_response(
        "Document verification updated",
        AdmissionDocumentResponse.model_validate(doc).model_dump(),
        request,
    )


@router.get(
    "/documents/{document_id}/file",
    summary="View an uploaded admission document",
)
def view_admission_document(
    document_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("admissions.read"))],
):
    document = InquiryAdmissionService(db).documents.get_by_id(document_id)
    if not document:
        raise NotFoundException("Admission document not found")
    upload_root = get_settings().upload_path.resolve()
    file_path = (upload_root / document.file_path).resolve()
    if not file_path.is_relative_to(upload_root) or not file_path.is_file():
        raise NotFoundException("Admission document file not found")
    media_type = {
        ".pdf": "application/pdf",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
    }.get(file_path.suffix.lower(), "application/octet-stream")
    return FileResponse(
        file_path,
        media_type=media_type,
        headers={
            "Cache-Control": "no-store",
            "Content-Disposition": "inline",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.get("/documents/required")
def list_required_documents(request: Request):
    return success_response(
        "Required documents listed",
        RequiredDocumentsResponse().model_dump(),
        request,
    )


@router.post("/inquiry-admissions/{admission_id}/approve")
def approve_inquiry_admission(
    admission_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("admissions.approve"))],
):
    admission = InquiryAdmissionService(db).submit_for_enrollment(
        admission_id, current_user.id, request
    )
    return success_response(
        "Admission approved for enrollment",
        _admission_response(admission),
        request,
    )


@router.post("/inquiry-admissions/{admission_id}/reject")
def reject_inquiry_admission(
    admission_id: int,
    payload: RejectionRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("admissions.reject"))],
):
    admission = InquiryAdmissionService(db).reject_admission(
        admission_id, payload.rejection_reason, current_user.id, request
    )
    return success_response(
        "Admission rejected",
        _admission_response(admission),
        request,
    )


@router.post(
    "/inquiry-admissions/{admission_id}/enroll",
    status_code=status.HTTP_201_CREATED,
    summary="Enroll student — assigns STU code and roll number",
)
def enroll_student(
    admission_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("enrollment.create"))],
):
    result = EnrollmentService(db).enroll_student(admission_id, current_user.id, request)
    return success_response(
        "Student enrolled successfully",
        result.model_dump(),
        request,
    )


# --- Legacy student-based admissions (backward compatible) ---


@router.get("/students/admissions/all")
def list_legacy_admissions(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("admissions.read"))],
    params: Annotated[PaginationParams, Depends(pagination_params)],
    status: str | None = Query(
        default=None,
        description="Filter by legacy admission state.",
    ),
    academic_year: str | None = Query(
        default=None,
        description="Filter by academic year.",
        examples=["2026-2027"],
    ),
):
    result = AdmissionService(db).list_admissions(params, status, academic_year)
    data = [AdmissionResponse.model_validate(item).model_dump() for item in result.items]
    return paginated_response(
        "Admissions fetched successfully",
        data,
        result.page,
        result.limit,
        result.total,
        request,
    )
