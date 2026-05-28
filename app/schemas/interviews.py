"""Pydantic schemas for interview scheduling APIs."""

from datetime import date, time

from pydantic import BaseModel, Field

from app.models.enums import InterviewMode, InterviewResultUpdate
from app.schemas.common import ORMModel


class InterviewCreateRequest(BaseModel):
    """Staff request to schedule an interview for an inquiry."""

    schedule_date: date
    schedule_time: time
    location: str = Field(..., min_length=1, max_length=255)
    mode: InterviewMode = InterviewMode.OFFLINE
    interviewer_teacher_id: int | None = Field(default=None, gt=0)
    remarks: str | None = None


class InterviewResultUpdateRequest(BaseModel):
    """Record pass, fail, or absent for a scheduled interview."""

    result: InterviewResultUpdate
    remarks: str | None = None


class InterviewResponse(ORMModel):
    """Interview details returned to staff and public status APIs."""

    id: int
    inquiry_id: int
    schedule_date: date
    schedule_time: time
    location: str
    mode: str
    interviewer_teacher_id: int | None
    remarks: str | None
    result: str
