"""
Public student inquiry APIs (no authentication required).

Endpoints:
- POST /inquiry — submit new inquiry
- GET  /inquiry/status/{inquiry_code} — track status with parent verification headers
- PUT  /inquiry/update — modify inquiry with verification
"""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Header, Path, Request, UploadFile, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response
from pydantic import EmailStr, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationException, BusinessRuleException
from app.core.responses import success_response
from app.db.session import get_db
from app.models.class_model import Class
from app.models.enums import ClassStatus
from app.repositories.inquiries import StudentInquiryRepository
from app.schemas.admissions import (
    PublicAdmissionDocumentUploadResponse,
    PublicInquiryAdmissionCreateRequest,
)
from app.schemas.classes import PublicClassOptionResponse
from app.schemas.inquiries import (
    PublicInquiryCreateRequest,
    PublicInquiryCreateResponse,
    PublicInquiryUpdateRequest,
)
from app.schemas.inquiry_mappers import to_public_status_response
from app.services.inquiries import InquiryService
from app.services.inquiry_admissions import InquiryAdmissionService

router = APIRouter()


@router.get(
    "/classes",
    summary="List classes available for public admission applications",
)
def list_public_class_options(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    classes = db.scalars(
        select(Class)
        .where(
            Class.status == ClassStatus.ACTIVE.value,
            Class.deleted_at.is_(None),
        )
        .order_by(Class.academic_year, Class.name, Class.section)
    ).all()
    data = [
        PublicClassOptionResponse(
            id=school_class.id,
            name=school_class.name,
            section=school_class.section,
            academic_year=school_class.academic_year,
        ).model_dump()
        for school_class in classes
    ]
    return success_response("Available admission classes fetched successfully", data, request)


@router.post(
    "/inquiry",
    status_code=status.HTTP_201_CREATED,
    summary="Submit student admission inquiry",
    description="Public form submission. Returns inquiry_code for status tracking.",
)
def submit_student_inquiry(
    payload: PublicInquiryCreateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    """Create a new student inquiry with status PENDING."""
    inquiry = InquiryService(db).create_public_inquiry(payload, request)
    data = PublicInquiryCreateResponse(
        inquiry_code=inquiry.inquiry_code,
        status=inquiry.status,
    )
    return success_response("Inquiry created successfully", data.model_dump(), request)


@router.get(
    "/inquiry/status/{inquiry_code}",
    summary="Check inquiry status",
    description="Requires the parent email and mobile number submitted with the inquiry.",
)
def get_inquiry_status(
    inquiry_code: Annotated[
        str,
        Path(
            description="Inquiry tracking code returned when the inquiry was submitted.",
            examples=["INQ202600007"],
        ),
    ],
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    email: Annotated[
        EmailStr,
        Header(
            alias="X-Parent-Email",
            description="Email address supplied with the original inquiry.",
        ),
    ],
    parent_mobile: Annotated[
        str,
        Header(
            alias="X-Parent-Mobile",
            description="Parent/guardian mobile number supplied with the original inquiry.",
        ),
    ],
):
    """Return current status, rejection reason, and status timeline."""
    inquiry = InquiryService(db).get_public_status(
        inquiry_code,
        str(email),
        parent_mobile,
    )
    return success_response(
        "Inquiry status fetched successfully",
        to_public_status_response(inquiry).model_dump(),
        request,
    )


@router.put(
    "/inquiry/update",
    summary="Update inquiry details",
    description="Requires inquiry_code, email, and parent_mobile to verify ownership.",
)
def update_student_inquiry(
    payload: PublicInquiryUpdateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    """Update allowed fields while inquiry is not in a locked terminal status."""
    inquiry = InquiryService(db).update_public_inquiry(payload, request)
    return success_response(
        "Inquiry updated successfully",
        to_public_status_response(inquiry).model_dump(),
        request,
    )


@router.post(
    "/admission",
    status_code=status.HTTP_201_CREATED,
    summary="Submit admission application (after interview pass)",
)
def submit_admission(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    inquiry_code: Annotated[
        str,
        Form(
            min_length=5,
            max_length=20,
            description="Inquiry tracking code returned when the inquiry was submitted.",
            examples=["INQ202600007"],
        ),
    ],
    email: Annotated[
        EmailStr,
        Form(description="Email address supplied with the original inquiry."),
    ],
    parent_mobile: Annotated[
        str,
        Form(
            min_length=5,
            max_length=30,
            description="Parent/guardian mobile number supplied with the original inquiry.",
        ),
    ],
    class_id: Annotated[
        int,
        Form(gt=0, description="Catalog ID of the class requested for admission.", examples=[1]),
    ],
    academic_year: Annotated[
        str,
        Form(
            min_length=4,
            max_length=20,
            description="Academic year for admission.",
            examples=["2026-2027"],
        ),
    ],
    student_aadhaar: Annotated[
        str,
        Form(description="12-digit student Aadhaar number."),
    ] = "",
    parent_aadhaar: Annotated[
        str,
        Form(description="12-digit parent/guardian Aadhaar number."),
    ] = "",
    last_school_marks: Annotated[
        str,
        Form(description="Marks obtained at the previous school."),
    ] = "",
    last_school_percentage: Annotated[
        str,
        Form(description="Percentage obtained at the previous school."),
    ] = "",
    last_school_id_or_roll_number: Annotated[
        str,
        Form(description="Previous-school student ID or roll number."),
    ] = "",
    section: Annotated[
        str | None,
        Form(max_length=20, description="Optional section within the selected class."),
    ] = None,
    permanent_address: Annotated[
        str | None,
        Form(max_length=2000, description="Optional permanent residential address."),
    ] = None,
):
    """
    Public admission form (FRD POST /student/admission).

    Parent must verify via inquiry_code, email, and parent_mobile.
    """
    inquiry = StudentInquiryRepository(db).verify_parent_credentials(
        inquiry_code.strip().upper(),
        str(email),
        parent_mobile.strip(),
    )
    if not inquiry:
        raise AuthenticationException("Invalid inquiry credentials")

    try:
        payload = PublicInquiryAdmissionCreateRequest.model_validate(
            {
                "class_id": class_id,
                "section": section,
                "academic_year": academic_year,
                "permanent_address": permanent_address,
                "student_aadhaar": student_aadhaar,
                "parent_aadhaar": parent_aadhaar,
                "last_school_marks": last_school_marks,
                "last_school_percentage": last_school_percentage,
                "last_school_id_or_roll_number": last_school_id_or_roll_number,
            }
        )
    except ValidationError as exc:
        errors = [
            {
                **error,
                "loc": ("body", *error.get("loc", ())),
            }
            for error in exc.errors()
        ]
        raise RequestValidationError(errors) from exc
    admission = InquiryAdmissionService(db).create_from_inquiry(
        inquiry.id, payload, actor_id=None, request=request
    )
    return success_response(
        "Admission submitted successfully",
        {"admission_code": admission.admission_code, "status": admission.status},
        request,
    )


@router.post(
    "/admission/documents",
    status_code=status.HTTP_201_CREATED,
    summary="Upload an admission document as the verified parent",
)
def upload_public_admission_document(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    inquiry_code: Annotated[str, Form(min_length=5, max_length=20)],
    email: Annotated[EmailStr, Form()],
    parent_mobile: Annotated[str, Form(min_length=5, max_length=30)],
    document_type: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
):
    inquiry = StudentInquiryRepository(db).verify_parent_credentials(
        inquiry_code.strip().upper(),
        str(email),
        parent_mobile.strip(),
    )
    if not inquiry:
        raise AuthenticationException("Invalid inquiry credentials")
    admission = InquiryAdmissionService(db).get_public_admission(inquiry.id)
    document = InquiryAdmissionService(db).upload_document(
        admission.id, document_type, file, request
    )
    data = PublicAdmissionDocumentUploadResponse(
        document_type=document.document_type,
        verification_status=document.verification_status,
        rejection_reason=document.rejection_reason,
        verified_at=document.verified_at,
    ).model_dump()
    return success_response("Admission document uploaded successfully", data, request)


@router.get(
    "/inquiry/status/{inquiry_code}/admission-letter",
    summary="Download the admission letter after enrollment",
    response_class=Response,
    responses={
        200: {
            "description": "Parent-verified PDF admission letter.",
            "content": {
                "application/pdf": {
                    "schema": {"type": "string", "format": "binary"},
                }
            },
        }
    },
)
def download_admission_letter(
    inquiry_code: Annotated[str, Path(min_length=5, max_length=20)],
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    email: Annotated[EmailStr, Header(alias="X-Parent-Email")],
    parent_mobile: Annotated[str, Header(alias="X-Parent-Mobile")],
)-> Response:
    from app.services.admission_letter import create_admission_letter

    inquiry = StudentInquiryRepository(db).verify_parent_credentials(
        inquiry_code.strip().upper(),
        str(email),
        parent_mobile.strip(),
    )
    if not inquiry:
        raise AuthenticationException("Invalid inquiry credentials")
    admission = InquiryAdmissionService(db).get_public_admission(inquiry.id)
    if not admission.student:
        raise BusinessRuleException("The admission letter is available after enrollment.")
    content = create_admission_letter(admission)
    student_code = admission.student.student_code
    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Cache-Control": "no-store",
            "Content-Disposition": f'attachment; filename="{student_code}-admission.pdf"',
            "X-Content-Type-Options": "nosniff",
        },
    )
