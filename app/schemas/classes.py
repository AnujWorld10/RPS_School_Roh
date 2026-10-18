from pydantic import BaseModel, Field, field_validator

from app.models.enums import ClassStatus
from app.schemas.common import ORMModel


class ClassCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Class or grade name.")
    section: str | None = Field(
        default=None, max_length=20, description="Optional section identifier."
    )
    academic_year: str = Field(
        ...,
        min_length=4,
        max_length=20,
        description="Academic year for this class.",
        examples=["2026-2027"],
    )
    capacity: int = Field(..., gt=0, description="Maximum number of students.")

    @field_validator("name", "section", "academic_year", mode="before")
    @classmethod
    def strip_strings(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value


class ClassUpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated class or grade name.",
    )
    section: str | None = Field(
        default=None, max_length=20, description="Updated section identifier."
    )
    academic_year: str | None = Field(
        default=None,
        min_length=4,
        max_length=20,
        description="Updated academic year.",
        examples=["2026-2027"],
    )
    capacity: int | None = Field(default=None, gt=0, description="Updated maximum student count.")
    status: ClassStatus | None = Field(default=None, description="Class state: active or inactive.")

    @field_validator("name", "section", "academic_year", mode="before")
    @classmethod
    def strip_strings(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value


class ClassResponse(ORMModel):
    id: int = Field(..., description="Internal class ID.")
    name: str = Field(..., description="Class or grade name.")
    section: str | None = Field(..., description="Section identifier, if set.")
    academic_year: str = Field(..., description="Academic year.", examples=["2026-2027"])
    capacity: int = Field(..., description="Maximum number of students.")
    status: ClassStatus = Field(..., description="Class state: active or inactive.")


class ClassFilterParams(BaseModel):
    academic_year: str | None = Field(
        default=None, description="Filter by academic year.", examples=["2026-2027"]
    )
    status: ClassStatus | None = Field(
        default=None, description="Filter by class state: active or inactive."
    )
