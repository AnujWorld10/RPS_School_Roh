from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.pagination import PaginatedResult, PaginationParams
from app.models.class_model import Class
from app.models.enums import ClassStatus, StudentStatus, TeacherStatus
from app.models.student import Student
from app.models.subject import ClassSubject, Subject, TeacherClassSubject
from app.models.teacher import Teacher
from app.repositories.base import BaseRepository


class SubjectRepository(BaseRepository[Subject]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Subject)

    def list_filtered(
        self,
        params: PaginationParams,
        active: bool | None = None,
        search: str | None = None,
    ) -> PaginatedResult:
        stmt = select(Subject)
        if active is not None:
            stmt = stmt.where(Subject.is_active.is_(active))
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(Subject.code.like(pattern) | Subject.name.like(pattern))
        return self.paginate(stmt, params)

    def code_exists(self, code: str, exclude_id: int | None = None) -> bool:
        stmt = select(Subject.id).where(Subject.code == code)
        if exclude_id is not None:
            stmt = stmt.where(Subject.id != exclude_id)
        return self.session.scalar(stmt) is not None

    def get_for_update(self, subject_id: int) -> Subject | None:
        return self.session.scalar(
            select(Subject).where(Subject.id == subject_id).with_for_update()
        )

    def active_class_offerings(self, subject_id: int) -> list[int]:
        stmt = (
            select(ClassSubject.class_id)
            .join(Class, Class.id == ClassSubject.class_id)
            .where(
                ClassSubject.subject_id == subject_id,
                Class.status == ClassStatus.ACTIVE.value,
                Class.deleted_at.is_(None),
            )
        )
        return list(self.session.scalars(stmt))


class ClassSubjectRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def has_offering(self, class_id: int, subject_id: int) -> bool:
        return self.session.get(ClassSubject, (class_id, subject_id)) is not None

    def has_active_offering(self, class_id: int, subject_id: int) -> bool:
        return self.session.scalar(
            select(ClassSubject.class_id)
            .join(Subject, Subject.id == ClassSubject.subject_id)
            .where(
                ClassSubject.class_id == class_id,
                ClassSubject.subject_id == subject_id,
                Subject.is_active.is_(True),
            )
        ) is not None

    def add(self, class_id: int, subject_id: int) -> ClassSubject:
        offering = ClassSubject(class_id=class_id, subject_id=subject_id)
        self.session.add(offering)
        self.session.flush()
        return offering

    def remove(self, class_id: int, subject_id: int) -> bool:
        offering = self.session.get(ClassSubject, (class_id, subject_id))
        if offering is None:
            return False
        self.session.delete(offering)
        self.session.flush()
        return True

    def list_for_class(self, class_id: int, active_only: bool = False) -> list[Subject]:
        stmt = (
            select(Subject)
            .join(ClassSubject, ClassSubject.subject_id == Subject.id)
            .where(ClassSubject.class_id == class_id)
            .order_by(Subject.name, Subject.id)
        )
        if active_only:
            stmt = stmt.where(Subject.is_active.is_(True))
        return list(self.session.scalars(stmt))

    def active_subject_ids(self, class_id: int) -> list[int]:
        stmt = (
            select(Subject.id)
            .join(ClassSubject, ClassSubject.subject_id == Subject.id)
            .where(ClassSubject.class_id == class_id, Subject.is_active.is_(True))
        )
        return list(self.session.scalars(stmt))

    def active_student_count(self, class_id: int) -> int:
        stmt = select(func.count()).select_from(Student).where(
            or_(Student.class_id == class_id, Student.current_class_id == class_id),
            Student.deleted_at.is_(None),
            Student.status == StudentStatus.ACTIVE.value,
        )
        return self.session.scalar(stmt) or 0


class TeacherClassSubjectRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def has_assignment(self, teacher_id: int, class_id: int, subject_id: int) -> bool:
        return (
            self.session.get(TeacherClassSubject, (teacher_id, class_id, subject_id))
            is not None
        )

    def add(self, teacher_id: int, class_id: int, subject_id: int) -> TeacherClassSubject:
        assignment = TeacherClassSubject(
            teacher_id=teacher_id,
            class_id=class_id,
            subject_id=subject_id,
        )
        self.session.add(assignment)
        self.session.flush()
        return assignment

    def remove(self, teacher_id: int, class_id: int, subject_id: int) -> bool:
        assignment = self.session.get(TeacherClassSubject, (teacher_id, class_id, subject_id))
        if assignment is None:
            return False
        self.session.delete(assignment)
        self.session.flush()
        return True

    def list_for_teacher(self, teacher_id: int) -> list[tuple[int, int, str, str]]:
        stmt = (
            select(
                TeacherClassSubject.class_id,
                TeacherClassSubject.subject_id,
                Class.name,
                Subject.name,
            )
            .join(Class, Class.id == TeacherClassSubject.class_id)
            .join(Subject, Subject.id == TeacherClassSubject.subject_id)
            .where(
                TeacherClassSubject.teacher_id == teacher_id,
                Class.status == ClassStatus.ACTIVE.value,
                Class.deleted_at.is_(None),
                Subject.is_active.is_(True),
            )
            .order_by(Class.academic_year, Class.name, Subject.name)
        )
        return list(self.session.execute(stmt).tuples())

    def has_teacher_subject_assignment(self, teacher_id: int) -> bool:
        stmt = select(TeacherClassSubject.teacher_id).where(
            TeacherClassSubject.teacher_id == teacher_id
        )
        return self.session.scalar(stmt) is not None


def active_teacher_exists(session: Session, teacher_id: int) -> bool:
    return session.scalar(
        select(Teacher.id).where(
            Teacher.id == teacher_id,
            Teacher.status == TeacherStatus.ACTIVE.value,
        )
    ) is not None
