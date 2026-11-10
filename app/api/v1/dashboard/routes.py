from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.core.responses import success_response
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardSummaryEnvelope
from app.services.dashboard import DashboardService

router = APIRouter()


@router.get(
    "/summary",
    response_model=DashboardSummaryEnvelope,
    summary="Get permission-filtered dashboard metrics",
)
def get_dashboard_summary(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        User,
        Depends(
            require_permissions(
                "students.read",
                "teachers.read",
                "classes.read",
                "subjects.read",
                "inquiries.read",
                "admissions.read",
                "interviews.read",
            )
        ),
    ],
):
    summary = DashboardService(db).get_summary(current_user)
    return success_response(
        "Dashboard summary fetched successfully",
        summary.model_dump(),
        request,
    )
