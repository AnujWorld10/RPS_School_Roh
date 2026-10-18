from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class IDMixin(BaseModel):
    id: int = Field(..., description="Internal database record ID.")


class TimestampResponse(ORMModel):
    created_at: datetime = Field(..., description="Timestamp when the record was created.")
    updated_at: datetime | None = Field(
        default=None,
        description="Timestamp of the most recent update, if any.",
    )


class MessageResponse(BaseModel):
    message: str = Field(
        ...,
        description="Human-readable operation result.",
    )


class StatusUpdateRequest(BaseModel):
    status: str = Field(..., description="New lifecycle or workflow status.")
    reason: str | None = Field(
        default=None,
        description="Optional explanation for the status change.",
    )


class NotesRequest(BaseModel):
    notes: str | None = Field(default=None, description="Optional staff notes.")


class RejectionRequest(BaseModel):
    rejection_reason: str = Field(
        ...,
        min_length=1,
        description="Explanation shown for the rejection.",
    )


class WarningItem(BaseModel):
    code: str = Field(..., description="Machine-readable warning identifier.")
    message: str = Field(
        ...,
        description="Human-readable warning details.",
    )
