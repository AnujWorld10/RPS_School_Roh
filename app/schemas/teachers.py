from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.models.enums import (
    AttendanceStatus,
    PaymentStatus,
    SalaryStatus,
    TeacherStatus,
)
from app.schemas.common import ORMModel


class TeacherCreateRequest(BaseModel):
    employee_no: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique employee number.",
        examples=["EMP-2026-001"],
    )
    first_name: str = Field(..., min_length=1, max_length=100, description="Teacher's given name.")
    last_name: str = Field(..., min_length=1, max_length=100, description="Teacher's family name.")
    email: EmailStr = Field(..., description="Teacher's work email address.")
    phone: str = Field(
        ...,
        min_length=5,
        max_length=30,
        description="Teacher's contact phone number.",
    )
    joining_date: date = Field(
        ..., description="Employment start date (YYYY-MM-DD).", examples=["2026-04-01"]
    )
    user_id: int | None = Field(
        default=None, gt=0, description="Optional existing platform user ID to link."
    )

    @field_validator("employee_no", "first_name", "last_name", "phone", mode="before")
    @classmethod
    def strip_strings(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value


class TeacherUpdateRequest(BaseModel):
    first_name: str | None = Field(default=None, description="Updated given name.")
    last_name: str | None = Field(default=None, description="Updated family name.")
    email: EmailStr | None = Field(
        default=None,
        description="Updated work email address.",
    )
    phone: str | None = Field(default=None, description="Updated contact phone number.")
    status: TeacherStatus | None = Field(
        default=None, description="Employment status: active, inactive, or resigned."
    )


class SubjectAssignRequest(BaseModel):
    subject_id: int = Field(..., gt=0, description="ID of the subject to assign.")


class ClassAssignRequest(BaseModel):
    class_id: int = Field(..., gt=0, description="ID of the class to assign.", examples=[1])


class AttendanceCreateRequest(BaseModel):
    attendance_date: date = Field(
        ..., description="Date for this attendance record.", examples=["2026-10-19"]
    )
    status: AttendanceStatus = Field(
        ..., description="Attendance state: present, absent, leave, or half_day."
    )
    remarks: str | None = Field(default=None, description="Optional attendance note.")


class SalaryPaymentCreateRequest(BaseModel):
    payment_month: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}$",
        description="Salary month in YYYY-MM format.",
        examples=["2026-10"],
    )
    gross_amount: Decimal = Field(
        ...,
        ge=0,
        max_digits=12,
        decimal_places=2,
        description="Gross salary amount before deductions.",
    )
    deduction_amount: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        max_digits=12,
        decimal_places=2,
        description="Total deductions; cannot exceed gross_amount.",
    )
    net_amount: Decimal = Field(
        ...,
        ge=0,
        max_digits=12,
        decimal_places=2,
        description="Take-home amount; must equal gross_amount minus deduction_amount.",
        examples=["47500.00"],
    )
    status: PaymentStatus = Field(
        default=PaymentStatus.PAID,
        description="Payment state: pending, paid, or failed.",
    )
    paid_at: datetime | None = Field(
        default=None,
        description="Payment completion timestamp, if paid.",
    )

    @model_validator(mode="after")
    def validate_net_amount(self) -> "SalaryPaymentCreateRequest":
        if self.net_amount != self.gross_amount - self.deduction_amount:
            raise ValueError("net_amount must equal gross_amount minus deduction_amount")
        if self.deduction_amount > self.gross_amount:
            raise ValueError("deduction_amount cannot exceed gross_amount")
        return self


class TeacherResponse(ORMModel):
    id: int = Field(..., description="Internal teacher ID.")
    employee_no: str = Field(..., description="Unique employee number.", examples=["EMP-2026-001"])
    first_name: str = Field(..., description="Teacher's given name.")
    last_name: str = Field(..., description="Teacher's family name.")
    email: str = Field(..., description="Teacher's work email address.")
    phone: str | None = Field(..., description="Contact phone, if available.")
    joining_date: date | None = Field(
        ..., description="Employment start date, if recorded.", examples=["2026-04-01"]
    )
    status: TeacherStatus = Field(
        ..., description="Employment status: active, inactive, or resigned."
    )


class AttendanceResponse(ORMModel):
    id: int = Field(..., description="Internal attendance record ID.")
    teacher_id: int = Field(..., description="ID of the teacher.")
    attendance_date: date = Field(..., description="Attendance date.", examples=["2026-10-19"])
    status: AttendanceStatus = Field(
        ..., description="Attendance state: present, absent, leave, or half_day."
    )
    remarks: str | None = Field(..., description="Attendance note, if any.")


class SalaryResponse(ORMModel):
    id: int = Field(..., description="Internal salary record ID.")
    teacher_id: int = Field(..., description="ID of the teacher.")
    base_salary: Decimal = Field(..., description="Base salary amount.")
    allowance: Decimal = Field(..., description="Additional salary allowance.")
    deduction: Decimal = Field(..., description="Recurring salary deduction.")
    effective_from: date = Field(
        ..., description="Date the salary terms take effect.", examples=["2026-04-01"]
    )
    status: SalaryStatus = Field(..., description="Salary record state: active or inactive.")


class SalaryPaymentResponse(ORMModel):
    id: int = Field(..., description="Internal salary payment ID.")
    teacher_id: int = Field(..., description="ID of the teacher receiving payment.")
    salary_id: int = Field(..., description="ID of the salary record used.")
    payment_month: str = Field(
        ..., description="Salary month in YYYY-MM format.", examples=["2026-10"]
    )
    gross_amount: Decimal = Field(..., description="Gross salary before deductions.")
    deduction_amount: Decimal = Field(..., description="Total deductions.")
    net_amount: Decimal = Field(..., description="Net amount paid.", examples=["47500.00"])
    status: PaymentStatus = Field(..., description="Payment state: pending, paid, or failed.")
    paid_at: datetime | None = Field(..., description="Payment timestamp, if paid.")


class TeacherFilterParams(BaseModel):
    status: TeacherStatus | None = Field(
        default=None, description="Filter by employment status: active, inactive, or resigned."
    )
    search: str | None = Field(
        default=None,
        description="Search by teacher name, employee number, or contact details.",
    )
