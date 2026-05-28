from datetime import UTC, datetime

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleException, ConflictException, NotFoundException
from app.core.pagination import PaginatedResult, PaginationParams
from app.core.transactions import transaction
from app.models.class_model import Class
from app.models.enums import ClassStatus
from app.repositories.classes import ClassRepository
from app.schemas.classes import ClassCreateRequest, ClassUpdateRequest
from app.services.audit import AuditService


class ClassService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = ClassRepository(session)
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
            "capacity": school_class.capacity,
            "status": school_class.status,
        }
        if payload.capacity is not None:
            enrolled = self.repo.count_active_students(class_id)
            if payload.capacity < enrolled:
                raise BusinessRuleException("Capacity is below current student count")

        if payload.name and payload.academic_year:
            year = payload.academic_year or school_class.academic_year
            if self.repo.exists_duplicate(
                payload.name,
                payload.section if payload.section is not None else school_class.section,
                year,
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
            if payload.capacity is not None:
                school_class.capacity = payload.capacity
            if payload.status is not None:
                school_class.status = payload.status
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
            self.repo.update(school_class)
            self.audit.log(
                action="class.delete",
                entity_type="class",
                entity_id=class_id,
                actor_user_id=actor_id,
                request=request,
            )
