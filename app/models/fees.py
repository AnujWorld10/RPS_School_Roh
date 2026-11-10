from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BIGINT_PK, Base, TimestampMixin
from app.models.class_model import Class


class AdmissionFeeStructure(Base, TimestampMixin):
    __tablename__ = "admission_fee_structures"
    __table_args__ = (
        UniqueConstraint(
            "academic_year",
            "class_id",
            name="uq_admission_fee_year_class",
        ),
    )

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    class_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("classes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    structure_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    school_class: Mapped["Class"] = relationship(
        "Class",
        back_populates="admission_fee_structures",
    )
    components: Mapped[list["AdmissionFeeComponent"]] = relationship(
        back_populates="structure",
        cascade="all, delete-orphan",
        order_by="AdmissionFeeComponent.id",
    )


class AdmissionFeeComponent(Base):
    __tablename__ = "admission_fee_components"
    __table_args__ = (
        UniqueConstraint("structure_id", "fee_name", name="uq_admission_fee_component_name"),
        CheckConstraint("amount >= 0", name="ck_admission_fee_component_nonnegative"),
    )

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    structure_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("admission_fee_structures.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fee_name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_refundable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )

    structure: Mapped[AdmissionFeeStructure] = relationship(back_populates="components")


class MonthlyFeeStructure(Base, TimestampMixin):
    __tablename__ = "monthly_fee_structures"
    __table_args__ = (
        UniqueConstraint(
            "academic_year",
            "class_id",
            name="uq_monthly_fee_year_class",
        ),
    )

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    class_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("classes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    structure_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    school_class: Mapped["Class"] = relationship(
        "Class",
        back_populates="monthly_fee_structures",
    )
    components: Mapped[list["MonthlyFeeComponent"]] = relationship(
        back_populates="structure",
        cascade="all, delete-orphan",
        order_by="MonthlyFeeComponent.id",
    )


class MonthlyFeeComponent(Base):
    __tablename__ = "monthly_fee_components"
    __table_args__ = (
        UniqueConstraint("structure_id", "fee_name", name="uq_monthly_fee_component_name"),
        CheckConstraint("amount >= 0", name="ck_monthly_fee_component_nonnegative"),
        CheckConstraint(
            "billing_frequency IN ('MONTHLY', 'QUARTERLY', 'ANNUALLY', 'ONE_TIME')",
            name="ck_monthly_fee_component_frequency",
        ),
    )

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    structure_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("monthly_fee_structures.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fee_name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    billing_frequency: Mapped[str] = mapped_column(String(20), nullable=False)
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )

    structure: Mapped[MonthlyFeeStructure] = relationship(back_populates="components")
