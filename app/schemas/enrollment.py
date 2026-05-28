"""Schemas for student enrollment API responses."""

from pydantic import BaseModel, Field


class EnrollmentResponse(BaseModel):
    """Result of successful enrollment from an approved admission."""

    student_id: int
    student_code: str = Field(description="Business ID e.g. STU202600001")
    admission_id: int
    admission_code: str
    inquiry_code: str
    class_id: int
    section: str | None
    academic_year: str
    roll_number: int
