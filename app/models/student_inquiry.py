"""
ORM models for the student admission inquiry domain.

Maps to FRD tables:
- ``student_inquiries`` (student_inquiry)
- ``inquiry_status_history``
"""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BigInt, TimestampMixin
from app.models.enums import Gender, InquiryStatus

if TYPE_CHECKING:
    from app.models.class_model import Class
    from app.models.user import User


class StudentInquiry(Base, TimestampMixin):
    """
  Stores a public student admission inquiry from first contact through enrollment.

  ``inquiry_code`` (e.g. INQ20260001) is the parent-facing identifier.
  ``id`` remains the internal primary key for foreign keys and staff tools.
    """

    __tablename__ = "student_inquiries"
    __table_args__ = (
        UniqueConstraint("inquiry_code", name="uq_student_inquiry_code"),
        UniqueConstraint("serial_number", name="uq_student_inquiry_serial"),
        Index("ix_student_inquiry_status", "status"),
        Index("ix_student_inquiry_parent_mobile", "parent_mobile"),
        Index("ix_student_inquiry_email", "email"),
        {"comment": "Public student admission inquiries and their current pipeline status"},
    )

    # --- Primary key ---
    id: Mapped[int] = mapped_column(
        BigInt,
        primary_key=True,
        autoincrement=True,
        comment="Internal surrogate primary key",
    )

    # --- Business identifiers (auto-generated on create) ---
    inquiry_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Human-readable inquiry ID shown to parents, e.g. INQ20260001",
    )
    serial_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Monotonic serial used when generating inquiry_code for the academic year",
    )

    # --- Student profile (from public form) ---
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Student given name",
    )
    middle_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Student middle name (optional)",
    )
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Student family name",
    )
    gender: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=Gender.MALE.value,
        comment="Student gender (male, female, other)",
    )
    father_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Father or legal guardian full name",
    )
    date_of_birth: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Student date of birth",
    )

    # --- Contact ---
    student_mobile: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        comment="Student mobile number (optional)",
    )
    parent_mobile: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Primary parent/guardian mobile for verification and contact",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Parent or student email used for status updates and verification",
    )
    address: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Residential address",
    )

    # --- Academic background ---
    last_school: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Name of the school the student last attended",
    )
    current_class: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Class/grade the student is currently in (free text from applicant)",
    )
    admission_for_class: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Class/grade the student is applying for (free text from applicant)",
    )
    last_school_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Previous school percentage or grade (optional)",
    )

    # --- Optional link to structured class catalog (resolved by staff later) ---
    admission_for_class_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("classes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to classes.id when admission target is mapped to catalog",
    )

    # --- Workflow ---
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=InquiryStatus.PENDING.value,
        comment="Current inquiry pipeline status (see InquiryStatus enum)",
    )
    rejection_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Reason shown to parent when status is REJECTED",
    )
    internal_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Staff-only notes; never exposed on public APIs",
    )

    # --- Relationships ---
    target_class: Mapped["Class | None"] = relationship(
        "Class",
        foreign_keys=[admission_for_class_id],
        back_populates="inquiries",
    )
    status_history: Mapped[list["InquiryStatusHistory"]] = relationship(
        "InquiryStatusHistory",
        back_populates="inquiry",
        order_by="InquiryStatusHistory.created_at",
        cascade="all, delete-orphan",
    )
    interviews: Mapped[list["InterviewSchedule"]] = relationship(
        "InterviewSchedule",
        back_populates="inquiry",
        order_by="InterviewSchedule.schedule_date",
    )
    admission: Mapped["InquiryAdmission | None"] = relationship(
        "InquiryAdmission",
        back_populates="inquiry",
        uselist=False,
    )


class InquiryStatusHistory(Base):
    """
    Append-only audit of inquiry status transitions.

    Each row captures one change (including the initial PENDING state on create).
    """

    __tablename__ = "inquiry_status_history"
    __table_args__ = (
        Index("ix_inquiry_status_history_inquiry_id", "inquiry_id"),
        {"comment": "Historical log of student inquiry status changes"},
    )

    id: Mapped[int] = mapped_column(
        BigInt,
        primary_key=True,
        autoincrement=True,
        comment="Surrogate primary key for this history row",
    )
    inquiry_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("student_inquiries.id", ondelete="CASCADE"),
        nullable=False,
        comment="FK to student_inquiries.id",
    )
    from_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Previous status; null on initial creation",
    )
    to_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="New status after this transition",
    )
    changed_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="Staff user who performed the change; null for system/public actions",
    )
    change_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Optional reason or note for this transition",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When this transition was recorded",
    )

    inquiry: Mapped["StudentInquiry"] = relationship(
        "StudentInquiry",
        back_populates="status_history",
    )
    changed_by_user: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[changed_by],
    )
