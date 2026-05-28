"""
Data access layer for ``student_inquiries`` and ``inquiry_status_history``.
"""

from datetime import date

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.pagination import PaginatedResult, PaginationParams
from app.models.admission import InquiryAdmission
from app.models.student_inquiry import InquiryStatusHistory, StudentInquiry
from app.repositories.base import BaseRepository


class StudentInquiryRepository(BaseRepository[StudentInquiry]):
    """CRUD and query helpers for student admission inquiries."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, StudentInquiry)

    def get_by_id_with_relations(self, inquiry_id: int) -> StudentInquiry | None:
        """Load inquiry by internal PK with class, history, interviews, and admission."""
        stmt = (
            select(StudentInquiry)
            .where(StudentInquiry.id == inquiry_id)
            .options(
                selectinload(StudentInquiry.target_class),
                selectinload(StudentInquiry.status_history),
                selectinload(StudentInquiry.interviews),
                selectinload(StudentInquiry.admission).selectinload(InquiryAdmission.documents),
            )
        )
        return self.session.scalar(stmt)

    def get_by_code_with_history(self, inquiry_code: str) -> StudentInquiry | None:
        """Load inquiry by public inquiry_code with status timeline, interviews, admission."""
        stmt = (
            select(StudentInquiry)
            .where(StudentInquiry.inquiry_code == inquiry_code)
            .options(
                selectinload(StudentInquiry.status_history),
                selectinload(StudentInquiry.interviews),
                selectinload(StudentInquiry.admission).selectinload(
                    InquiryAdmission.documents  # type: ignore[name-defined]
                ),
            )
        )
        return self.session.scalar(stmt)

    def get_by_code(self, inquiry_code: str) -> StudentInquiry | None:
        """Load inquiry by public inquiry_code without eager loads."""
        stmt = select(StudentInquiry).where(StudentInquiry.inquiry_code == inquiry_code)
        return self.session.scalar(stmt)

    def verify_parent_credentials(
        self,
        inquiry_code: str,
        email: str,
        parent_mobile: str,
    ) -> StudentInquiry | None:
        """
        Match inquiry for public update: code + email + parent mobile must match.

        Returns the inquiry row or None if verification fails.
        """
        stmt = select(StudentInquiry).where(
            StudentInquiry.inquiry_code == inquiry_code,
            StudentInquiry.email == email,
            StudentInquiry.parent_mobile == parent_mobile,
        )
        return self.session.scalar(stmt)

    def find_duplicate_inquiry(
        self,
        first_name: str,
        last_name: str,
        father_name: str,
        date_of_birth: date,
    ) -> StudentInquiry | None:
        """
        Check for duplicate inquiry using combination of student identifiers.

        Validates using case-insensitive comparison of:
        - first_name, last_name, father_name, and date_of_birth

        Excludes rejected and failed interview inquiries (allows reapplication).
        Excluded statuses: REJECTED, INTERVIEW_FAIL

        Returns the existing inquiry if found, None otherwise.
        """
        stmt = select(StudentInquiry).where(
            and_(
                StudentInquiry.first_name.ilike(first_name.strip()),
                StudentInquiry.last_name.ilike(last_name.strip()),
                StudentInquiry.father_name.ilike(father_name.strip()),
                StudentInquiry.date_of_birth == date_of_birth,
                # Exclude rejected and failed interviews to allow reapplication
                ~StudentInquiry.status.in_(["REJECTED", "INTERVIEW_FAIL"]),
            )
        )
        return self.session.scalar(stmt)

    def list_filtered(
        self,
        params: PaginationParams,
        status: str | None = None,
        admission_for_class_id: int | None = None,
        search: str | None = None,
    ) -> PaginatedResult:
        """Paginated staff list with optional status, class, and search filters."""
        stmt = select(StudentInquiry)
        if status:
            stmt = stmt.where(StudentInquiry.status == status)
        if admission_for_class_id:
            stmt = stmt.where(StudentInquiry.admission_for_class_id == admission_for_class_id)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    StudentInquiry.first_name.like(pattern),
                    StudentInquiry.last_name.like(pattern),
                    StudentInquiry.inquiry_code.like(pattern),
                    StudentInquiry.email.like(pattern),
                    StudentInquiry.parent_mobile.like(pattern),
                )
            )
        return self.paginate(stmt, params)


class InquiryStatusHistoryRepository(BaseRepository[InquiryStatusHistory]):
    """Append-only writes to inquiry status history."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, InquiryStatusHistory)

    def add_transition(
        self,
        *,
        inquiry_id: int,
        from_status: str | None,
        to_status: str,
        changed_by: int | None = None,
        change_reason: str | None = None,
    ) -> InquiryStatusHistory:
        """Record a single status transition."""
        row = InquiryStatusHistory(
            inquiry_id=inquiry_id,
            from_status=from_status,
            to_status=to_status,
            changed_by=changed_by,
            change_reason=change_reason,
        )
        return self.create(row)
