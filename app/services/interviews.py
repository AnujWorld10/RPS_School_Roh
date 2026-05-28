"""
Business logic for scheduling interviews and recording results.
"""

from datetime import date, time

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleException, NotFoundException
from app.core.transactions import transaction
from app.models.enums import InquiryStatus, InterviewMode, InterviewResult
from app.models.interview import InterviewSchedule
from app.repositories.interviews import InterviewRepository
from app.repositories.inquiries import StudentInquiryRepository
from app.repositories.teachers import TeacherRepository
from app.schemas.interviews import InterviewCreateRequest, InterviewResultUpdateRequest
from app.services.audit import AuditService
from app.services.inquiries import InquiryService


class InterviewService:
    """Schedule interviews and sync inquiry status on outcomes."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = InterviewRepository(session)
        self.inquiries = StudentInquiryRepository(session)
        self.teachers = TeacherRepository(session)
        self.inquiry_service = InquiryService(session)
        self.audit = AuditService(session)

    def schedule_interview(
        self,
        inquiry_id: int,
        payload: InterviewCreateRequest,
        actor_id: int,
        request: Request,
    ) -> InterviewSchedule:
        """
        Create an interview and move inquiry to INTERVIEW_SCHEDULED.

        Inquiry must be in PROCESSING or already INTERVIEW_SCHEDULED (reschedule).
        """
        inquiry = self.inquiries.get_by_id(inquiry_id)
        if not inquiry:
            raise NotFoundException("Inquiry not found")
        allowed = {InquiryStatus.PROCESSING.value, InquiryStatus.INTERVIEW_SCHEDULED.value}
        if inquiry.status not in allowed:
            raise BusinessRuleException(
                f"Cannot schedule interview while inquiry status is {inquiry.status}",
            )
        if payload.interviewer_teacher_id:
            teacher = self.teachers.get_by_id(payload.interviewer_teacher_id)
            if not teacher:
                raise NotFoundException("Interviewer teacher not found")

        with transaction(self.session):
            interview = self.repo.create(
                InterviewSchedule(
                    inquiry_id=inquiry_id,
                    schedule_date=payload.schedule_date,
                    schedule_time=payload.schedule_time,
                    location=payload.location,
                    mode=payload.mode.value,
                    interviewer_teacher_id=payload.interviewer_teacher_id,
                    remarks=payload.remarks,
                    result=InterviewResult.SCHEDULED.value,
                )
            )
            if inquiry.status != InquiryStatus.INTERVIEW_SCHEDULED.value:
                self.inquiry_service.transition_status(
                    inquiry_id,
                    InquiryStatus.INTERVIEW_SCHEDULED.value,
                    actor_id,
                    request,
                    change_reason="Interview scheduled",
                    manage_transaction=False,
                )
            self.audit.log(
                action="interview.schedule",
                entity_type="interview_schedule",
                entity_id=interview.id,
                actor_user_id=actor_id,
                new_values={"inquiry_id": inquiry_id},
                request=request,
            )
            return interview

    def record_result(
        self,
        interview_id: int,
        payload: InterviewResultUpdateRequest,
        actor_id: int,
        request: Request,
    ) -> InterviewSchedule:
        """
        Set interview result and update inquiry to INTERVIEW_PASS or INTERVIEW_FAIL.
        """
        interview = self.repo.get_with_relations(interview_id)
        if not interview:
            raise NotFoundException("Interview not found")
        if interview.result != InterviewResult.SCHEDULED.value:
            raise BusinessRuleException("Interview result has already been recorded")

        result = payload.result.value
        inquiry_id = interview.inquiry_id

        with transaction(self.session):
            interview.result = result
            interview.remarks = payload.remarks or interview.remarks
            interview = self.repo.update(interview)

            if result == InterviewResult.PASSED.value:
                self.inquiry_service.transition_status(
                    inquiry_id,
                    InquiryStatus.INTERVIEW_PASS.value,
                    actor_id,
                    request,
                    change_reason=payload.remarks or "Interview passed",
                    manage_transaction=False,
                )
            elif result in (InterviewResult.FAILED.value, InterviewResult.ABSENT.value):
                self.inquiry_service.transition_status(
                    inquiry_id,
                    InquiryStatus.INTERVIEW_FAIL.value,
                    actor_id,
                    request,
                    change_reason=payload.remarks or f"Interview {result.lower()}",
                    manage_transaction=False,
                )

            self.audit.log(
                action="interview.result",
                entity_type="interview_schedule",
                entity_id=interview.id,
                actor_user_id=actor_id,
                new_values={"result": result},
                request=request,
            )
            return interview

    def list_for_inquiry(self, inquiry_id: int) -> list[InterviewSchedule]:
        """Return all interviews for an inquiry."""
        if not self.inquiries.get_by_id(inquiry_id):
            raise NotFoundException("Inquiry not found")
        return self.repo.list_for_inquiry(inquiry_id)

    def get_interview(self, interview_id: int) -> InterviewSchedule:
        interview = self.repo.get_with_relations(interview_id)
        if not interview:
            raise NotFoundException("Interview not found")
        return interview
