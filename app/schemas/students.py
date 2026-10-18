from datetime import date

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.common import ORMModel


class StudentCreateRequest(BaseModel):
    admission_no: str | None = Field(
        default=None,
        max_length=50,
        description="Optional school-issued admission number.",
        examples=["ADM2026001"],
    )
    first_name: str = Field(..., min_length=1, max_length=100, description="Student's given name.")
    last_name: str = Field(..., min_length=1, max_length=100, description="Student's family name.")
    date_of_birth: date = Field(
        ..., description="Student date of birth in YYYY-MM-DD format.", examples=["2018-04-12"]
    )
    gender: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Gender value recorded for the student (male, female, or other).",
    )
    email: EmailStr | None = Field(
        default=None,
        description="Optional student or guardian email address.",
    )
    phone: str | None = Field(
        default=None,
        max_length=30,
        description="Optional student or guardian phone number.",
    )
    current_class_id: int | None = Field(
        default=None, gt=0, description="Optional ID of the student's current class.", examples=[1]
    )

    @field_validator("first_name", "last_name", "admission_no", "phone", mode="before")
    @classmethod
    def strip_strings(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value


class StudentUpdateRequest(BaseModel):
    first_name: str | None = Field(default=None, description="Updated given name.")
    last_name: str | None = Field(default=None, description="Updated family name.")
    date_of_birth: date | None = Field(
        default=None, description="Updated date of birth (YYYY-MM-DD).", examples=["2018-04-12"]
    )
    gender: str | None = Field(
        default=None,
        description="Updated gender value (male, female, or other).",
    )
    email: EmailStr | None = Field(
        default=None,
        description="Updated student or guardian email.",
    )
    phone: str | None = Field(default=None, description="Updated contact phone number.")
    current_class_id: int | None = Field(
        default=None, gt=0, description="Updated current class ID.", examples=[1]
    )


class StudentClassAssignRequest(BaseModel):
    class_id: int = Field(..., gt=0, description="ID of the class to assign.", examples=[1])
    academic_year: str = Field(
        ...,
        min_length=4,
        max_length=20,
        description="Academic year for the assignment.",
        examples=["2026-2027"],
    )


class StudentResponse(ORMModel):
    id: int = Field(..., description="Internal student ID.")
    admission_no: str | None = Field(
        ..., description="School-issued admission number, if assigned.", examples=["ADM2026001"]
    )
    first_name: str = Field(..., description="Student's given name.")
    last_name: str = Field(..., description="Student's family name.")
    date_of_birth: date = Field(..., description="Student date of birth.", examples=["2018-04-12"])
    gender: str = Field(..., description="Recorded gender: male, female, or other.")
    email: str | None = Field(..., description="Student or guardian email, if available.")
    phone: str | None = Field(..., description="Contact phone, if available.")
    current_class_id: int | None = Field(
        ..., description="Current class ID, if assigned.", examples=[1]
    )
    status: str = Field(
        ...,
        description=(
            "Student lifecycle status: prospective, active, inactive, graduated, or transferred."
        ),
    )


class StudentFilterParams(BaseModel):
    status: str | None = Field(
        default=None,
        description=(
            "Filter by student status: prospective, active, inactive, graduated, or transferred."
        ),
    )
    current_class_id: int | None = Field(
        default=None, description="Filter by current class ID.", examples=[1]
    )
    search: str | None = Field(
        default=None, description="Search student names or admission number."
    )
