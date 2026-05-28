"""Data access for interview_schedules."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.interview import InterviewSchedule
from app.repositories.base import BaseRepository


class InterviewRepository(BaseRepository[InterviewSchedule]):
    """CRUD and queries for interview schedules."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, InterviewSchedule)

    def list_for_inquiry(self, inquiry_id: int) -> list[InterviewSchedule]:
        """All interviews for an inquiry, newest date first."""
        stmt = (
            select(InterviewSchedule)
            .where(InterviewSchedule.inquiry_id == inquiry_id)
            .order_by(InterviewSchedule.schedule_date.desc(), InterviewSchedule.schedule_time.desc())
        )
        return list(self.session.scalars(stmt).all())

    def get_with_relations(self, interview_id: int) -> InterviewSchedule | None:
        """Load interview with inquiry and interviewer."""
        stmt = (
            select(InterviewSchedule)
            .where(InterviewSchedule.id == interview_id)
            .options(
                selectinload(InterviewSchedule.inquiry),
                selectinload(InterviewSchedule.interviewer),
            )
        )
        return self.session.scalar(stmt)

    def get_latest_for_inquiry(self, inquiry_id: int) -> InterviewSchedule | None:
        """Most recent interview row for an inquiry."""
        stmt = (
            select(InterviewSchedule)
            .where(InterviewSchedule.inquiry_id == inquiry_id)
            .order_by(InterviewSchedule.created_at.desc())
            .limit(1)
        )
        return self.session.scalar(stmt)
