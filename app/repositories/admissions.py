from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.pagination import PaginatedResult, PaginationParams
from app.models.admission import StudentAdmission
from app.models.enums import AdmissionStatus
from app.repositories.base import BaseRepository


class AdmissionRepository(BaseRepository[StudentAdmission]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, StudentAdmission)

    def get_for_student(self, student_id: int) -> StudentAdmission | None:
        stmt = (
            select(StudentAdmission)
            .where(StudentAdmission.student_id == student_id)
            .order_by(StudentAdmission.created_at.desc())
        )
        return self.session.scalar(stmt)

    def exists_for_year(self, student_id: int, academic_year: str) -> bool:
        stmt = select(StudentAdmission.id).where(
            StudentAdmission.student_id == student_id,
            StudentAdmission.academic_year == academic_year,
            StudentAdmission.status != AdmissionStatus.REJECTED.value,
        )
        return self.session.scalar(stmt) is not None

    def list_filtered(
        self,
        params: PaginationParams,
        status: str | None = None,
        academic_year: str | None = None,
    ) -> PaginatedResult:
        stmt = select(StudentAdmission)
        if status:
            stmt = stmt.where(StudentAdmission.status == status)
        if academic_year:
            stmt = stmt.where(StudentAdmission.academic_year == academic_year)
        return self.paginate(stmt, params)
