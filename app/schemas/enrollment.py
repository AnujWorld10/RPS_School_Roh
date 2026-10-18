"""Schemas for student enrollment API responses."""

from pydantic import BaseModel, Field


class EnrollmentResponse(BaseModel):
    """Result of successful enrollment from an approved admission."""

    student_id: int = Field(..., description="Internal ID of the newly enrolled student.")
    student_code: str = Field(description="Business ID e.g. STU202600001")
    admission_id: int = Field(..., description="Internal ID of the approved admission.")
    admission_code: str = Field(
        ..., description="Business identifier of the admission.", examples=["ADM202600055"]
    )
    inquiry_code: str = Field(
        ...,
        description="Public tracking code of the originating inquiry.",
        examples=["INQ202600007"],
    )
    class_id: int = Field(..., description="ID of the enrolled class.", examples=[1])
    section: str | None = Field(..., description="Assigned class section, if applicable.")
    academic_year: str = Field(
        ..., description="Academic year of enrollment.", examples=["2026-2027"]
    )
    roll_number: int = Field(
        ..., description="Roll number assigned within the class and academic year."
    )
