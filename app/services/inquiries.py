"""
Business logic for student admission inquiries.

Handles public submission, parent updates, staff review, and status history.
"""

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AuthenticationException,
    BusinessRuleException,
    ConflictException,
    NotFoundException,
)
from app.core.pagination import PaginatedResult, PaginationParams
from app.core.transactions import transaction
from app.models.enums import (
    INQUIRY_ADMIN_TRANSITIONS,
    INQUIRY_LOCKED_STATUSES,
    ClassStatus,
    InquiryStatus,
)
from app.models.student_inquiry import StudentInquiry
from app.repositories.classes import ClassRepository
from app.repositories.inquiries import (
    InquiryStatusHistoryRepository,
    StudentInquiryRepository,
)
from app.schemas.inquiries import (
    AdminInquiryUpdateRequest,
    PublicInquiryCreateRequest,
    PublicInquiryUpdateRequest,
)
from app.services.audit import AuditService
from app.utils.inquiry_ids import generate_inquiry_identifiers


class InquiryService:
    """Orchestrates inquiry lifecycle, status transitions, and audit logging."""

    def __init__(self, session: Session) -> None:
        self.session = session
        # Repository aliases: some methods use `repo`, others expect `inquiries`
        self.repo = StudentInquiryRepository(session)
        self.inquiries = self.repo
        self.history = InquiryStatusHistoryRepository(session)
        self.classes = ClassRepository(session)
        self.audit = AuditService(session)

    def create_public_inquiry(
        self,
        payload: PublicInquiryCreateRequest,
        request: Request,
    ) -> StudentInquiry:
        """
        Create a new inquiry from the public form.

        Validates no duplicate inquiry exists using:
        - Student first_name, last_name
        - Father name
        - Date of birth (case-insensitive name matching)

        Sets status to PENDING, generates inquiry_code, and writes initial history.
        """
        # Check for duplicate inquiry before proceeding
        existing_inquiry = self.repo.find_duplicate_inquiry(
            first_name=payload.first_name,
            last_name=payload.last_name,
            father_name=payload.father_name,
            date_of_birth=payload.dob,
        )
        if existing_inquiry:
            raise ConflictException(
                "Student inquiry already exists. Please contact school administration."
            )

        if payload.admission_for_class_id:
            school_class = self.classes.get_active(payload.admission_for_class_id)
            if not school_class or school_class.status != ClassStatus.ACTIVE.value:
                raise NotFoundException("Admission target class not found in catalog")

        with transaction(self.session):
            inquiry_code, serial_number = generate_inquiry_identifiers(self.session)
            inquiry = self.repo.create(
                StudentInquiry(
                    inquiry_code=inquiry_code,
                    serial_number=serial_number,
                    first_name=payload.first_name,
                    middle_name=payload.middle_name,
                    last_name=payload.last_name,
                    gender=payload.gender.value,
                    father_name=payload.father_name,
                    date_of_birth=payload.dob,
                    student_mobile=payload.student_mobile,
                    parent_mobile=payload.parent_mobile,
                    email=str(payload.email),
                    address=payload.address,
                    last_school=payload.last_school,
                    current_class=payload.current_class,
                    admission_for_class=payload.admission_for_class,
                    last_school_percentage=payload.last_school_percentage,
                    admission_for_class_id=payload.admission_for_class_id,
                    status=InquiryStatus.PENDING.value,
                )
            )
            self._record_status(
                inquiry=inquiry,
                from_status=None,
                to_status=InquiryStatus.PENDING.value,
                change_reason="Inquiry submitted via public form",
            )
            self.audit.log(
                action="inquiry.create.public",
                entity_type="student_inquiry",
                entity_id=inquiry.id,
                new_values={"inquiry_code": inquiry.inquiry_code, "status": inquiry.status},
                request=request,
            )
            return inquiry

    def get_public_status(self, inquiry_code: str) -> StudentInquiry:
        """Return inquiry with history for parent status check (no staff fields)."""
        normalized_code = inquiry_code.strip().upper()
        inquiry = self.repo.get_by_code_with_history(normalized_code)
        if not inquiry:
            raise NotFoundException("Inquiry not found")
        return inquiry

    def update_public_inquiry(
        self,
        payload: PublicInquiryUpdateRequest,
        request: Request,
    ) -> StudentInquiry:
        """
        Update inquiry details after verifying inquiry_code, email, and parent_mobile.
        """
        inquiry = self.repo.verify_parent_credentials(
            payload.inquiry_code,
            str(payload.email),
            payload.parent_mobile,
        )
        if not inquiry:
            raise AuthenticationException(
                "Invalid inquiry credentials. Check inquiry ID, email, and parent mobile.",
            )
        if inquiry.status in INQUIRY_LOCKED_STATUSES:
            raise BusinessRuleException(
                f"Inquiry cannot be modified while status is {inquiry.status}",
            )

        with transaction(self.session):
            for field, attr in (
                ("first_name", "first_name"),
                ("middle_name", "middle_name"),
                ("last_name", "last_name"),
                ("father_name", "father_name"),
                ("dob", "date_of_birth"),
                ("student_mobile", "student_mobile"),
                ("address", "address"),
                ("last_school", "last_school"),
                ("current_class", "current_class"),
                ("admission_for_class", "admission_for_class"),
                ("last_school_percentage", "last_school_percentage"),
            ):
                value = getattr(payload, field)
                if value is not None:
                    setattr(inquiry, attr, value)
            if payload.gender is not None:
                inquiry.gender = payload.gender.value
            inquiry = self.repo.update(inquiry)
            self.audit.log(
                action="inquiry.update.public",
                entity_type="student_inquiry",
                entity_id=inquiry.id,
                request=request,
            )
            return inquiry

    def list_inquiries(
        self,
        params: PaginationParams,
        status: str | None = None,
        admission_for_class_id: int | None = None,
        search: str | None = None,
    ) -> PaginatedResult:
        """Staff paginated list."""
        return self.repo.list_filtered(params, status, admission_for_class_id, search)

    def get_inquiry(self, inquiry_id: int) -> StudentInquiry:
        """Staff fetch by internal id."""
        inquiry = self.repo.get_by_id_with_relations(inquiry_id)
        if not inquiry:
            raise NotFoundException("Inquiry not found")
        return inquiry

    def update_inquiry_admin(
        self,
        inquiry_id: int,
        payload: AdminInquiryUpdateRequest,
        actor_id: int,
        request: Request,
    ) -> StudentInquiry:
        """Staff-only updates (class mapping, internal notes)."""
        inquiry = self.get_inquiry(inquiry_id)
        with transaction(self.session):
            if payload.admission_for_class_id is not None:
                school_class = self.classes.get_active(payload.admission_for_class_id)
                if not school_class:
                    raise NotFoundException("Class not found")
                inquiry.admission_for_class_id = payload.admission_for_class_id
            if payload.internal_notes is not None:
                inquiry.internal_notes = payload.internal_notes
            inquiry = self.repo.update(inquiry)
            self.audit.log(
                action="inquiry.update.admin",
                entity_type="student_inquiry",
                entity_id=inquiry.id,
                actor_user_id=actor_id,
                request=request,
            )
            return inquiry

    def transition_status(
        self,
        inquiry_id: int,
        new_status: str,
        actor_id: int | None,
        request: Request,
        change_reason: str | None = None,
        rejection_reason: str | None = None,
        *,
        manage_transaction: bool = True,
    ) -> StudentInquiry:
        """
        Move inquiry to a new status if the transition is allowed.

        Set ``manage_transaction=False`` when called from another service that
        already owns the database transaction.
        """

        def _apply() -> StudentInquiry:
            inquiry = self.inquiries.get_by_id(inquiry_id)
            if not inquiry:
                raise NotFoundException("Inquiry not found")
            if new_status == InquiryStatus.REJECTED.value:
                if inquiry.status in INQUIRY_LOCKED_STATUSES:
                    raise BusinessRuleException("Inquiry is already in a terminal state")
            else:
                allowed = INQUIRY_ADMIN_TRANSITIONS.get(inquiry.status, set())
                if new_status not in allowed:
                    raise BusinessRuleException(
                        f"Cannot transition from {inquiry.status} to {new_status}",
                    )
            old_status = inquiry.status
            inquiry.status = new_status
            if new_status == InquiryStatus.REJECTED.value:
                if not rejection_reason:
                    raise BusinessRuleException("Rejection reason is required")
                inquiry.rejection_reason = rejection_reason
            inquiry = self.repo.update(inquiry)
            self._record_status(
                inquiry=inquiry,
                from_status=old_status,
                to_status=new_status,
                changed_by=actor_id,
                change_reason=change_reason or rejection_reason,
            )
            self.audit.log(
                action="inquiry.status_change",
                entity_type="student_inquiry",
                entity_id=inquiry.id,
                actor_user_id=actor_id,
                old_values={"status": old_status},
                new_values={"status": new_status},
                request=request,
            )
            return inquiry

        if manage_transaction:
            with transaction(self.session):
                return _apply()
        return _apply()

    def start_review(self, inquiry_id: int, actor_id: int, request: Request, notes: str | None) -> StudentInquiry:
        """Admin: PENDING → UNDER_REVIEW."""
        return self.transition_status(
            inquiry_id,
            InquiryStatus.UNDER_REVIEW.value,
            actor_id,
            request,
            change_reason=notes or "Review started",
        )

    def mark_processing(self, inquiry_id: int, actor_id: int, request: Request, notes: str | None) -> StudentInquiry:
        """Admin: UNDER_REVIEW → PROCESSING."""
        return self.transition_status(
            inquiry_id,
            InquiryStatus.PROCESSING.value,
            actor_id,
            request,
            change_reason=notes or "Marked eligible for processing",
        )

    def reject_inquiry(
        self,
        inquiry_id: int,
        rejection_reason: str,
        actor_id: int,
        request: Request,
    ) -> StudentInquiry:
        """Admin: any non-terminal → REJECTED."""
        inquiry = self.get_inquiry(inquiry_id)
        if inquiry.status in INQUIRY_LOCKED_STATUSES:
            raise BusinessRuleException("Inquiry is already in a terminal state")
        return self.transition_status(
            inquiry_id,
            InquiryStatus.REJECTED.value,
            actor_id,
            request,
            rejection_reason=rejection_reason,
        )

    def _record_status(
        self,
        *,
        inquiry: StudentInquiry,
        from_status: str | None,
        to_status: str,
        changed_by: int | None = None,
        change_reason: str | None = None,
    ) -> None:
        """Append one row to inquiry_status_history."""
        self.history.add_transition(
            inquiry_id=inquiry.id,
            from_status=from_status,
            to_status=to_status,
            changed_by=changed_by,
            change_reason=change_reason,
        )
