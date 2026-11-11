from datetime import UTC, date, datetime, time
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.common import ORMModel

AssessmentType = Literal[
    "unit_test",
    "periodic_test",
    "mid_term",
    "final_exam",
    "assignment",
    "quiz",
    "practical",
    "oral",
]


class AssignmentCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    details: str = Field(..., min_length=1, max_length=10000)
    class_id: int = Field(..., gt=0)
    subject_id: int = Field(..., gt=0)
    teacher_id: int | None = Field(default=None, gt=0)
    assigned_date: date | None = None
    due_date: date

    @field_validator("title", "details")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field cannot be blank")
        return normalized

    @model_validator(mode="after")
    def validate_due_date(self) -> "AssignmentCreateRequest":
        if self.assigned_date and self.due_date < self.assigned_date:
            raise ValueError("Due date cannot be before the assigned date")
        return self


class AssignmentUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    details: str | None = Field(default=None, min_length=1, max_length=10000)
    due_date: date | None = None

    @field_validator("title", "details")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field cannot be blank")
        return normalized

    @model_validator(mode="after")
    def require_changes(self) -> "AssignmentUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class AssignmentAttachmentResponse(ORMModel):
    id: int
    file_name: str
    content_type: str | None
    created_at: datetime


class AssignmentResponse(ORMModel):
    id: int
    title: str
    details: str
    class_id: int
    subject_id: int
    assigned_teacher_id: int
    assigned_date: date
    due_date: date
    status: str
    created_by: int
    updated_by: int | None
    created_at: datetime
    updated_at: datetime | None
    attachments: list[AssignmentAttachmentResponse] = Field(default_factory=list)


class TimetableCreateRequest(BaseModel):
    class_id: int = Field(..., gt=0)
    subject_id: int = Field(..., gt=0)
    teacher_id: int | None = Field(default=None, gt=0)
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: time
    end_time: time
    room: str | None = Field(default=None, max_length=100)
    academic_year: str = Field(..., min_length=1, max_length=20)

    @field_validator("room", "academic_year")
    @classmethod
    def strip_optional_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field cannot be blank")
        return normalized

    @model_validator(mode="after")
    def validate_period(self) -> "TimetableCreateRequest":
        if self.start_time >= self.end_time:
            raise ValueError("End time must be later than start time")
        return self


class TimetableUpdateRequest(BaseModel):
    class_id: int | None = Field(default=None, gt=0)
    subject_id: int | None = Field(default=None, gt=0)
    teacher_id: int | None = Field(default=None, gt=0)
    day_of_week: int | None = Field(default=None, ge=0, le=6)
    start_time: time | None = None
    end_time: time | None = None
    room: str | None = Field(default=None, max_length=100)
    academic_year: str | None = Field(default=None, min_length=1, max_length=20)

    @field_validator("room", "academic_year")
    @classmethod
    def normalize_timetable_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field cannot be blank")
        return normalized

    @model_validator(mode="after")
    def validate_timetable_update(self) -> "TimetableUpdateRequest":
        if not self.model_fields_set or all(
            getattr(self, field_name) is None for field_name in self.model_fields_set
        ):
            raise ValueError("At least one timetable field must be provided")
        if (
            self.start_time is not None
            and self.end_time is not None
            and self.start_time >= self.end_time
        ):
            raise ValueError("End time must be later than start time")
        return self

class TimetableResponse(ORMModel):
    id: int
    class_id: int
    subject_id: int
    teacher_id: int
    day_of_week: int
    start_time: time
    end_time: time
    room: str | None
    academic_year: str
    created_by: int
    updated_by: int | None
    created_at: datetime
    updated_at: datetime | None


class AssessmentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    assessment_type: AssessmentType
    class_id: int = Field(..., gt=0)
    subject_id: int = Field(..., gt=0)
    teacher_id: int | None = Field(default=None, gt=0)
    assessment_date: date
    max_score: Decimal = Field(..., gt=0, max_digits=8, decimal_places=2)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Name cannot be blank")
        return normalized


class AssessmentUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    assessment_type: AssessmentType | None = None
    assessment_date: date | None = None
    max_score: Decimal | None = Field(default=None, gt=0, max_digits=8, decimal_places=2)

    @field_validator("name")
    @classmethod
    def strip_optional_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Name cannot be blank")
        return normalized


class AssessmentResultRequest(BaseModel):
    score: Decimal | None = Field(default=None, ge=0, max_digits=8, decimal_places=2)
    result_status: Literal["present", "absent"] = "present"
    remarks: str | None = Field(default=None, max_length=500)

    @field_validator("remarks")
    @classmethod
    def strip_remarks(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def validate_score_state(self) -> "AssessmentResultRequest":
        if self.result_status == "absent" and self.score is not None:
            raise ValueError("Absent results cannot include a score")
        if self.result_status == "present" and self.score is None:
            raise ValueError("A score is required for a present student")
        return self


class AssessmentResultResponse(ORMModel):
    id: int
    assessment_id: int
    student_id: int
    score: Decimal | None
    result_status: str
    remarks: str | None
    entered_by: int
    updated_by: int | None
    created_at: datetime
    updated_at: datetime | None


class AssessmentResponse(ORMModel):
    id: int
    name: str
    assessment_type: str
    class_id: int
    subject_id: int
    teacher_id: int
    assessment_date: date
    max_score: Decimal
    is_published: bool
    created_by: int
    updated_by: int | None
    created_at: datetime
    updated_at: datetime | None
    results: list[AssessmentResultResponse] = Field(default_factory=list)


class EventCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=10000)
    starts_at: datetime
    ends_at: datetime
    venue: str | None = Field(default=None, max_length=200)
    audience: Literal["public", "students", "parents", "all"] = "all"

    @field_validator("title", "description")
    @classmethod
    def strip_event_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field cannot be blank")
        return normalized

    @field_validator("starts_at", "ends_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Event date-times must include a timezone offset")
        return value

    @model_validator(mode="after")
    def validate_event_period(self) -> "EventCreateRequest":
        if self.starts_at >= self.ends_at:
            raise ValueError("Event end must be later than its start")
        return self


class EventUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=10000)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    venue: str | None = Field(default=None, max_length=200)
    audience: Literal["public", "students", "parents", "all"] | None = None

    @field_validator("title", "description")
    @classmethod
    def strip_optional_event_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field cannot be blank")
        return normalized

    @field_validator("starts_at", "ends_at")
    @classmethod
    def require_optional_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("Event date-times must include a timezone offset")
        return value

    @model_validator(mode="after")
    def validate_event_update(self) -> "EventUpdateRequest":
        if not self.model_fields_set or all(
            getattr(self, field_name) is None for field_name in self.model_fields_set
        ):
            raise ValueError("At least one event field must be provided")
        if (
            self.starts_at is not None
            and self.ends_at is not None
            and self.starts_at >= self.ends_at
        ):
            raise ValueError("Event end must be later than its start")
        return self


class EventReviewRequest(BaseModel):
    status: Literal["published", "rejected"]
    rejection_reason: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_rejection_reason(self) -> "EventReviewRequest":
        if self.status == "rejected" and not (self.rejection_reason or "").strip():
            raise ValueError("A rejection reason is required")
        return self


class EventResponse(ORMModel):
    id: int
    title: str
    description: str
    starts_at: datetime
    ends_at: datetime
    venue: str | None
    audience: str
    status: str
    created_by: int
    reviewed_by: int | None
    reviewed_at: datetime | None
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime | None

    @field_validator("starts_at", "ends_at", "reviewed_at", mode="before")
    @classmethod
    def restore_utc_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            return value.replace(tzinfo=UTC)
        return value
