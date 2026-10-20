from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.pagination import PaginatedResult, PaginationParams
from app.models.class_model import Class
from app.models.enums import ClassStatus, StudentStatus, TeacherStatus
from app.models.student import Student
from app.models.subject import ClassSubject, Subject
from app.models.teacher import Teacher
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

    def count_active_students(
        self,
        class_id: int,
        exclude_student_id: int | None = None,
    ) -> int:
        from sqlalchemy import or_

        stmt = select(func.count()).select_from(Student).where(
            or_(Student.class_id == class_id, Student.current_class_id == class_id),
            Student.deleted_at.is_(None),
            Student.status == StudentStatus.ACTIVE.value,
        )
        if exclude_student_id is not None:
            stmt = stmt.where(Student.id != exclude_student_id)
        return self.session.scalar(stmt) or 0

    def get_active(self, class_id: int) -> Class | None:
        entity = self.get_by_id(class_id)
        if entity and entity.deleted_at is None:
            return entity
        return None

    def get_active_for_update(self, class_id: int) -> Class | None:
        stmt = (
            select(Class)
            .where(Class.id == class_id, Class.deleted_at.is_(None))
            .with_for_update()
        )
        return self.session.scalar(stmt)

    def class_teacher_assigned_elsewhere(self, teacher_id: int, class_id: int) -> bool:
        stmt = select(Class.id).where(
            Class.class_teacher_id == teacher_id,
            Class.id != class_id,
            Class.deleted_at.is_(None),
        )
        return self.session.scalar(stmt) is not None

    def academic_readiness_issues(self, school_class: Class) -> list[str]:
        issues = []
        if school_class.status != ClassStatus.ACTIVE.value:
            issues.append("Class is not active.")
        if school_class.class_teacher_id is None:
            issues.append("No class teacher is assigned.")
        elif self.session.scalar(
            select(Teacher.id).where(
                Teacher.id == school_class.class_teacher_id,
                Teacher.status == TeacherStatus.ACTIVE.value,
            )
        ) is None:
            issues.append("The designated class teacher is not active.")

        active_subject_id = self.session.scalar(
            select(ClassSubject.subject_id)
            .join(Subject, Subject.id == ClassSubject.subject_id)
            .where(
                ClassSubject.class_id == school_class.id,
                Subject.is_active.is_(True),
            )
            .limit(1)
        )
        if active_subject_id is None:
            issues.append("No active subject is assigned to the class.")
        return issues
