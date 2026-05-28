"""
Authenticated staff APIs for managing student admission inquiries.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.core.pagination import PaginationParams, pagination_params
from app.core.responses import paginated_response, success_response
from app.db.session import get_db
from app.models.user import User
from app.schemas.inquiries import (
    AdminInquiryUpdateRequest,
    InquiryRejectRequest,
    InquiryReviewActionRequest,
)
from app.schemas.inquiry_mappers import to_staff_inquiry_response
from app.services.inquiries import InquiryService

router = APIRouter()


@router.get("")
def list_inquiries(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("inquiries.read"))],
    params: Annotated[PaginationParams, Depends(pagination_params)],
    status: str | None = Query(default=None, description="Filter by InquiryStatus value"),
    admission_for_class_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
):
    """Paginated list of all student inquiries for staff review."""
    result = InquiryService(db).list_inquiries(
        params, status, admission_for_class_id, search
    )
    data = [to_staff_inquiry_response(item) for item in result.items]
    return paginated_response(
        "Inquiries fetched successfully",
        data,
        result.page,
        result.limit,
        result.total,
        request,
    )


@router.get("/{inquiry_id}")
def get_inquiry(
    inquiry_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("inquiries.read"))],
):
    """Get full inquiry details including status history."""
    inquiry = InquiryService(db).get_inquiry(inquiry_id)
    return success_response(
        "Inquiry fetched successfully",
        to_staff_inquiry_response(inquiry),
        request,
    )


@router.put("/{inquiry_id}")
def update_inquiry_admin(
    inquiry_id: int,
    payload: AdminInquiryUpdateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("inquiries.update"))],
):
    """Update staff-only fields (class mapping, internal notes)."""
    inquiry = InquiryService(db).update_inquiry_admin(
        inquiry_id, payload, current_user.id, request
    )
    return success_response(
        "Inquiry updated successfully",
        to_staff_inquiry_response(inquiry),
        request,
    )


@router.post("/{inquiry_id}/review/start")
def start_inquiry_review(
    inquiry_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("inquiries.update"))],
    body: InquiryReviewActionRequest | None = None,
):
    """Move inquiry from PENDING to UNDER_REVIEW."""
    inquiry = InquiryService(db).start_review(
        inquiry_id,
        current_user.id,
        request,
        body.notes if body else None,
    )
    return success_response(
        "Inquiry review started",
        to_staff_inquiry_response(inquiry),
        request,
    )


@router.post("/{inquiry_id}/review/process")
def mark_inquiry_processing(
    inquiry_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("inquiries.update"))],
    body: InquiryReviewActionRequest | None = None,
):
    """Move inquiry from UNDER_REVIEW to PROCESSING (eligible)."""
    inquiry = InquiryService(db).mark_processing(
        inquiry_id,
        current_user.id,
        request,
        body.notes if body else None,
    )
    return success_response(
        "Inquiry marked as processing",
        to_staff_inquiry_response(inquiry),
        request,
    )


@router.post("/{inquiry_id}/reject")
def reject_inquiry(
    inquiry_id: int,
    payload: InquiryRejectRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("inquiries.reject"))],
):
    """Reject inquiry with a parent-visible reason; status becomes REJECTED."""
    inquiry = InquiryService(db).reject_inquiry(
        inquiry_id,
        payload.rejection_reason,
        current_user.id,
        request,
    )
    return success_response(
        "Inquiry rejected successfully",
        to_staff_inquiry_response(inquiry),
        request,
    )
