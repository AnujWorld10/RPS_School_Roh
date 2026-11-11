from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from typing import Protocol

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator

from app.models.enums import BillingFrequency
from app.schemas.common import ORMModel

MONEY_FIELD = Field(
    ...,
    ge=Decimal("0"),
    max_digits=10,
    decimal_places=2,
    description="Non-negative amount with a maximum of two decimal places.",
)


class FeeComponentInput(Protocol):
    fee_name: str


def _validate_unique_names(components: Sequence[FeeComponentInput]) -> None:
    names = [component.fee_name.casefold() for component in components]
    if len(names) != len(set(names)):
        raise ValueError("Fee component names must be unique within a structure.")


def _normalize_fee_name(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        raise ValueError("Fee name cannot be blank.")
    return normalized


class FeeClassResponse(ORMModel):
    id: int
    name: str
    section: str | None
    academic_year: str


class AdmissionFeeComponentCreate(BaseModel):
    fee_name: str = Field(..., min_length=1, max_length=100, description="Unique charge name.")
    amount: Decimal = MONEY_FIELD
    is_refundable: bool = Field(default=False, description="Whether this charge is refundable.")
    is_optional: bool = Field(default=False, description="Whether families may opt out.")
    description: str | None = Field(default=None, max_length=255)

    @field_validator("fee_name", mode="before")
    @classmethod
    def normalize_fee_name(cls, value: str) -> str:
        return _normalize_fee_name(value) or ""


class AdmissionFeeComponentUpdate(BaseModel):
    id: int | None = Field(
        default=None, gt=0, description="Existing component ID; omit to add a component."
    )
    fee_name: str | None = Field(default=None, min_length=1, max_length=100)
    amount: Decimal | None = Field(default=None, ge=Decimal("0"), max_digits=10, decimal_places=2)
    is_refundable: bool | None = None
    is_optional: bool | None = None
    description: str | None = Field(default=None, max_length=255)

    @field_validator("fee_name", mode="before")
    @classmethod
    def normalize_fee_name(cls, value: str | None) -> str | None:
        return _normalize_fee_name(value)

    @model_validator(mode="after")
    def validate_component_update(self) -> "AdmissionFeeComponentUpdate":
        supplied_fields = self.model_fields_set - {"id"}
        non_nullable_fields = {"fee_name", "amount", "is_refundable", "is_optional"}
        if any(
            field in self.model_fields_set and getattr(self, field) is None
            for field in non_nullable_fields
        ):
            raise ValueError("Non-nullable fee component fields cannot be null.")
        if self.id is None and (self.fee_name is None or self.amount is None):
            raise ValueError("A new component requires a fee name and amount.")
        if self.id is not None and not supplied_fields:
            raise ValueError("Provide at least one component field to update.")
        return self


class AdmissionFeeComponentResponse(ORMModel):
    id: int
    fee_name: str
    amount: Decimal
    is_refundable: bool
    is_optional: bool
    description: str | None
    created_at: datetime


class AdmissionFeeStructureCreate(BaseModel):
    academic_year: str = Field(..., min_length=4, max_length=20, examples=["2026-2027"])
    class_id: int = Field(..., gt=0, description="Existing class in the selected academic year.")
    structure_name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool = True
    components: list[AdmissionFeeComponentCreate] = Field(..., min_length=1)

    @field_validator("academic_year", "structure_name", mode="before")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_component_names(self) -> "AdmissionFeeStructureCreate":
        _validate_unique_names(self.components)
        return self


class AdmissionFeeStructureUpdate(BaseModel):
    academic_year: str | None = Field(default=None, min_length=4, max_length=20)
    class_id: int | None = Field(default=None, gt=0)
    structure_name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    components: list[AdmissionFeeComponentUpdate] | None = Field(default=None, min_length=1)

    @field_validator("academic_year", "structure_name", mode="before")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_update(self) -> "AdmissionFeeStructureUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update.")
        non_nullable_fields = {
            "academic_year",
            "class_id",
            "structure_name",
            "is_active",
            "components",
        }
        if any(
            field in self.model_fields_set and getattr(self, field) is None
            for field in non_nullable_fields
        ):
            raise ValueError("Non-nullable fee structure fields cannot be null.")
        if self.components is not None:
            ids = [component.id for component in self.components if component.id is not None]
            if len(ids) != len(set(ids)):
                raise ValueError("A component may only be updated once per request.")
        return self


class AdmissionFeeStructureResponse(ORMModel):
    id: int
    academic_year: str
    class_id: int
    school_class: FeeClassResponse
    structure_name: str
    description: str | None
    is_active: bool
    components: list[AdmissionFeeComponentResponse]
    created_at: datetime
    updated_at: datetime | None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def mandatory_total(self) -> Decimal:
        return sum(
            (component.amount for component in self.components if not component.is_optional),
            Decimal("0.00"),
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def optional_total(self) -> Decimal:
        return sum(
            (component.amount for component in self.components if component.is_optional),
            Decimal("0.00"),
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_amount(self) -> Decimal:
        return self.mandatory_total + self.optional_total


class MonthlyFeeComponentCreate(BaseModel):
    fee_name: str = Field(..., min_length=1, max_length=100, description="Unique charge name.")
    amount: Decimal = MONEY_FIELD
    billing_frequency: BillingFrequency
    is_optional: bool = Field(default=False, description="Whether families may opt out.")
    description: str | None = Field(default=None, max_length=255)

    @field_validator("fee_name", mode="before")
    @classmethod
    def normalize_fee_name(cls, value: str) -> str:
        return _normalize_fee_name(value) or ""


class MonthlyFeeComponentUpdate(BaseModel):
    id: int | None = Field(
        default=None, gt=0, description="Existing component ID; omit to add a component."
    )
    fee_name: str | None = Field(default=None, min_length=1, max_length=100)
    amount: Decimal | None = Field(default=None, ge=Decimal("0"), max_digits=10, decimal_places=2)
    billing_frequency: BillingFrequency | None = None
    is_optional: bool | None = None
    description: str | None = Field(default=None, max_length=255)

    @field_validator("fee_name", mode="before")
    @classmethod
    def normalize_fee_name(cls, value: str | None) -> str | None:
        return _normalize_fee_name(value)

    @model_validator(mode="after")
    def validate_component_update(self) -> "MonthlyFeeComponentUpdate":
        supplied_fields = self.model_fields_set - {"id"}
        non_nullable_fields = {
            "fee_name",
            "amount",
            "billing_frequency",
            "is_optional",
        }
        if any(
            field in self.model_fields_set and getattr(self, field) is None
            for field in non_nullable_fields
        ):
            raise ValueError("Non-nullable fee component fields cannot be null.")
        if self.id is None and (
            self.fee_name is None or self.amount is None or self.billing_frequency is None
        ):
            raise ValueError("A new component requires a fee name, amount, and billing frequency.")
        if self.id is not None and not supplied_fields:
            raise ValueError("Provide at least one component field to update.")
        return self


class MonthlyFeeComponentResponse(ORMModel):
    id: int
    fee_name: str
    amount: Decimal
    billing_frequency: BillingFrequency
    is_optional: bool
    description: str | None
    created_at: datetime


class MonthlyFeeStructureCreate(BaseModel):
    academic_year: str = Field(..., min_length=4, max_length=20, examples=["2026-2027"])
    class_id: int = Field(..., gt=0, description="Existing class in the selected academic year.")
    structure_name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool = True
    components: list[MonthlyFeeComponentCreate] = Field(..., min_length=1)

    @field_validator("academic_year", "structure_name", mode="before")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_component_names(self) -> "MonthlyFeeStructureCreate":
        _validate_unique_names(self.components)
        return self


class MonthlyFeeStructureUpdate(BaseModel):
    academic_year: str | None = Field(default=None, min_length=4, max_length=20)
    class_id: int | None = Field(default=None, gt=0)
    structure_name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    components: list[MonthlyFeeComponentUpdate] | None = Field(default=None, min_length=1)

    @field_validator("academic_year", "structure_name", mode="before")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_update(self) -> "MonthlyFeeStructureUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update.")
        non_nullable_fields = {
            "academic_year",
            "class_id",
            "structure_name",
            "is_active",
            "components",
        }
        if any(
            field in self.model_fields_set and getattr(self, field) is None
            for field in non_nullable_fields
        ):
            raise ValueError("Non-nullable fee structure fields cannot be null.")
        if self.components is not None:
            ids = [component.id for component in self.components if component.id is not None]
            if len(ids) != len(set(ids)):
                raise ValueError("A component may only be updated once per request.")
        return self


_ANNUAL_FREQUENCY_MULTIPLIERS = {
    BillingFrequency.MONTHLY: Decimal("12"),
    BillingFrequency.QUARTERLY: Decimal("4"),
    BillingFrequency.ANNUALLY: Decimal("1"),
    BillingFrequency.ONE_TIME: Decimal("1"),
}


class MonthlyFeeStructureResponse(ORMModel):
    id: int
    academic_year: str
    class_id: int
    school_class: FeeClassResponse
    structure_name: str
    description: str | None
    is_active: bool
    components: list[MonthlyFeeComponentResponse]
    created_at: datetime
    updated_at: datetime | None

    def _annual_total(self, optional: bool) -> Decimal:
        return sum(
            (
                component.amount * _ANNUAL_FREQUENCY_MULTIPLIERS[component.billing_frequency]
                for component in self.components
                if component.is_optional is optional
            ),
            Decimal("0.00"),
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def mandatory_annual_total(self) -> Decimal:
        return self._annual_total(optional=False)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def optional_annual_total(self) -> Decimal:
        return self._annual_total(optional=True)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def mandatory_monthly_equivalent(self) -> Decimal:
        return (self.mandatory_annual_total / Decimal("12")).quantize(Decimal("0.01"))

    @computed_field  # type: ignore[prop-decorator]
    @property
    def optional_monthly_equivalent(self) -> Decimal:
        return (self.optional_annual_total / Decimal("12")).quantize(Decimal("0.01"))

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_annual_amount(self) -> Decimal:
        return self.mandatory_annual_total + self.optional_annual_total


class FeeStructureStatusUpdate(BaseModel):
    is_active: bool = Field(..., description="Whether the fee structure is active.")
