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

    @model_validator(mode="after")
    def require_an_update(self) -> "SubjectUpdateRequest":
        if self.code is None and self.name is None:
            raise ValueError("At least one subject field must be provided")
        return self


class SubjectResponse(ORMModel):
    id: int = Field(..., description="Internal subject ID.")
    code: str = Field(..., description="Unique subject code.")
    name: str = Field(..., description="Subject display name.")
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
