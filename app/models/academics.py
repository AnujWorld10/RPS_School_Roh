from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BIGINT_PK, Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.student import Student


class StudentSubjectSelection(Base, TimestampMixin):
    __tablename__ = "student_subject_selections"
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "class_id",
            "subject_id",
            name="uq_student_subject_selection",
        ),
        ForeignKeyConstraint(
            ["class_id", "subject_id"],
            ["class_subjects.class_id", "class_subjects.subject_id"],
            name="fk_student_subject_selection_offering",
            ondelete="RESTRICT",
        ),
    )

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    class_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    subject_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    selected_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)


class Examination(Base, TimestampMixin):
    __tablename__ = "examinations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'scheduled', 'published', 'locked')",
            name="ck_examinations_status",
        ),
        CheckConstraint(
            "examination_type IN ('unit_test', 'periodic_test', 'term', 'mid_term', "
            "'final_exam', 'practical', 'oral')",
            name="ck_examinations_type",
        ),
        CheckConstraint("start_date <= end_date", name="ck_examinations_date_range"),
        UniqueConstraint("class_id", "name", name="uq_examinations_class_name"),
    )

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    class_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("classes.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    examination_type: Mapped[str] = mapped_column(String(40), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    subjects: Mapped[list["ExaminationSubject"]] = relationship(
        back_populates="examination", cascade="all, delete-orphan"
    )
    results: Mapped[list["ExaminationResult"]] = relationship(
        back_populates="examination", cascade="all, delete-orphan"
    )


class ExaminationSubject(Base, TimestampMixin):
    __tablename__ = "examination_subjects"
    __table_args__ = (
        UniqueConstraint("examination_id", "subject_id", name="uq_examination_subject"),
        ForeignKeyConstraint(
            ["class_id", "subject_id"],
            ["class_subjects.class_id", "class_subjects.subject_id"],
            name="fk_examination_subject_offering",
            ondelete="RESTRICT",
        ),
        CheckConstraint("max_marks > 0", name="ck_examination_subject_max_positive"),
        CheckConstraint(
            "passing_marks >= 0 AND passing_marks <= max_marks",
            name="ck_examination_subject_pass_range",
        ),
    )

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    examination_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("examinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    class_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    subject_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    teacher_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True
    )
    max_marks: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    passing_marks: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    components: Mapped[list["ExaminationComponent"]] = relationship(
        back_populates="examination_subject", cascade="all, delete-orphan"
    )
    examination: Mapped[Examination] = relationship(back_populates="subjects")


class ExaminationComponent(Base, TimestampMixin):
    __tablename__ = "examination_components"
    __table_args__ = (
        UniqueConstraint("examination_subject_id", "name", name="uq_examination_component_name"),
        CheckConstraint(
            "component_type IN ('theory', 'practical', 'internal', 'combined')",
            name="ck_examination_component_type",
        ),
        CheckConstraint("max_marks > 0", name="ck_examination_component_max_positive"),
        CheckConstraint(
            "passing_marks >= 0 AND passing_marks <= max_marks",
            name="ck_examination_component_pass_range",
        ),
    )

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    examination_subject_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("examination_subjects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    component_type: Mapped[str] = mapped_column(String(20), nullable=False)
    max_marks: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    passing_marks: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    examination_subject: Mapped[ExaminationSubject] = relationship(back_populates="components")


class StudentMark(Base, TimestampMixin):
    __tablename__ = "student_marks"
    __table_args__ = (
        UniqueConstraint("component_id", "student_id", name="uq_student_mark_component_student"),
        CheckConstraint(
            "result_status IN ('PASS', 'FAIL', 'ABSENT', 'EXEMPTED')",
            name="ck_student_marks_result_status",
        ),
        CheckConstraint(
            "obtained_marks IS NULL OR obtained_marks >= 0", name="ck_student_marks_nonnegative"
        ),
    )

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    component_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("examination_components.id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    obtained_marks: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    result_status: Mapped[str] = mapped_column(String(10), nullable=False)
    remarks: Mapped[str | None] = mapped_column(String(500), nullable=True)
    entered_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    grade: Mapped[str | None] = mapped_column(String(10), nullable=True)


class GradingRule(Base, TimestampMixin):
    __tablename__ = "grading_rules"
    __table_args__ = (
        UniqueConstraint("scale_code", "grade", name="uq_grading_rule_scale_grade"),
        CheckConstraint(
            "minimum_percentage >= 0 AND maximum_percentage <= 100 "
            "AND minimum_percentage <= maximum_percentage",
            name="ck_grading_rule_percentage_range",
        ),
    )

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    scale_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    grade: Mapped[str] = mapped_column(String(10), nullable=False)
    minimum_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    maximum_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)


class ExaminationResult(Base, TimestampMixin):
    __tablename__ = "examination_results"
    __table_args__ = (
        UniqueConstraint("examination_id", "student_id", name="uq_examination_result_student"),
        CheckConstraint(
            "result_status IN ('PASS', 'FAIL')",
            name="ck_examination_results_status",
        ),
    )

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    examination_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("examinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    total_max_marks: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_obtained_marks: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    grade: Mapped[str] = mapped_column(String(10), nullable=False)
    result_status: Mapped[str] = mapped_column(String(10), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    examination: Mapped[Examination] = relationship(back_populates="results")
    student: Mapped["Student"] = relationship()
