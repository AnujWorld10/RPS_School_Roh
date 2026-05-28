from datetime import date

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.common import ORMModel


class StudentCreateRequest(BaseModel):
    admission_no: str | None = Field(default=None, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender: str = Field(..., min_length=1, max_length=20)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    current_class_id: int | None = Field(default=None, gt=0)

    @field_validator("first_name", "last_name", "admission_no", "phone", mode="before")
    @classmethod
    def strip_strings(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value


class StudentUpdateRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    current_class_id: int | None = Field(default=None, gt=0)


class StudentClassAssignRequest(BaseModel):
    class_id: int = Field(..., gt=0)
    academic_year: str = Field(..., min_length=4, max_length=20)


class StudentResponse(ORMModel):
    id: int
    admission_no: str | None
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    email: str | None
    phone: str | None
    current_class_id: int | None
    status: str


class StudentFilterParams(BaseModel):
    status: str | None = None
    current_class_id: int | None = None
    search: str | None = None
