from datetime import UTC, datetime

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleException, ConflictException, NotFoundException
from app.core.pagination import PaginatedResult, PaginationParams
from app.core.transactions import transaction
from app.models.enums import PaymentStatus, TeacherStatus
from app.models.teacher import Teacher, TeacherAttendance, TeacherSalaryPayment
from app.repositories.teachers import (
    TeacherAssignmentRepository,
    TeacherAttendanceRepository,
    TeacherRepository,
    TeacherSalaryPaymentRepository,
    TeacherSalaryRepository,
)
from app.schemas.teachers import (
    AttendanceCreateRequest,
    ClassAssignRequest,
    SalaryPaymentCreateRequest,
    SubjectAssignRequest,
    TeacherCreateRequest,
    TeacherUpdateRequest,
)
from app.services.audit import AuditService


class TeacherService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = TeacherRepository(session)
        self.assignments = TeacherAssignmentRepository(session)
        self.attendance_repo = TeacherAttendanceRepository(session)
        self.salary_repo = TeacherSalaryRepository(session)
        self.payment_repo = TeacherSalaryPaymentRepository(session)
        self.audit = AuditService(session)

    def create_teacher(
        self,
        payload: TeacherCreateRequest,
        actor_id: int,
        request: Request,
    ) -> Teacher:
        if self.repo.employee_no_exists(payload.employee_no):
            raise ConflictException("Employee number already exists", field="employee_no")
        with transaction(self.session):
            teacher = self.repo.create(
                Teacher(
                    user_id=payload.user_id,
                    employee_no=payload.employee_no,
                    first_name=payload.first_name,
                    last_name=payload.last_name,
                    email=str(payload.email),
                    phone=payload.phone,
                    joining_date=payload.joining_date,
                    status=TeacherStatus.ACTIVE.value,
                )
            )
            self.audit.log(
                action="teacher.create",
                entity_type="teacher",
                entity_id=teacher.id,
                actor_user_id=actor_id,
                request=request,
            )
            return teacher

    def list_teachers(
        self,
        params: PaginationParams,
        status: str | None = None,
        search: str | None = None,
    ) -> PaginatedResult:
        return self.repo.list_filtered(params, status, search)

    def get_teacher(self, teacher_id: int) -> Teacher:
        teacher = self.repo.get_by_id(teacher_id)
        if not teacher:
            raise NotFoundException("Teacher not found")
        return teacher

    def update_teacher(
        self,
        teacher_id: int,
        payload: TeacherUpdateRequest,
        actor_id: int,
        request: Request,
    ) -> Teacher:
        teacher = self.get_teacher(teacher_id)
        if teacher.status == TeacherStatus.RESIGNED.value and payload.status != TeacherStatus.ACTIVE.value:
            raise BusinessRuleException("Cannot update resigned teacher without override")
        with transaction(self.session):
            for field in ("first_name", "last_name", "email", "phone", "status"):
                value = getattr(payload, field)
                if value is not None:
                    setattr(teacher, field, str(value) if field == "email" else value)
            teacher = self.repo.update(teacher)
            self.audit.log(
                action="teacher.update",
                entity_type="teacher",
                entity_id=teacher.id,
                actor_user_id=actor_id,
                request=request,
            )
            return teacher

    def assign_subject(
        self,
        teacher_id: int,
        payload: SubjectAssignRequest,
        actor_id: int,
        request: Request,
    ):
        self.get_teacher(teacher_id)
        if self.assignments.subject_exists(teacher_id, payload.subject_id):
            raise ConflictException("Subject already assigned to teacher")
        with transaction(self.session):
            assignment = self.assignments.assign_subject(teacher_id, payload.subject_id)
            self.audit.log(
                action="teacher.assign_subject",
                entity_type="teacher",
                entity_id=teacher_id,
                actor_user_id=actor_id,
                new_values={"subject_id": payload.subject_id},
                request=request,
            )
            return assignment

    def list_subjects(self, teacher_id: int):
        self.get_teacher(teacher_id)
        return self.assignments.list_subjects(teacher_id)

    def assign_class(
        self,
        teacher_id: int,
        payload: ClassAssignRequest,
        actor_id: int,
        request: Request,
    ):
        self.get_teacher(teacher_id)
        if self.assignments.class_exists(teacher_id, payload.class_id):
            raise ConflictException("Class already assigned to teacher")
        with transaction(self.session):
            assignment = self.assignments.assign_class(teacher_id, payload.class_id)
            self.audit.log(
                action="teacher.assign_class",
                entity_type="teacher",
                entity_id=teacher_id,
                actor_user_id=actor_id,
                new_values={"class_id": payload.class_id},
                request=request,
            )
            return assignment

    def list_classes(self, teacher_id: int):
        self.get_teacher(teacher_id)
        return self.assignments.list_classes(teacher_id)

    def record_attendance(
        self,
        teacher_id: int,
        payload: AttendanceCreateRequest,
        actor_id: int,
        request: Request,
    ) -> TeacherAttendance:
        self.get_teacher(teacher_id)
        if self.attendance_repo.exists_for_date(teacher_id, payload.attendance_date):
            raise ConflictException("Attendance already recorded for this date")
        with transaction(self.session):
            record = self.attendance_repo.create(
                TeacherAttendance(
                    teacher_id=teacher_id,
                    attendance_date=payload.attendance_date,
                    status=payload.status,
                    remarks=payload.remarks,
                )
            )
            self.audit.log(
                action="teacher.attendance",
                entity_type="teacher",
                entity_id=teacher_id,
                actor_user_id=actor_id,
                request=request,
            )
            return record

    def get_salary(self, teacher_id: int):
        self.get_teacher(teacher_id)
        salary = self.salary_repo.get_by_teacher(teacher_id)
        if not salary:
            raise NotFoundException("Salary setup not found")
        return salary

    def create_salary_payment(
        self,
        teacher_id: int,
        payload: SalaryPaymentCreateRequest,
        actor_id: int,
        request: Request,
    ) -> TeacherSalaryPayment:
        teacher = self.get_teacher(teacher_id)
        if teacher.status != TeacherStatus.ACTIVE.value:
            raise BusinessRuleException("Inactive teacher cannot receive new salary payments")
        salary = self.salary_repo.get_by_teacher(teacher_id)
        if not salary:
            raise BusinessRuleException("Teacher salary setup is required before payment")
        if self.payment_repo.exists_for_month(teacher_id, payload.payment_month):
            raise ConflictException("Salary already paid for this month")

        with transaction(self.session):
            payment = self.payment_repo.create(
                TeacherSalaryPayment(
                    teacher_id=teacher_id,
                    salary_id=salary.id,
                    payment_month=payload.payment_month,
                    gross_amount=payload.gross_amount,
                    deduction_amount=payload.deduction_amount,
                    net_amount=payload.net_amount,
                    status=payload.status or PaymentStatus.PAID.value,
                    paid_at=payload.paid_at or datetime.now(UTC),
                )
            )
            self.audit.log(
                action="teacher.salary_payment",
                entity_type="teacher",
                entity_id=teacher_id,
                actor_user_id=actor_id,
                new_values={"payment_month": payload.payment_month},
                request=request,
            )
            return payment
