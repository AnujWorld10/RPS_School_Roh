"""Pydantic schemas for interview scheduling APIs."""

from datetime import date, time

from pydantic import BaseModel, Field

from app.models.enums import InterviewMode, InterviewResultUpdate
from app.schemas.common import ORMModel


class InterviewCreateRequest(BaseModel):
    """Staff request to schedule an interview for an inquiry."""

    schedule_date: date = Field(..., description="Date of the interview.", examples=["2026-11-05"])
    schedule_time: time = Field(
        ..., description="Start time in 24-hour HH:MM format.", examples=["10:30"]
    )
    location: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Room, address, or meeting location.",
    )
    mode: InterviewMode = Field(
        default=InterviewMode.OFFLINE, description="Interview mode: ONLINE or OFFLINE."
    )
    interviewer_teacher_id: int | None = Field(
        default=None, gt=0, description="Optional ID of the assigned interviewer."
    )
    remarks: str | None = Field(
        default=None,
        description="Optional scheduling notes.",
    )


class InterviewResultUpdateRequest(BaseModel):
    """Record pass, fail, or absent for a scheduled interview."""

    result: InterviewResultUpdate = Field(
        ..., description="Interview outcome: PASSED, FAILED, or ABSENT."
    )
    remarks: str | None = Field(
        default=None,
        description="Optional notes about the outcome.",
    )


class InterviewResponse(ORMModel):
    """Interview details returned to staff and public status APIs."""

    id: int = Field(..., description="Internal interview ID.")
    inquiry_id: int = Field(..., description="ID of the related student inquiry.")
    schedule_date: date = Field(
        ..., description="Scheduled interview date.", examples=["2026-11-05"]
    )
    schedule_time: time = Field(..., description="Scheduled start time.", examples=["10:30"])
    location: str = Field(..., description="Interview location or meeting details.")
    mode: str = Field(..., description="Interview mode: ONLINE or OFFLINE.")
    interviewer_teacher_id: int | None = Field(..., description="Assigned teacher ID, if any.")
    remarks: str | None = Field(..., description="Interview notes, if any.")
    result: str = Field(..., description="Outcome: SCHEDULED, PASSED, FAILED, or ABSENT.")
