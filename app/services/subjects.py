from fastapi import Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleException, ConflictException, NotFoundException
from app.core.pagination import PaginatedResult, PaginationParams
from app.core.transactions import transaction
from app.models.subject import Subject
from app.repositories.subjects import SubjectRepository
from app.schemas.subjects import SubjectCreateRequest, SubjectUpdateRequest
from app.services.audit import AuditService


class SubjectService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = SubjectRepository(session)
        self.audit = AuditService(session)

    def create(
        self,
        payload: SubjectCreateRequest,
        actor_id: int,
        request: Request,
    ) -> Subject:
        if self.repo.code_exists(payload.code):
            raise ConflictException("Subject code already exists", field="code")
        try:
            with transaction(self.session):
                subject = self.repo.create(Subject(code=payload.code, name=payload.name))
                self.audit.log(
                    action="subject.create",
                    entity_type="subject",
                    entity_id=subject.id,
                    actor_user_id=actor_id,
                    new_values={"code": subject.code, "name": subject.name},
                    request=request,
                )
                return subject
        except IntegrityError as exc:
            raise ConflictException("Subject code already exists", field="code") from exc

    def list(
        self,
        params: PaginationParams,
        active: bool | None = None,
        search: str | None = None,
    ) -> PaginatedResult:
        return self.repo.list_filtered(params, active, search)

    def get(self, subject_id: int) -> Subject:
        subject = self.repo.get_by_id(subject_id)
        if not subject:
            raise NotFoundException("Subject not found")
        return subject

    def update(
        self,
        subject_id: int,
        payload: SubjectUpdateRequest,
        actor_id: int,
        request: Request,
    ) -> Subject:
        subject = self.get(subject_id)
        if payload.code is not None and self.repo.code_exists(
            payload.code,
            exclude_id=subject_id,
        ):
            raise ConflictException("Subject code already exists", field="code")
        old_values = {"code": subject.code, "name": subject.name}
        with transaction(self.session):
            subject = self.repo.get_for_update(subject_id)
            if subject is None:
                raise NotFoundException("Subject not found")
            for field in ("code", "name"):
                value = getattr(payload, field)
                if value is not None:
                    setattr(subject, field, value)
            try:
                self.repo.update(subject)
            except IntegrityError as exc:
                raise ConflictException("Subject code already exists", field="code") from exc
            self.audit.log(
                action="subject.update",
                entity_type="subject",
                entity_id=subject_id,
                actor_user_id=actor_id,
                old_values=old_values,
                new_values={
                    "code": subject.code,
                    "name": subject.name,
                    "is_active": subject.is_active,
                },
                request=request,
            )
            return subject

    def activate(self, subject_id: int, actor_id: int, request: Request) -> Subject:
        with transaction(self.session):
            subject = self.repo.get_for_update(subject_id)
            if subject is None:
                raise NotFoundException("Subject not found")
            if subject.is_active:
                return subject
            subject.is_active = True
            self.repo.update(subject)
            self.audit.log(
                action="subject.activate",
                entity_type="subject",
                entity_id=subject_id,
                actor_user_id=actor_id,
                old_values={"is_active": False},
                new_values={"is_active": True},
                request=request,
            )
            return subject

    def deactivate(self, subject_id: int, actor_id: int, request: Request) -> Subject:
        with transaction(self.session):
            subject = self.repo.get_for_update(subject_id)
            if subject is None:
                raise NotFoundException("Subject not found")
            if not subject.is_active:
                return subject
            self._ensure_can_deactivate(subject_id)
            subject.is_active = False
            self.repo.update(subject)
            self.audit.log(
                action="subject.deactivate",
                entity_type="subject",
                entity_id=subject_id,
                actor_user_id=actor_id,
                old_values={"is_active": True},
                new_values={"is_active": False},
                request=request,
            )
            return subject

    def _ensure_can_deactivate(self, subject_id: int) -> None:
        active_classes = self.repo.active_class_offerings(subject_id)
        if active_classes:
            ids = ", ".join(str(class_id) for class_id in active_classes)
            raise BusinessRuleException(
                "Remove this subject from active classes before deactivating it. "
                f"Active class IDs: {ids}"
            )
