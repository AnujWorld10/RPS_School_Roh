from datetime import UTC, datetime

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleException, ConflictException, NotFoundException
from app.core.pagination import PaginatedResult, PaginationParams
from app.core.transactions import transaction
from app.models.enums import ClassStatus, StudentStatus
from app.models.student import Student
from app.repositories.classes import ClassRepository
from app.repositories.students import StudentRepository
from app.schemas.students import (
    StudentClassAssignRequest,
    StudentCreateRequest,
    StudentUpdateRequest,
)
from app.services.audit import AuditService
from app.utils.business_ids import generate_student_code

VALID_STATUS_TRANSITIONS = {
    StudentStatus.PROSPECTIVE.value: {
        StudentStatus.ACTIVE.value,
        StudentStatus.INACTIVE.value,
    },
    StudentStatus.ACTIVE.value: {
        StudentStatus.INACTIVE.value,
        StudentStatus.GRADUATED.value,
        StudentStatus.TRANSFERRED.value,
    },
    StudentStatus.INACTIVE.value: {StudentStatus.ACTIVE.value},
}


class StudentService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = StudentRepository(session)
        self.classes = ClassRepository(session)
        self.audit = AuditService(session)

    def create_student(
        self,
        payload: StudentCreateRequest,
        actor_id: int,
        request: Request,
    ) -> Student:
        if payload.admission_no and self.repo.admission_no_exists(payload.admission_no):
            raise ConflictException("Admission number already exists", field="admission_no")
        if payload.current_class_id:
            school_class = self.classes.get_active(payload.current_class_id)
            if not school_class:
                raise NotFoundException("Class not found")
            self._ensure_capacity(school_class.id)
        with transaction(self.session):
            student = self.repo.create(
                Student(
                    student_code=generate_student_code(self.session),
                    admission_no=payload.admission_no,
                    first_name=payload.first_name,
                    last_name=payload.last_name,
                    date_of_birth=payload.date_of_birth,
                    gender=payload.gender,
                    email=payload.email,
                    phone=payload.phone,
                    class_id=payload.current_class_id,
                    current_class_id=payload.current_class_id,
                    status=StudentStatus.PROSPECTIVE.value
                    if not payload.current_class_id
                    else StudentStatus.ACTIVE.value,
                )
            )
            self.audit.log(
                action="student.create",
                entity_type="student",
                entity_id=student.id,
                actor_user_id=actor_id,
                request=request,
            )
            return student

    def list_students(
        self,
        params: PaginationParams,
        status: str | None = None,
        current_class_id: int | None = None,
        search: str | None = None,
    ) -> PaginatedResult:
        return self.repo.list_filtered(params, status, current_class_id, search)

    def get_student(self, student_id: int) -> Student:
        student = self.repo.get_active(student_id)
        if not student:
            raise NotFoundException("Student not found")
        return student

    def update_student(
        self,
        student_id: int,
        payload: StudentUpdateRequest,
        actor_id: int,
        request: Request,
    ) -> Student:
        student = self.get_student(student_id)
        with transaction(self.session):
            for field in ("first_name", "last_name", "date_of_birth", "gender", "email", "phone"):
                value = getattr(payload, field)
                if value is not None:
                    setattr(student, field, value)
            if payload.current_class_id is not None:
                self._ensure_capacity(payload.current_class_id)
                student.current_class_id = payload.current_class_id
            student = self.repo.update(student)
            self.audit.log(
                action="student.update",
                entity_type="student",
                entity_id=student.id,
                actor_user_id=actor_id,
                request=request,
            )
            return student

    def update_status(
        self,
        student_id: int,
        status: str,
        actor_id: int,
        request: Request,
        reason: str | None = None,
    ) -> Student:
        student = self.get_student(student_id)
        allowed = VALID_STATUS_TRANSITIONS.get(student.status, set())
        if status not in allowed:
            raise BusinessRuleException("Invalid status transition")
        with transaction(self.session):
            old_status = student.status
            student.status = status
            student = self.repo.update(student)
            self.audit.log(
                action="student.status_change",
                entity_type="student",
                entity_id=student.id,
                actor_user_id=actor_id,
                old_values={"status": old_status, "reason": reason},
                new_values={"status": status},
                request=request,
            )
            return student

    def assign_class(
        self,
        student_id: int,
        payload: StudentClassAssignRequest,
        actor_id: int,
        request: Request,
    ) -> Student:
        student = self.get_student(student_id)
        school_class = self.classes.get_active(payload.class_id)
        if not school_class or school_class.status != ClassStatus.ACTIVE.value:
            raise NotFoundException("Class not found")
        self._ensure_capacity(payload.class_id)
        with transaction(self.session):
            student.current_class_id = payload.class_id
            if student.status == StudentStatus.PROSPECTIVE.value:
                student.status = StudentStatus.ACTIVE.value
            student = self.repo.update(student)
            self.audit.log(
                action="student.assign_class",
                entity_type="student",
                entity_id=student.id,
                actor_user_id=actor_id,
                new_values={"class_id": payload.class_id, "academic_year": payload.academic_year},
                request=request,
            )
            return student

    def soft_delete(self, student_id: int, actor_id: int, request: Request) -> None:
        student = self.get_student(student_id)
        with transaction(self.session):
            student.deleted_at = datetime.now(UTC)
            student.deleted_by = actor_id
            student.is_active = False
            self.repo.update(student)
            self.audit.log(
                action="student.delete",
                entity_type="student",
                entity_id=student.id,
                actor_user_id=actor_id,
                request=request,
            )

    def _ensure_capacity(self, class_id: int) -> None:
        school_class = self.classes.get_active(class_id)
        if not school_class:
            raise NotFoundException("Class not found")
        enrolled = self.classes.count_active_students(class_id)
        if enrolled >= school_class.capacity:
            raise BusinessRuleException("Class capacity exceeded")
