from sqlalchemy import exists, false, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.pagination import PaginatedResult, PaginationParams
from app.models.student import Student
from app.models.student_inquiry import StudentInquiry
from app.models.user import User
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Student)

    def get_active(self, student_id: int) -> Student | None:
        entity = self.get_by_id(student_id)
        if entity and entity.deleted_at is None:
            return entity
        return None

    def get_active_for_user(
        self,
        student_id: int,
        user: User,
        role_codes: set[str],
    ) -> Student | None:
        ownership = self._ownership_filter(user, role_codes)
        if ownership is None:
            return self.get_active(student_id)
        stmt = select(Student).where(
            Student.id == student_id,
            Student.deleted_at.is_(None),
            ownership,
        )
        return self.session.scalar(stmt)

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
        user: User | None = None,
        role_codes: set[str] | None = None,
    ) -> PaginatedResult:
        stmt = (
            select(Student)
            .where(Student.deleted_at.is_(None))
            .options(selectinload(Student.current_class))
        )
        ownership = (
            self._ownership_filter(user, role_codes or set())
            if user is not None
            else None
        )
        if ownership is not None:
            stmt = stmt.where(ownership)
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

    @staticmethod
    def _ownership_filter(user: User, role_codes: set[str]):
        scoped_roles = {"STUDENT", "PARENT"}
        if not role_codes.intersection(scoped_roles):
            return None

        filters = []
        if "STUDENT" in role_codes:
            filters.append(Student.email == user.email)

        if "PARENT" in role_codes and user.phone:
            filters.append(
                exists(
                    select(StudentInquiry.id).where(
                        StudentInquiry.id == Student.inquiry_id,
                        StudentInquiry.email == user.email,
                        StudentInquiry.parent_mobile == user.phone,
                    )
                )
            )

        if not filters:
            return false()
        return or_(*filters)
