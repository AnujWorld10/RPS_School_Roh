from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BIGINT_PK, Base, TimestampMixin


class Assignment(Base, TimestampMixin):
    __tablename__ = "assignments"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'published', 'closed')",
            name="ck_assignments_status",
        ),
        ForeignKeyConstraint(
            ["class_id", "subject_id"],
            ["class_subjects.class_id", "class_subjects.subject_id"],
            name="fk_assignments_class_subject",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["assigned_teacher_id", "class_id", "subject_id"],
            [
                "teacher_class_subjects.teacher_id",
                "teacher_class_subjects.class_id",
                "teacher_class_subjects.subject_id",
            ],
            name="fk_assignments_teacher_class_subject",
            ondelete="RESTRICT",
        ),
        {"comment": "Class and subject assignments created by mapped teachers"},
    )

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False)
    class_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    subject_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    assigned_teacher_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    assigned_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
    )
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    attachments: Mapped[list["AssignmentAttachment"]] = relationship(
        back_populates="assignment",
        cascade="all, delete-orphan",
    )


class AssignmentAttachment(Base, TimestampMixin):
    __tablename__ = "assignment_attachments"

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    assignment_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("assignments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    assignment: Mapped[Assignment] = relationship(back_populates="attachments")


class TimetableEntry(Base, TimestampMixin):
    __tablename__ = "timetable_entries"
    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 0 AND 6", name="ck_timetable_day_of_week"),
        CheckConstraint("start_time < end_time", name="ck_timetable_time_order"),
        ForeignKeyConstraint(
            ["class_id", "subject_id"],
            ["class_subjects.class_id", "class_subjects.subject_id"],
            name="fk_timetable_class_subject",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["teacher_id", "class_id", "subject_id"],
            [
                "teacher_class_subjects.teacher_id",
                "teacher_class_subjects.class_id",
                "teacher_class_subjects.subject_id",
            ],
            name="fk_timetable_teacher_class_subject",
            ondelete="RESTRICT",
        ),
        {"comment": "Weekly class timetable entries"},
    )

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    subject_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    teacher_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    room: Mapped[str | None] = mapped_column(String(100), nullable=True)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class Assessment(Base, TimestampMixin):
    __tablename__ = "assessments"
    __table_args__ = (
        CheckConstraint(
            "assessment_type IN ('unit_test', 'periodic_test', 'mid_term', 'final_exam', "
            "'assignment', 'quiz', 'practical', 'oral')",
            name="ck_assessments_type",
        ),
        CheckConstraint("max_score > 0", name="ck_assessments_max_score_positive"),
        ForeignKeyConstraint(
            ["class_id", "subject_id"],
            ["class_subjects.class_id", "class_subjects.subject_id"],
            name="fk_assessments_class_subject",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["teacher_id", "class_id", "subject_id"],
            [
                "teacher_class_subjects.teacher_id",
                "teacher_class_subjects.class_id",
                "teacher_class_subjects.subject_id",
            ],
            name="fk_assessments_teacher_class_subject",
            ondelete="RESTRICT",
        ),
        {"comment": "Class assessments and publication state"},
    )

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    assessment_type: Mapped[str] = mapped_column(String(30), nullable=False)
    class_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    subject_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    teacher_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    assessment_date: Mapped[date] = mapped_column(Date, nullable=False)
    max_score: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    results: Mapped[list["AssessmentResult"]] = relationship(
        back_populates="assessment",
        cascade="all, delete-orphan",
    )


class AssessmentResult(Base, TimestampMixin):
    __tablename__ = "assessment_results"
    __table_args__ = (
        UniqueConstraint("assessment_id", "student_id", name="uq_assessment_result_student"),
        CheckConstraint(
            "result_status IN ('present', 'absent')",
            name="ck_assessment_result_status",
        ),
        CheckConstraint("score IS NULL OR score >= 0", name="ck_assessment_result_nonnegative"),
        {"comment": "Student assessment scores and absence records"},
    )

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    assessment_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    result_status: Mapped[str] = mapped_column(String(10), nullable=False, default="present")
    remarks: Mapped[str | None] = mapped_column(String(500), nullable=True)
    entered_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    assessment: Mapped[Assessment] = relationship(back_populates="results")


class SchoolEvent(Base, TimestampMixin):
    __tablename__ = "school_events"
    __table_args__ = (
        CheckConstraint("starts_at < ends_at", name="ck_school_events_time_order"),
        CheckConstraint(
            "audience IN ('public', 'students', 'parents', 'all')",
            name="ck_school_events_audience",
        ),
        CheckConstraint(
            "status IN ('pending_review', 'published', 'rejected')",
            name="ck_school_events_status",
        ),
        {"comment": "School events with administrator publication review"},
    )

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    venue: Mapped[str | None] = mapped_column(String(200), nullable=True)
    audience: Mapped[str] = mapped_column(String(20), nullable=False, default="all")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending_review")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
