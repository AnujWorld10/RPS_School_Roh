"""
ORM model for interview / test scheduling tied to a student inquiry.

Supports multiple rows per inquiry (reschedule, retest).
"""

from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, ForeignKey, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, BigInt, TimestampMixin
from app.models.enums import InterviewMode, InterviewResult

if TYPE_CHECKING:
    from app.models.student_inquiry import StudentInquiry
    from app.models.teacher import Teacher


class InterviewSchedule(Base, TimestampMixin):
    """
    One scheduled interview or entrance test for a student inquiry.

    When result becomes PASSED or FAILED, ``InterviewService`` updates the
    parent inquiry status accordingly.
    """

    __tablename__ = "interview_schedules"
    __table_args__ = {"comment": "Interview and test appointments for student inquiries"}

    id: Mapped[int] = mapped_column(
        BigInt,
        primary_key=True,
        autoincrement=True,
        comment="Surrogate primary key",
    )
    inquiry_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("student_inquiries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to student_inquiries.id",
    )
    schedule_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Calendar date of the interview",
    )
    schedule_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
        comment="Local time of the interview",
    )
    location: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Venue or meeting link description",
    )
    mode: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=InterviewMode.OFFLINE.value,
        comment="ONLINE or OFFLINE",
    )
    interviewer_teacher_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("teachers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Optional FK to assigned interviewer",
    )
    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Staff notes about this schedule",
    )
    result: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=InterviewResult.SCHEDULED.value,
        index=True,
        comment="SCHEDULED, PASSED, FAILED, or ABSENT",
    )

    inquiry: Mapped["StudentInquiry"] = relationship(
        "StudentInquiry",
        back_populates="interviews",
    )
    interviewer: Mapped["Teacher | None"] = relationship(
        "Teacher",
        foreign_keys=[interviewer_teacher_id],
    )
