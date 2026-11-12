from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class SubjectOfferingRequest(BaseModel):
    subject_type: Literal["mandatory", "elective", "optional"]
    stream: str | None = Field(default=None, max_length=30)
    is_active: bool = True


class ExaminationComponentInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    component_type: Literal["theory", "practical", "internal", "combined"]
    max_marks: Decimal = Field(gt=0, max_digits=8, decimal_places=2)
    passing_marks: Decimal = Field(ge=0, max_digits=8, decimal_places=2)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Component name cannot be blank")
        return normalized

    @model_validator(mode="after")
    def validate_passing_marks(self) -> "ExaminationComponentInput":
        if self.passing_marks > self.max_marks:
            raise ValueError("Component passing marks cannot exceed maximum marks")
        return self


class ExaminationSubjectInput(BaseModel):
    subject_id: int = Field(gt=0)
    teacher_id: int | None = Field(default=None, gt=0)
    max_marks: Decimal = Field(gt=0, max_digits=8, decimal_places=2)
    passing_marks: Decimal = Field(ge=0, max_digits=8, decimal_places=2)
    components: list[ExaminationComponentInput] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_marks_and_components(self) -> "ExaminationSubjectInput":
        if self.passing_marks > self.max_marks:
            raise ValueError("Subject passing marks cannot exceed maximum marks")
        if (
            sum((component.max_marks for component in self.components), Decimal("0"))
            != self.max_marks
        ):
            raise ValueError("Component maximum marks must add up to the subject maximum")
        names = [component.name.casefold() for component in self.components]
        if len(names) != len(set(names)):
            raise ValueError("Component names must be unique within a subject")
        return self


class ExaminationCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    class_id: int = Field(gt=0)
    examination_type: Literal[
        "unit_test",
        "periodic_test",
        "term",
        "mid_term",
        "final_exam",
        "practical",
        "oral",
    ]
    start_date: date
    end_date: date
    description: str | None = Field(default=None, max_length=5000)
    subjects: list[ExaminationSubjectInput] = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field cannot be blank")
        return normalized

    @model_validator(mode="after")
    def validate_exam(self) -> "ExaminationCreateRequest":
        if self.end_date < self.start_date:
            raise ValueError("Examination end date must not precede its start date")
        subject_ids = [item.subject_id for item in self.subjects]
        if len(subject_ids) != len(set(subject_ids)):
            raise ValueError("Each subject may only be added once to an examination")
        return self


class StudentMarkInput(BaseModel):
    student_id: int = Field(gt=0)
    component_id: int = Field(gt=0)
    status: Literal["PRESENT", "ABSENT", "EXEMPTED"]
    obtained_marks: Decimal | None = Field(default=None, ge=0, max_digits=8, decimal_places=2)
    remarks: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_score_for_status(self) -> "StudentMarkInput":
        if self.status == "PRESENT" and self.obtained_marks is None:
            raise ValueError("Marks are required when the student is present")
        if self.status != "PRESENT" and self.obtained_marks is not None:
            raise ValueError("Marks must be omitted for absent or exempted students")
        return self


class MarksBatchRequest(BaseModel):
    marks: list[StudentMarkInput] = Field(min_length=1, max_length=2000)

    @model_validator(mode="after")
    def reject_duplicate_marks(self) -> "MarksBatchRequest":
        keys = [(item.student_id, item.component_id) for item in self.marks]
        if len(keys) != len(set(keys)):
            raise ValueError("A student can have only one mark per component")
        return self


class MarksCorrectionRequest(MarksBatchRequest):
    reason: str = Field(min_length=5, max_length=500)

    @field_validator("reason")
    @classmethod
    def strip_reason(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) < 5:
            raise ValueError("Correction reason must contain at least 5 characters")
        return normalized


class GradingRuleInput(BaseModel):
    grade: str = Field(min_length=1, max_length=10)
    minimum_percentage: Decimal = Field(ge=0, le=100, max_digits=5, decimal_places=2)
    maximum_percentage: Decimal = Field(ge=0, le=100, max_digits=5, decimal_places=2)
    description: str | None = Field(default=None, max_length=200)

    @field_validator("grade")
    @classmethod
    def normalize_grade(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("Grade cannot be blank")
        return normalized

    @model_validator(mode="after")
    def validate_range(self) -> "GradingRuleInput":
        if self.minimum_percentage > self.maximum_percentage:
            raise ValueError("Minimum percentage cannot exceed maximum percentage")
        return self


class GradingScaleUpdateRequest(BaseModel):
    rules: list[GradingRuleInput] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def validate_ranges(self) -> "GradingScaleUpdateRequest":
        ordered = sorted(self.rules, key=lambda rule: rule.minimum_percentage)
        if len({rule.grade for rule in ordered}) != len(ordered):
            raise ValueError("Each grade must be unique within the scale")
        if ordered[0].minimum_percentage != Decimal("0"):
            raise ValueError("The grading scale must start at 0 percent")
        if ordered[-1].maximum_percentage != Decimal("100"):
            raise ValueError("The grading scale must end at 100 percent")
        for current, following in zip(ordered, ordered[1:], strict=False):
            if following.minimum_percentage != current.maximum_percentage + Decimal("0.01"):
                raise ValueError("Grading ranges must be contiguous and must not overlap")
        return self
