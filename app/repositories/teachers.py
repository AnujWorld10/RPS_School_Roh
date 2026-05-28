from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.pagination import PaginatedResult, PaginationParams
from app.models.subject import Subject, TeacherSubject
from app.models.teacher import (
    Teacher,
    TeacherAttendance,
    TeacherClass,
    TeacherSalary,
    TeacherSalaryPayment,
)
from app.repositories.base import BaseRepository


class TeacherRepository(BaseRepository[Teacher]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Teacher)

    def employee_no_exists(self, employee_no: str) -> bool:
        stmt = select(Teacher.id).where(Teacher.employee_no == employee_no)
        return self.session.scalar(stmt) is not None

    def list_filtered(
        self,
        params: PaginationParams,
        status: str | None = None,
        search: str | None = None,
    ) -> PaginatedResult:
        stmt = select(Teacher)
        if status:
            stmt = stmt.where(Teacher.status == status)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Teacher.first_name.like(pattern),
                    Teacher.last_name.like(pattern),
                    Teacher.employee_no.like(pattern),
                )
            )
        return self.paginate(stmt, params)


class TeacherAssignmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def assign_subject(self, teacher_id: int, subject_id: int) -> TeacherSubject:
        entity = TeacherSubject(teacher_id=teacher_id, subject_id=subject_id)
        self.session.add(entity)
        self.session.flush()
        return entity

    def assign_class(self, teacher_id: int, class_id: int) -> TeacherClass:
        entity = TeacherClass(teacher_id=teacher_id, class_id=class_id)
        self.session.add(entity)
        self.session.flush()
        return entity

    def list_subjects(self, teacher_id: int) -> list[Subject]:
        stmt = (
            select(Subject)
            .join(TeacherSubject, TeacherSubject.subject_id == Subject.id)
            .where(TeacherSubject.teacher_id == teacher_id)
        )
        return list(self.session.scalars(stmt).all())

    def list_classes(self, teacher_id: int) -> list:
        from app.models.class_model import Class

        stmt = (
            select(Class)
            .join(TeacherClass, TeacherClass.class_id == Class.id)
            .where(TeacherClass.teacher_id == teacher_id, Class.deleted_at.is_(None))
        )
        return list(self.session.scalars(stmt).all())

    def subject_exists(self, teacher_id: int, subject_id: int) -> bool:
        stmt = select(TeacherSubject.teacher_id).where(
            TeacherSubject.teacher_id == teacher_id,
            TeacherSubject.subject_id == subject_id,
        )
        return self.session.scalar(stmt) is not None

    def class_exists(self, teacher_id: int, class_id: int) -> bool:
        stmt = select(TeacherClass.teacher_id).where(
            TeacherClass.teacher_id == teacher_id,
            TeacherClass.class_id == class_id,
        )
        return self.session.scalar(stmt) is not None


class TeacherAttendanceRepository(BaseRepository[TeacherAttendance]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, TeacherAttendance)

    def exists_for_date(self, teacher_id: int, attendance_date: date) -> bool:
        stmt = select(TeacherAttendance.id).where(
            TeacherAttendance.teacher_id == teacher_id,
            TeacherAttendance.attendance_date == attendance_date,
        )
        return self.session.scalar(stmt) is not None


class TeacherSalaryRepository(BaseRepository[TeacherSalary]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, TeacherSalary)

    def get_by_teacher(self, teacher_id: int) -> TeacherSalary | None:
        stmt = select(TeacherSalary).where(TeacherSalary.teacher_id == teacher_id)
        return self.session.scalar(stmt)


class TeacherSalaryPaymentRepository(BaseRepository[TeacherSalaryPayment]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, TeacherSalaryPayment)

    def exists_for_month(self, teacher_id: int, payment_month: str) -> bool:
        stmt = select(TeacherSalaryPayment.id).where(
            TeacherSalaryPayment.teacher_id == teacher_id,
            TeacherSalaryPayment.payment_month == payment_month,
        )
        return self.session.scalar(stmt) is not None
