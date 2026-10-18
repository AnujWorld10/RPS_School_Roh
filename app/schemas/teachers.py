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
    employee_no: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=5, max_length=30)
    joining_date: date
    user_id: int | None = Field(default=None, gt=0)

    @field_validator("employee_no", "first_name", "last_name", "phone", mode="before")
    @classmethod
    def strip_strings(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value


class TeacherUpdateRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    status: TeacherStatus | None = None


class SubjectAssignRequest(BaseModel):
    subject_id: int = Field(..., gt=0)


class ClassAssignRequest(BaseModel):
    class_id: int = Field(..., gt=0)


class AttendanceCreateRequest(BaseModel):
    attendance_date: date
    status: AttendanceStatus
    remarks: str | None = None


class SalaryPaymentCreateRequest(BaseModel):
    payment_month: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    gross_amount: Decimal = Field(..., ge=0, max_digits=12, decimal_places=2)
    deduction_amount: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    net_amount: Decimal = Field(..., ge=0, max_digits=12, decimal_places=2)
    status: PaymentStatus = PaymentStatus.PAID
    paid_at: datetime | None = None

    @model_validator(mode="after")
    def validate_net_amount(self) -> "SalaryPaymentCreateRequest":
        if self.net_amount != self.gross_amount - self.deduction_amount:
            raise ValueError(
                "net_amount must equal gross_amount minus deduction_amount"
            )
        if self.deduction_amount > self.gross_amount:
            raise ValueError("deduction_amount cannot exceed gross_amount")
        return self


class TeacherResponse(ORMModel):
    id: int
    employee_no: str
    first_name: str
    last_name: str
    email: str
    phone: str | None
    joining_date: date | None
    status: TeacherStatus


class AttendanceResponse(ORMModel):
    id: int
    teacher_id: int
    attendance_date: date
    status: AttendanceStatus
    remarks: str | None


class SalaryResponse(ORMModel):
    id: int
    teacher_id: int
    base_salary: Decimal
    allowance: Decimal
    deduction: Decimal
    effective_from: date
    status: SalaryStatus


class SalaryPaymentResponse(ORMModel):
    id: int
    teacher_id: int
    salary_id: int
    payment_month: str
    gross_amount: Decimal
    deduction_amount: Decimal
    net_amount: Decimal
    status: PaymentStatus
    paid_at: datetime | None


class TeacherFilterParams(BaseModel):
    status: TeacherStatus | None = None
    search: str | None = None
