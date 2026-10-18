from pydantic import BaseModel, Field, field_validator

from app.models.enums import ClassStatus
from app.schemas.common import ORMModel


class ClassCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    section: str | None = Field(default=None, max_length=20)
    academic_year: str = Field(..., min_length=4, max_length=20)
    capacity: int = Field(..., gt=0)

    @field_validator("name", "section", "academic_year", mode="before")
    @classmethod
    def strip_strings(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value


class ClassUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    section: str | None = Field(default=None, max_length=20)
    academic_year: str | None = Field(default=None, min_length=4, max_length=20)
    capacity: int | None = Field(default=None, gt=0)
    status: ClassStatus | None = None

    @field_validator("name", "section", "academic_year", mode="before")
    @classmethod
    def strip_strings(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value


class ClassResponse(ORMModel):
    id: int
    name: str
    section: str | None
    academic_year: str
    capacity: int
    status: ClassStatus


class ClassFilterParams(BaseModel):
    academic_year: str | None = None
    status: ClassStatus | None = None
