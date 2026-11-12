from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.common import ORMModel


class SubjectCreateRequest(BaseModel):
    code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique subject code.",
        examples=["MATH"],
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Subject display name.",
        examples=["Mathematics"],
    )
    category: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    subject_type: Literal["mandatory", "elective", "optional"] = "mandatory"
    max_marks: Decimal | None = Field(default=None, gt=0, max_digits=8, decimal_places=2)
    passing_marks: Decimal | None = Field(default=None, ge=0, max_digits=8, decimal_places=2)

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("Subject code cannot be blank")
        return normalized

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Subject name cannot be blank")
        return normalized

    @field_validator("category", "description")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def validate_mark_ranges(self) -> "SubjectCreateRequest":
        if (self.max_marks is None) != (self.passing_marks is None):
            raise ValueError("Maximum marks and passing marks must be provided together")
        if self.max_marks is not None and self.passing_marks > self.max_marks:
            raise ValueError("Passing marks cannot exceed maximum marks")
        return self


class SubjectUpdateRequest(BaseModel):
    code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Updated unique subject code.",
        examples=["MATH"],
    )
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated subject display name.",
        examples=["Mathematics"],
    )
    category: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    subject_type: Literal["mandatory", "elective", "optional"] | None = None
    max_marks: Decimal | None = Field(default=None, gt=0, max_digits=8, decimal_places=2)
    passing_marks: Decimal | None = Field(default=None, ge=0, max_digits=8, decimal_places=2)

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("Subject code cannot be blank")
        return normalized

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Subject name cannot be blank")
        return normalized

    @field_validator("category", "description")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def require_an_update(self) -> "SubjectUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("At least one subject field must be provided")
        if {"max_marks", "passing_marks"} & self.model_fields_set and not {
            "max_marks",
            "passing_marks",
        }.issubset(self.model_fields_set):
            raise ValueError("Maximum marks and passing marks must be provided together")
        if (
            self.max_marks is not None
            and self.passing_marks is not None
            and self.passing_marks > self.max_marks
        ):
            raise ValueError("Passing marks cannot exceed maximum marks")
        return self


class SubjectResponse(ORMModel):
    id: int = Field(..., description="Internal subject ID.")
    code: str = Field(..., description="Unique subject code.")
    name: str = Field(..., description="Subject display name.")
    category: str | None
    description: str | None
    subject_type: str
    max_marks: Decimal | None
    passing_marks: Decimal | None
    is_active: bool = Field(..., description="Whether the subject can be assigned.")


class ClassSubjectAssignRequest(BaseModel):
    subject_id: int = Field(..., gt=0, description="Existing active subject catalog ID.")


class ClassTeacherAssignRequest(BaseModel):
    teacher_id: int = Field(..., gt=0, description="Existing active teacher ID.")


class TeacherClassSubjectAssignRequest(BaseModel):
    class_id: int = Field(..., gt=0, description="Class offering this subject.")
    subject_id: int = Field(..., gt=0, description="Subject already offered to the class.")


class ClassAcademicReadinessResponse(BaseModel):
    class_id: int
    ready: bool
    class_teacher_id: int | None
    active_subject_ids: list[int]
    issues: list[str]
