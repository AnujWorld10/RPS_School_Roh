from datetime import UTC, datetime

from fastapi import Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleException, ConflictException, NotFoundException
from app.core.pagination import PaginatedResult, PaginationParams
from app.core.transactions import transaction
from app.models.class_model import Class
from app.models.enums import ClassStatus
from app.repositories.classes import ClassRepository
from app.repositories.subjects import (
    ClassSubjectRepository,
    SubjectRepository,
    active_teacher_exists,
)
from app.schemas.classes import ClassCreateRequest, ClassUpdateRequest
from app.schemas.subjects import ClassAcademicReadinessResponse
from app.services.audit import AuditService


class ClassService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = ClassRepository(session)
        self.subjects = SubjectRepository(session)
        self.class_subjects = ClassSubjectRepository(session)
        self.audit = AuditService(session)

    def create_class(
        self,
        payload: ClassCreateRequest,
        actor_id: int,
        request: Request,
    ) -> Class:
        if self.repo.exists_duplicate(payload.name, payload.section, payload.academic_year):
            raise ConflictException(
                "Class already exists for this section and academic year",
            )
        with transaction(self.session):
            school_class = self.repo.create(
                Class(
                    name=payload.name,
                    section=payload.section,
                    academic_year=payload.academic_year,
                    capacity=payload.capacity,
                    status=ClassStatus.ACTIVE.value,
                )
            )
            self.audit.log(
                action="class.create",
                entity_type="class",
                entity_id=school_class.id,
                actor_user_id=actor_id,
                new_values={
                    "name": school_class.name,
                    "section": school_class.section,
                    "academic_year": school_class.academic_year,
                },
                request=request,
            )
            return school_class

    def list_classes(
        self,
        params: PaginationParams,
        academic_year: str | None = None,
        status: str | None = None,
    ) -> PaginatedResult:
        return self.repo.list_filtered(params, academic_year, status)

    def get_class(self, class_id: int) -> Class:
        school_class = self.repo.get_active(class_id)
        if not school_class:
            raise NotFoundException("Class not found")
        return school_class

    def academic_readiness(self, class_id: int) -> ClassAcademicReadinessResponse:
        school_class = self.get_class(class_id)
        issues = self.repo.academic_readiness_issues(school_class)
        return ClassAcademicReadinessResponse(
            class_id=school_class.id,
            ready=not issues,
            class_teacher_id=school_class.class_teacher_id,
            active_subject_ids=self.class_subjects.active_subject_ids(school_class.id),
            issues=issues,
        )

    def list_subjects(self, class_id: int):
        self.get_class(class_id)
        return self.class_subjects.list_for_class(class_id)

    def assign_subject(
        self,
        class_id: int,
        subject_id: int,
        actor_id: int,
        request: Request,
    ) -> None:
        try:
            with transaction(self.session):
                school_class = self.repo.get_active_for_update(class_id)
                if not school_class:
                    raise NotFoundException("Class not found")
                subject = self.subjects.get_for_update(subject_id)
                if not subject or not subject.is_active:
                    raise NotFoundException("Active subject not found")
                if self.class_subjects.has_offering(class_id, subject_id):
                    raise ConflictException("Subject is already assigned to this class")
                self.class_subjects.add(class_id, subject_id)
                self.audit.log(
                    action="class.subject.assign",
                    entity_type="class",
                    entity_id=class_id,
                    actor_user_id=actor_id,
                    new_values={"subject_id": subject_id},
                    request=request,
                )
        except IntegrityError as exc:
            raise ConflictException("Subject is already assigned to this class") from exc

    def remove_subject(
        self,
        class_id: int,
        subject_id: int,
        actor_id: int,
        request: Request,
    ) -> None:
        with transaction(self.session):
            school_class = self.repo.get_active_for_update(class_id)
            if not school_class:
                raise NotFoundException("Class not found")
            if self.class_subjects.active_student_count(class_id):
                raise BusinessRuleException(
                    "Cannot remove a class subject while active students are enrolled"
                )
            if not self.class_subjects.remove(class_id, subject_id):
                raise NotFoundException("Subject is not assigned to this class")
            self.audit.log(
                action="class.subject.remove",
                entity_type="class",
                entity_id=class_id,
                actor_user_id=actor_id,
                old_values={"subject_id": subject_id},
                request=request,
            )

    def assign_class_teacher(
        self,
        class_id: int,
        teacher_id: int,
        actor_id: int,
        request: Request,
        replace: bool = False,
    ) -> None:
        with transaction(self.session):
            school_class = self.repo.get_active_for_update(class_id)
            if not school_class:
                raise NotFoundException("Class not found")
            if not active_teacher_exists(self.session, teacher_id):
                raise NotFoundException("Active teacher not found")
            if self.repo.class_teacher_assigned_elsewhere(teacher_id, class_id):
                raise ConflictException(
                    "A teacher can be designated class teacher for only one class"
                )
            if (
                school_class.class_teacher_id is not None
                and school_class.class_teacher_id != teacher_id
                and not replace
            ):
                raise ConflictException(
                    "Class already has a designated class teacher; remove the current "
                    "assignment first"
                )
            try:
                school_class.class_teacher_id = teacher_id
                self.repo.update(school_class)
                self.audit.log(
                    action="class.class_teacher.assign",
                    entity_type="class",
                    entity_id=class_id,
                    actor_user_id=actor_id,
                    new_values={"teacher_id": teacher_id},
                    request=request,
                )
            except IntegrityError as exc:
                raise ConflictException(
                    "A teacher can be designated class teacher for only one class"
                ) from exc

    def remove_class_teacher(
        self,
        class_id: int,
        actor_id: int,
        request: Request,
    ) -> None:
        with transaction(self.session):
            school_class = self.repo.get_active_for_update(class_id)
            if not school_class:
                raise NotFoundException("Class not found")
            if school_class.class_teacher_id is None:
                raise NotFoundException("Class has no designated class teacher")
            teacher_id = school_class.class_teacher_id
            school_class.class_teacher_id = None
            self.repo.update(school_class)
            self.audit.log(
                action="class.class_teacher.remove",
                entity_type="class",
                entity_id=class_id,
                actor_user_id=actor_id,
                old_values={"teacher_id": teacher_id},
                request=request,
            )

    def update_class(
        self,
        class_id: int,
        payload: ClassUpdateRequest,
        actor_id: int,
        request: Request,
    ) -> Class:
        school_class = self.get_class(class_id)
        old_values = {
            "name": school_class.name,
            "section": school_class.section,
            "academic_year": school_class.academic_year,
            "capacity": school_class.capacity,
            "status": school_class.status,
        }
        if payload.capacity is not None:
            enrolled = self.repo.count_active_students(class_id)
            if payload.capacity < enrolled:
                raise BusinessRuleException("Capacity is below current student count")

        new_name = payload.name if payload.name is not None else school_class.name
        new_section = payload.section if payload.section is not None else school_class.section
        new_academic_year = (
            payload.academic_year
            if payload.academic_year is not None
            else school_class.academic_year
        )
        if (
            payload.name is not None
            or payload.section is not None
            or payload.academic_year is not None
        ):
            if self.repo.exists_duplicate(
                new_name,
                new_section,
                new_academic_year,
                exclude_id=class_id,
            ):
                raise ConflictException(
                    "Class already exists for this section and academic year",
                )

        with transaction(self.session):
            if payload.name is not None:
                school_class.name = payload.name
            if payload.section is not None:
                school_class.section = payload.section
            if payload.academic_year is not None:
                school_class.academic_year = payload.academic_year
            if payload.capacity is not None:
                school_class.capacity = payload.capacity
            if payload.status is not None:
                if payload.status.value == ClassStatus.ACTIVE.value:
                    old_status = school_class.status
                    school_class.status = ClassStatus.ACTIVE.value
                    readiness = self.repo.academic_readiness_issues(school_class)
                    if readiness:
                        school_class.status = old_status
                        raise BusinessRuleException(
                            "Class cannot be activated until academic setup is complete: "
                            + " ".join(readiness)
                        )
                else:
                    school_class.status = payload.status.value
            school_class = self.repo.update(school_class)
            self.audit.log(
                action="class.update",
                entity_type="class",
                entity_id=school_class.id,
                actor_user_id=actor_id,
                old_values=old_values,
                new_values={
                    "name": school_class.name,
                    "section": school_class.section,
                    "academic_year": school_class.academic_year,
                    "capacity": school_class.capacity,
                    "status": school_class.status,
                },
                request=request,
            )
            return school_class

    def delete_class(self, class_id: int, actor_id: int, request: Request) -> None:
        school_class = self.get_class(class_id)
        if self.repo.count_active_students(class_id) > 0:
            raise BusinessRuleException("Cannot delete class with active students")
        with transaction(self.session):
            school_class.deleted_at = datetime.now(UTC)
            school_class.deleted_by = actor_id
            school_class.is_active = False
            school_class.class_teacher_id = None
            self.repo.update(school_class)
            self.audit.log(
                action="class.delete",
                entity_type="class",
                entity_id=class_id,
                actor_user_id=actor_id,
                request=request,
            )
