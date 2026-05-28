from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.pagination import PaginatedResult, PaginationParams
from app.models.student import Student
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Student)

    def get_active(self, student_id: int) -> Student | None:
        entity = self.get_by_id(student_id)
        if entity and entity.deleted_at is None:
            return entity
        return None

    def admission_no_exists(self, admission_no: str, exclude_id: int | None = None) -> bool:
        stmt = select(Student.id).where(
            Student.admission_no == admission_no,
            Student.deleted_at.is_(None),
        )
        if exclude_id:
            stmt = stmt.where(Student.id != exclude_id)
        return self.session.scalar(stmt) is not None

    def list_filtered(
        self,
        params: PaginationParams,
        status: str | None = None,
        current_class_id: int | None = None,
        search: str | None = None,
    ) -> PaginatedResult:
        stmt = select(Student).where(Student.deleted_at.is_(None))
        if status:
            stmt = stmt.where(Student.status == status)
        if current_class_id:
            stmt = stmt.where(Student.current_class_id == current_class_id)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Student.first_name.like(pattern),
                    Student.last_name.like(pattern),
                    Student.admission_no.like(pattern),
                )
            )
        return self.paginate(stmt, params)
