from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class IDMixin(BaseModel):
    id: int


class TimestampResponse(ORMModel):
    created_at: datetime
    updated_at: datetime | None = None


class MessageResponse(BaseModel):
    message: str


class StatusUpdateRequest(BaseModel):
    status: str
    reason: str | None = None


class NotesRequest(BaseModel):
    notes: str | None = None


class RejectionRequest(BaseModel):
    rejection_reason: str = Field(..., min_length=1)


class WarningItem(BaseModel):
    code: str
    message: str
