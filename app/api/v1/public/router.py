"""Aggregates all public (unauthenticated) v1 routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.api.v1.public.student import routes as student_public_routes
from app.schemas.role_portal import EventResponse
from app.services.role_portal import RolePortalService

public_router = APIRouter()
public_router.include_router(
    student_public_routes.router,
    prefix="/student",
)


@public_router.get("/events", tags=["public"])
def list_public_events(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    events = RolePortalService(db).list_public_events()
    data = [EventResponse.model_validate(event).model_dump() for event in events]
    return success_response("Published school events fetched successfully", data, request)
