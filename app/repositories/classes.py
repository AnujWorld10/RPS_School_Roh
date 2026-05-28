from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.pagination import PaginatedResult, PaginationParams
from app.models.class_model import Class
from app.models.student import Student
from app.models.enums import StudentStatus
from app.repositories.base import BaseRepository


class ClassRepository(BaseRepository[Class]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Class)

    def exists_duplicate(
        self,
        name: str,
        section: str | None,
        academic_year: str,
        exclude_id: int | None = None,
    ) -> bool:
        stmt = select(Class.id).where(
            Class.name == name,
            Class.section == section,
            Class.academic_year == academic_year,
            Class.deleted_at.is_(None),
        )
        if exclude_id:
            stmt = stmt.where(Class.id != exclude_id)
        return self.session.scalar(stmt) is not None

    def list_filtered(
        self,
        params: PaginationParams,
        academic_year: str | None = None,
        status: str | None = None,
    ) -> PaginatedResult:
        stmt = select(Class).where(Class.deleted_at.is_(None))
        if academic_year:
            stmt = stmt.where(Class.academic_year == academic_year)
        if status:
            stmt = stmt.where(Class.status == status)
        return self.paginate(stmt, params)

    def count_active_students(self, class_id: int) -> int:
        from sqlalchemy import or_

        stmt = select(func.count()).select_from(Student).where(
            or_(Student.class_id == class_id, Student.current_class_id == class_id),
            Student.deleted_at.is_(None),
            Student.status == StudentStatus.ACTIVE.value,
        )
        return self.session.scalar(stmt) or 0

    def get_active(self, class_id: int) -> Class | None:
        entity = self.get_by_id(class_id)
        if entity and entity.deleted_at is None:
            return entity
        return None
