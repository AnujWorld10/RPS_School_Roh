from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.schemas.email import AppEmail
from app.schemas.fees import AdmissionFeeStructureResponse, MonthlyFeeStructureResponse


class StudentPortalRegistrationRequest(BaseModel):
    admission_id: str = Field(..., min_length=1, max_length=50)
    email: AppEmail
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    @model_validator(mode="after")
    def passwords_must_match(self) -> "StudentPortalRegistrationRequest":
        if self.password != self.confirm_password:
            raise ValueError("Password and confirmation do not match.")
        return self


class StudentPortalLoginRequest(BaseModel):
    student_id: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)


class StudentPortalRegistrationResponse(BaseModel):
    student_id: str
    email: str


class StudentPortalProfileResponse(BaseModel):
    student_id: str
    admission_id: str
    first_name: str
    middle_name: str | None
    last_name: str
    father_name: str | None
    mother_name: str | None = None
    date_of_birth: date
    gender: str
    class_name: str | None
    section: str | None
    academic_year: str | None
    email: str
    phone: str | None
    address: str | None
    admission_date: datetime | None
    student_photo_url: str | None = None
    status: str


class StudentPortalFeeDetailsResponse(BaseModel):
    student_id: str
    class_id: int | None
    academic_year: str | None
    admission_fee_structure: AdmissionFeeStructureResponse | None
    monthly_fee_structure: MonthlyFeeStructureResponse | None
    payment_records_available: bool = False
    paid_amount: Decimal | None = None
    pending_amount: Decimal | None = None
    upcoming_due_date: date | None = None
    payment_status: str | None = None
    billing_message: str

