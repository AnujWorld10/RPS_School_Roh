"""
Public student inquiry APIs (no authentication required).

Endpoints:
- POST /inquiry — submit new inquiry
- GET  /inquiry/status/{inquiry_code} — track status with parent verification headers
- PUT  /inquiry/update — modify inquiry with verification
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Form, Header, Path, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import EmailStr, ValidationError
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationException
from app.core.responses import success_response
from app.db.session import get_db
from app.repositories.inquiries import StudentInquiryRepository
from app.schemas.admissions import InquiryAdmissionCreateRequest
from app.schemas.inquiries import (
    PublicInquiryCreateRequest,
    PublicInquiryCreateResponse,
    PublicInquiryUpdateRequest,
)
from app.schemas.inquiry_mappers import to_public_status_response
from app.services.inquiries import InquiryService
from app.services.inquiry_admissions import InquiryAdmissionService

router = APIRouter()


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
        payload = InquiryAdmissionCreateRequest(
            class_id=class_id,
            section=section,
            academic_year=academic_year,
            permanent_address=permanent_address,
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
