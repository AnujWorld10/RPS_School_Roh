"""
Staff APIs for interview scheduling and result recording.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.core.responses import success_response
from app.db.session import get_db
from app.models.user import User
from app.schemas.interviews import (
    InterviewCreateRequest,
    InterviewResponse,
    InterviewResultUpdateRequest,
)
from app.services.interviews import InterviewService

router = APIRouter()


@router.post(
    "/inquiries/{inquiry_id}/schedule",
    status_code=status.HTTP_201_CREATED,
    summary="Schedule interview for inquiry",
)
def schedule_interview(
    inquiry_id: int,
    payload: InterviewCreateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("interviews.schedule"))],
):
    """Create interview and set inquiry status to INTERVIEW_SCHEDULED."""
    interview = InterviewService(db).schedule_interview(
        inquiry_id, payload, current_user.id, request
    )
    return success_response(
        "Interview scheduled successfully",
        InterviewResponse.model_validate(interview).model_dump(),
        request,
    )


@router.get("/inquiries/{inquiry_id}")
def list_inquiry_interviews(
    inquiry_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("interviews.read"))],
):
    """List all interviews for an inquiry."""
    interviews = InterviewService(db).list_for_inquiry(inquiry_id)
    data = [InterviewResponse.model_validate(i).model_dump() for i in interviews]
    return success_response("Interviews fetched successfully", data, request)


@router.post("/{interview_id}/result")
def record_interview_result(
    interview_id: int,
    payload: InterviewResultUpdateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("interviews.update"))],
):
    """Record PASSED, FAILED, or ABSENT and update inquiry status."""
    interview = InterviewService(db).record_result(
        interview_id, payload, current_user.id, request
    )
    return success_response(
        "Interview result recorded",
        InterviewResponse.model_validate(interview).model_dump(),
        request,
    )


@router.get("/{interview_id}")
def get_interview(
    interview_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("interviews.read"))],
):
    interview = InterviewService(db).get_interview(interview_id)
    return success_response(
        "Interview fetched successfully",
        InterviewResponse.model_validate(interview).model_dump(),
        request,
    )
