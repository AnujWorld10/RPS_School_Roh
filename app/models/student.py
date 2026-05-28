"""
ORM model for enrolled students (post-admission).
"""

from datetime import date

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin
from app.models.enums import StudentStatus


class Student(Base, TimestampMixin, SoftDeleteMixin):
    """
    Enrolled student record created from a successful admission.

    ``student_code`` (e.g. STU202600001) and ``roll_number`` are assigned at enrollment.
    """

    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("student_code", name="uq_student_code"),
        UniqueConstraint(
            "class_id",
            "academic_year",
            "roll_number",
            name="uq_student_roll_per_class_year",
        ),
        {"comment": "Enrolled students"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Internal surrogate primary key",
    )
    student_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Business ID e.g. STU202600001",
    )
    inquiry_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("student_inquiries.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        comment="Originating inquiry if applicable",
    )
    admission_no: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
        comment="Legacy/alternate admission number",
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    class_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("classes.id"),
        nullable=True,
        index=True,
        comment="Current class FK",
    )
    academic_year: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Active academic year for roll number scope",
    )
    roll_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Roll number unique within class + academic year",
    )
    # Deprecated alias — use class_id; kept for migration compatibility.
    current_class_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("classes.id"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=StudentStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )

    current_class: Mapped["Class | None"] = relationship(  # noqa: F821
        foreign_keys=[class_id],
        back_populates="students",
    )
    inquiry_admission: Mapped["InquiryAdmission | None"] = relationship(  # noqa: F821
        back_populates="student",
        uselist=False,
    )
    legacy_admissions: Mapped[list["StudentAdmission"]] = relationship(  # noqa: F821
        back_populates="student",
    )
