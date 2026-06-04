"""
ORM models for inquiry-linked admission and document verification.

Flow: inquiry (interview pass) → admission application → documents → enrollment.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BigInt, TimestampMixin
from app.models.enums import AdmissionStatus, DocumentVerificationStatus

if TYPE_CHECKING:
    from app.models.class_model import Class
    from app.models.student import Student
    from app.models.student_inquiry import StudentInquiry
    from app.models.user import User


class InquiryAdmission(Base, TimestampMixin):
    """
    Formal admission application created after a successful interview.

    ``student_id`` is populated only after enrollment completes.
    """

    __tablename__ = "inquiry_admissions"
    __table_args__ = (
        UniqueConstraint("inquiry_id", name="uq_inquiry_admission_inquiry"),
        UniqueConstraint("admission_code", name="uq_inquiry_admission_code"),
        {"comment": "Admission applications linked to student inquiries"},
    )

    id: Mapped[int] = mapped_column(
        BigInt,
        primary_key=True,
        autoincrement=True,
        comment="Internal surrogate primary key",
    )
    admission_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Business ID e.g. ADM202600001",
    )
    inquiry_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("student_inquiries.id", ondelete="CASCADE"),
        nullable=False,
        comment="FK to originating student inquiry",
    )
    class_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("classes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Target class for admission",
    )
    section: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Target section within the class",
    )
    academic_year: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Academic session e.g. 2026-2027",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=AdmissionStatus.DRAFT.value,
        nullable=False,
        index=True,
        comment="Admission workflow status",
    )
    permanent_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    temporary_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(100), nullable=True)
    disability: Mapped[str | None] = mapped_column(String(255), nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(10), nullable=True)
    reason_for_school_change: Mapped[str | None] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    student_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        comment="Set after successful enrollment",
    )
    approved_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    inquiry: Mapped["StudentInquiry"] = relationship(
        "StudentInquiry",
        back_populates="admission",
    )
    school_class: Mapped["Class"] = relationship("Class")
    student: Mapped["Student | None"] = relationship("Student", back_populates="inquiry_admission")
    documents: Mapped[list["AdmissionDocument"]] = relationship(
        "AdmissionDocument",
        back_populates="admission",
        cascade="all, delete-orphan",
    )


class AdmissionDocument(Base, TimestampMixin):
    """Uploaded file metadata and verification state for one admission."""

    __tablename__ = "admission_documents"
    __table_args__ = (
        UniqueConstraint("admission_id", "document_type", name="uq_admission_document_type"),
        {"comment": "Admission document uploads and verification"},
    )

    id: Mapped[int] = mapped_column(
        BigInt,
        primary_key=True,
        autoincrement=True,
        comment="Surrogate primary key",
    )
    admission_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("inquiry_admissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to inquiry_admissions.id",
    )
    document_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Document type code (see DocumentType enum)",
    )
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Original uploaded file name",
    )
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Relative or absolute storage path",
    )
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    verification_status: Mapped[str] = mapped_column(
        String(20),
        default=DocumentVerificationStatus.PENDING.value,
        nullable=False,
        index=True,
        comment="PENDING, VERIFIED, or REJECTED",
    )
    verified_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    admission: Mapped["InquiryAdmission"] = relationship(
        "InquiryAdmission",
        back_populates="documents",
    )


# Legacy table kept for backward-compatible migrations; prefer InquiryAdmission.
class StudentAdmission(Base, TimestampMixin):
    """Deprecated: use InquiryAdmission for inquiry-driven admissions."""

    __tablename__ = "student_admissions"
    __table_args__ = (
        UniqueConstraint("student_id", "academic_year", name="uq_student_admission_year"),
    )

    id: Mapped[int] = mapped_column(BigInt, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("students.id"),
        nullable=False,
        index=True,
    )
    class_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("classes.id"), nullable=False)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default=AdmissionStatus.DRAFT.value,
        nullable=False,
        index=True,
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    student: Mapped["Student"] = relationship(back_populates="legacy_admissions")  # noqa: F821
    school_class: Mapped["Class"] = relationship()  # noqa: F821
