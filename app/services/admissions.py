from datetime import UTC, datetime

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleException, ConflictException, NotFoundException
from app.core.pagination import PaginatedResult, PaginationParams
from app.core.transactions import transaction
from app.models.admission import StudentAdmission
from app.models.enums import AdmissionStatus, ClassStatus, StudentStatus
from app.repositories.admissions import AdmissionRepository
from app.repositories.classes import ClassRepository
from app.repositories.students import StudentRepository
from app.schemas.admissions import AdmissionCreateRequest, AdmissionUpdateRequest
from app.services.audit import AuditService


class AdmissionService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = AdmissionRepository(session)
        self.students = StudentRepository(session)
        self.classes = ClassRepository(session)
        self.audit = AuditService(session)

    def list_admissions(
        self,
        params: PaginationParams,
        status: str | None = None,
        academic_year: str | None = None,
    ) -> PaginatedResult:
        return self.repo.list_filtered(params, status, academic_year)

    def create_admission(
        self,
        student_id: int,
        payload: AdmissionCreateRequest,
        actor_id: int,
        request: Request,
    ) -> StudentAdmission:
        student = self.students.get_active(student_id)
        if not student:
            raise NotFoundException("Student not found")
        school_class = self.classes.get_active(payload.class_id)
        if not school_class:
            raise NotFoundException("Class not found")
        if self.repo.exists_for_year(student_id, payload.academic_year):
            raise ConflictException("Admission already exists for this academic year")

        with transaction(self.session):
            admission = self.repo.create(
                StudentAdmission(
                    student_id=student_id,
                    class_id=payload.class_id,
                    academic_year=payload.academic_year,
                    status=AdmissionStatus.SUBMITTED.value,
                    notes=payload.notes,
                )
            )
            self.audit.log(
                action="admission.create",
                entity_type="student_admission",
                entity_id=admission.id,
                actor_user_id=actor_id,
                request=request,
            )
            return admission

    def get_student_admission(self, student_id: int) -> StudentAdmission:
        if not self.students.get_active(student_id):
            raise NotFoundException("Student not found")
        admission = self.repo.get_for_student(student_id)
        if not admission:
            raise NotFoundException("Admission not found")
        return admission

    def get_admission(self, admission_id: int) -> StudentAdmission:
        admission = self.repo.get_by_id(admission_id)
        if not admission:
            raise NotFoundException("Admission not found")
        return admission

    def update_admission(
        self,
        admission_id: int,
        payload: AdmissionUpdateRequest,
        actor_id: int,
        request: Request,
    ) -> StudentAdmission:
        admission = self.get_admission(admission_id)
        if admission.status == AdmissionStatus.APPROVED.value and any(
            v is not None for v in (payload.class_id, payload.academic_year)
        ):
            raise BusinessRuleException("Cannot edit approved admission except notes")
        with transaction(self.session):
            if payload.class_id is not None:
                admission.class_id = payload.class_id
            if payload.academic_year is not None:
                admission.academic_year = payload.academic_year
            if payload.notes is not None:
                admission.notes = payload.notes
            admission = self.repo.update(admission)
            self.audit.log(
                action="admission.update",
                entity_type="student_admission",
                entity_id=admission.id,
                actor_user_id=actor_id,
                request=request,
            )
            return admission

    def approve_admission(
        self,
        admission_id: int,
        actor_id: int,
        request: Request,
        notes: str | None = None,
    ) -> StudentAdmission:
        admission = self.get_admission(admission_id)
        if admission.status != AdmissionStatus.SUBMITTED.value:
            raise BusinessRuleException("Admission must be submitted before approval")
        student = self.students.get_active(admission.student_id)
        if not student:
            raise BusinessRuleException("Deleted student cannot be admitted")
        school_class = self.classes.get_active(admission.class_id)
        if not school_class or school_class.status != ClassStatus.ACTIVE.value:
            raise BusinessRuleException("Class is not active")
        enrolled = self.classes.count_active_students(admission.class_id)
        if enrolled >= school_class.capacity:
            raise BusinessRuleException("Class capacity exceeded")

        with transaction(self.session):
            admission.status = AdmissionStatus.APPROVED.value
            admission.approved_by = actor_id
            admission.approved_at = datetime.now(UTC)
            if notes:
                admission.notes = notes
            admission = self.repo.update(admission)
            student.status = StudentStatus.ACTIVE.value
            student.current_class_id = admission.class_id
            self.students.update(student)
            self.audit.log(
                action="admission.approve",
                entity_type="student_admission",
                entity_id=admission.id,
                actor_user_id=actor_id,
                request=request,
            )
            return admission

    def reject_admission(
        self,
        admission_id: int,
        rejection_reason: str,
        actor_id: int,
        request: Request,
    ) -> StudentAdmission:
        admission = self.get_admission(admission_id)
        if admission.status == AdmissionStatus.APPROVED.value:
            raise BusinessRuleException("Cannot reject approved admission")
        with transaction(self.session):
            admission.status = AdmissionStatus.REJECTED.value
            admission.rejection_reason = rejection_reason
            admission = self.repo.update(admission)
            self.audit.log(
                action="admission.reject",
                entity_type="student_admission",
                entity_id=admission.id,
                actor_user_id=actor_id,
                new_values={"rejection_reason": rejection_reason},
                request=request,
            )
            return admission
