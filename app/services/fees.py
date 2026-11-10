from typing import Any, TypeVar

from fastapi import Request
from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.core.pagination import PaginatedResult, PaginationParams
from app.core.transactions import transaction
from app.models.class_model import Class
from app.models.fees import (
    AdmissionFeeComponent,
    AdmissionFeeStructure,
    MonthlyFeeComponent,
    MonthlyFeeStructure,
)
from app.schemas.fees import (
    AdmissionFeeComponentCreate,
    AdmissionFeeComponentUpdate,
    AdmissionFeeStructureCreate,
    AdmissionFeeStructureUpdate,
    MonthlyFeeComponentCreate,
    MonthlyFeeComponentUpdate,
    MonthlyFeeStructureCreate,
    MonthlyFeeStructureUpdate,
)
from app.services.audit import AuditService

StructureT = TypeVar("StructureT", AdmissionFeeStructure, MonthlyFeeStructure)
ComponentCreateT = TypeVar(
    "ComponentCreateT", AdmissionFeeComponentCreate, MonthlyFeeComponentCreate
)
ComponentUpdateT = TypeVar(
    "ComponentUpdateT", AdmissionFeeComponentUpdate, MonthlyFeeComponentUpdate
)
StructureCreateT = TypeVar(
    "StructureCreateT", AdmissionFeeStructureCreate, MonthlyFeeStructureCreate
)
StructureUpdateT = TypeVar(
    "StructureUpdateT", AdmissionFeeStructureUpdate, MonthlyFeeStructureUpdate
)

_SORT_FIELDS = {"academic_year", "class_id", "created_at", "structure_name", "updated_at"}


class FeeService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.audit = AuditService(session)

    def create_admission(
        self,
        payload: AdmissionFeeStructureCreate,
        actor_id: int,
        request: Request,
    ) -> AdmissionFeeStructure:
        return self._create(
            AdmissionFeeStructure,
            AdmissionFeeComponent,
            payload,
            actor_id,
            request,
            "admission",
        )

    def list_admission(
        self,
        params: PaginationParams,
        class_id: int | None = None,
        academic_year: str | None = None,
        is_active: bool | None = None,
    ) -> PaginatedResult:
        return self._list(AdmissionFeeStructure, params, class_id, academic_year, is_active)

    def get_admission(self, structure_id: int) -> AdmissionFeeStructure:
        return self._get(AdmissionFeeStructure, structure_id, "Admission")

    def update_admission(
        self,
        structure_id: int,
        payload: AdmissionFeeStructureUpdate,
        actor_id: int,
        request: Request,
    ) -> AdmissionFeeStructure:
        return self._update(
            AdmissionFeeStructure,
            AdmissionFeeComponent,
            structure_id,
            payload,
            actor_id,
            request,
            "admission",
        )

    def set_admission_status(
        self,
        structure_id: int,
        is_active: bool,
        actor_id: int,
        request: Request,
    ) -> AdmissionFeeStructure:
        return self._set_status(
            AdmissionFeeStructure,
            structure_id,
            is_active,
            actor_id,
            request,
            "admission",
            "status",
        )

    def delete_admission(
        self,
        structure_id: int,
        actor_id: int,
        request: Request,
    ) -> AdmissionFeeStructure:
        return self._set_status(
            AdmissionFeeStructure,
            structure_id,
            False,
            actor_id,
            request,
            "admission",
            "delete",
        )

    def create_monthly(
        self,
        payload: MonthlyFeeStructureCreate,
        actor_id: int,
        request: Request,
    ) -> MonthlyFeeStructure:
        return self._create(
            MonthlyFeeStructure,
            MonthlyFeeComponent,
            payload,
            actor_id,
            request,
            "monthly",
        )

    def list_monthly(
        self,
        params: PaginationParams,
        class_id: int | None = None,
        academic_year: str | None = None,
        is_active: bool | None = None,
    ) -> PaginatedResult:
        return self._list(MonthlyFeeStructure, params, class_id, academic_year, is_active)

    def get_monthly(self, structure_id: int) -> MonthlyFeeStructure:
        return self._get(MonthlyFeeStructure, structure_id, "Monthly")

    def update_monthly(
        self,
        structure_id: int,
        payload: MonthlyFeeStructureUpdate,
        actor_id: int,
        request: Request,
    ) -> MonthlyFeeStructure:
        return self._update(
            MonthlyFeeStructure,
            MonthlyFeeComponent,
            structure_id,
            payload,
            actor_id,
            request,
            "monthly",
        )

    def set_monthly_status(
        self,
        structure_id: int,
        is_active: bool,
        actor_id: int,
        request: Request,
    ) -> MonthlyFeeStructure:
        return self._set_status(
            MonthlyFeeStructure,
            structure_id,
            is_active,
            actor_id,
            request,
            "monthly",
            "status",
        )

    def delete_monthly(
        self,
        structure_id: int,
        actor_id: int,
        request: Request,
    ) -> MonthlyFeeStructure:
        return self._set_status(
            MonthlyFeeStructure,
            structure_id,
            False,
            actor_id,
            request,
            "monthly",
            "delete",
        )

    def _create(
        self,
        model: type[StructureT],
        component_model: type[AdmissionFeeComponent] | type[MonthlyFeeComponent],
        payload: StructureCreateT,
        actor_id: int,
        request: Request,
        fee_type: str,
    ) -> StructureT:
        try:
            with transaction(self.session):
                school_class = self._validate_class(
                    payload.class_id,
                    payload.academic_year,
                    lock=True,
                )
                self._ensure_unique_structure(model, payload.class_id, payload.academic_year)
                structure = model(
                    academic_year=payload.academic_year,
                    class_id=payload.class_id,
                    school_class=school_class,
                    structure_name=payload.structure_name,
                    description=payload.description,
                    is_active=payload.is_active,
                )
                for component in payload.components:
                    self._append_component(
                        structure,
                        self._new_component(component_model, component),
                    )
                self.session.add(structure)
                self.session.flush()
                self.audit.log(
                    action=f"fee.{fee_type}_structure.create",
                    entity_type=f"{fee_type}_fee_structure",
                    entity_id=structure.id,
                    actor_user_id=actor_id,
                    new_values=self._structure_snapshot(structure),
                    request=request,
                )
                return structure
        except IntegrityError as exc:
            raise ConflictException(
                f"A {fee_type} fee structure already exists for this class and academic year."
            ) from exc

    def _list(
        self,
        model: type[StructureT],
        params: PaginationParams,
        class_id: int | None,
        academic_year: str | None,
        is_active: bool | None,
    ) -> PaginatedResult:
        if params.sort_by not in _SORT_FIELDS:
            raise ValidationException(
                f"Unsupported sort field '{params.sort_by}'.",
                field="sort_by",
            )
        filters = []
        if class_id is not None:
            filters.append(model.class_id == class_id)
        if academic_year is not None:
            filters.append(model.academic_year == academic_year)
        if is_active is not None:
            filters.append(model.is_active.is_(is_active))

        count_statement = select(func.count(model.id)).where(*filters)
        total = self.session.scalar(count_statement) or 0
        sort_column = getattr(model, params.sort_by)
        sort_column = sort_column.asc() if params.sort_order == "asc" else sort_column.desc()
        statement: Select[tuple[StructureT]] = (
            select(model)
            .where(*filters)
            .options(joinedload(model.school_class), selectinload(model.components))
            .order_by(sort_column, model.id.asc())
            .offset(params.offset)
            .limit(params.limit)
        )
        items = list(self.session.scalars(statement).all())
        return PaginatedResult(items=items, total=total, page=params.page, limit=params.limit)

    def _get(
        self,
        model: type[StructureT],
        structure_id: int,
        display_name: str,
    ) -> StructureT:
        statement = (
            select(model)
            .where(model.id == structure_id)
            .options(joinedload(model.school_class), selectinload(model.components))
        )
        structure = self.session.scalar(statement)
        if structure is None:
            raise NotFoundException(f"{display_name} fee structure not found.")
        return structure

    def _update(
        self,
        model: type[StructureT],
        component_model: type[AdmissionFeeComponent] | type[MonthlyFeeComponent],
        structure_id: int,
        payload: StructureUpdateT,
        actor_id: int,
        request: Request,
        fee_type: str,
    ) -> StructureT:
        try:
            with transaction(self.session):
                structure = self._get_for_update(model, structure_id, fee_type)
                old_values = self._structure_snapshot(structure)
                target_class_id = (
                    payload.class_id if payload.class_id is not None else structure.class_id
                )
                class_changed = target_class_id != structure.class_id
                target_year = (
                    payload.academic_year
                    if payload.academic_year is not None
                    else structure.school_class.academic_year
                    if class_changed
                    else structure.academic_year
                )
                school_class = self._validate_class(target_class_id, target_year, lock=True)
                self._ensure_unique_structure(
                    model,
                    target_class_id,
                    target_year,
                    exclude_id=structure_id,
                )
                structure.class_id = target_class_id
                structure.academic_year = target_year
                structure.school_class = school_class
                for field in ("structure_name", "description", "is_active"):
                    if field in payload.model_fields_set:
                        setattr(structure, field, getattr(payload, field))
                if payload.components is not None:
                    self._apply_component_updates(
                        structure,
                        component_model,
                        payload.components,
                    )
                self.session.flush()
                self.audit.log(
                    action=f"fee.{fee_type}_structure.update",
                    entity_type=f"{fee_type}_fee_structure",
                    entity_id=structure.id,
                    actor_user_id=actor_id,
                    old_values=old_values,
                    new_values=self._structure_snapshot(structure),
                    request=request,
                )
                return structure
        except IntegrityError as exc:
            raise ConflictException(
                f"A {fee_type} fee structure already exists for this class and academic year."
            ) from exc

    def _set_status(
        self,
        model: type[StructureT],
        structure_id: int,
        is_active: bool,
        actor_id: int,
        request: Request,
        fee_type: str,
        operation: str,
    ) -> StructureT:
        with transaction(self.session):
            structure = self._get_for_update(model, structure_id, fee_type)
            previous = structure.is_active
            structure.is_active = is_active
            self.session.flush()
            if previous != is_active:
                self.audit.log(
                    action=f"fee.{fee_type}_structure.{operation}",
                    entity_type=f"{fee_type}_fee_structure",
                    entity_id=structure.id,
                    actor_user_id=actor_id,
                    old_values={"is_active": previous},
                    new_values={"is_active": is_active},
                    request=request,
                )
            return structure

    def _get_for_update(
        self,
        model: type[StructureT],
        structure_id: int,
        fee_type: str,
    ) -> StructureT:
        statement = (
            select(model)
            .where(model.id == structure_id)
            .options(joinedload(model.school_class), selectinload(model.components))
            .with_for_update()
        )
        structure = self.session.scalar(statement)
        if structure is None:
            raise NotFoundException(f"{fee_type.title()} fee structure not found.")
        return structure

    def _validate_class(self, class_id: int, academic_year: str, *, lock: bool) -> Class:
        statement = select(Class).where(Class.id == class_id, Class.deleted_at.is_(None))
        if lock:
            statement = statement.with_for_update()
        school_class = self.session.scalar(statement)
        if school_class is None:
            raise NotFoundException("Class not found.")
        if school_class.academic_year != academic_year:
            raise ValidationException(
                "The academic year must match the selected class.",
                field="academic_year",
            )
        return school_class

    def _ensure_unique_structure(
        self,
        model: type[StructureT],
        class_id: int,
        academic_year: str,
        exclude_id: int | None = None,
    ) -> None:
        statement = select(model.id).where(
            model.class_id == class_id,
            model.academic_year == academic_year,
        )
        if exclude_id is not None:
            statement = statement.where(model.id != exclude_id)
        if self.session.scalar(statement) is not None:
            raise ConflictException(
                "A fee structure already exists for this class and academic year."
            )

    def _new_component(
        self,
        component_model: type[AdmissionFeeComponent] | type[MonthlyFeeComponent],
        payload: ComponentCreateT,
    ) -> AdmissionFeeComponent | MonthlyFeeComponent:
        values: dict[str, Any] = {
            "fee_name": payload.fee_name,
            "amount": payload.amount,
            "is_optional": payload.is_optional,
            "description": payload.description,
        }
        if isinstance(payload, AdmissionFeeComponentCreate):
            values["is_refundable"] = payload.is_refundable
        if isinstance(payload, MonthlyFeeComponentCreate):
            values["billing_frequency"] = payload.billing_frequency.value
        return component_model(**values)

    def _apply_component_updates(
        self,
        structure: AdmissionFeeStructure | MonthlyFeeStructure,
        component_model: type[AdmissionFeeComponent] | type[MonthlyFeeComponent],
        updates: list[ComponentUpdateT],
    ) -> None:
        existing_by_id = {component.id: component for component in structure.components}
        seen_ids: set[int] = set()
        for update in updates:
            component_id = update.id
            if component_id is None:
                values = update.model_dump(exclude_unset=True, exclude={"id"})
                fee_name = values.get("fee_name")
                amount = values.get("amount")
                if fee_name is None or amount is None:
                    raise ValidationException("New fee components require a name and amount.")
                if "billing_frequency" in values and values["billing_frequency"] is not None:
                    values["billing_frequency"] = values["billing_frequency"].value
                self._append_component(structure, component_model(**values))
                continue
            if component_id in seen_ids:
                raise ValidationException("A component may only be updated once per request.")
            seen_ids.add(component_id)
            component = existing_by_id.get(component_id)
            if component is None:
                raise NotFoundException("Fee component not found in this structure.")
            values = update.model_dump(exclude_unset=True, exclude={"id"})
            if "billing_frequency" in values and values["billing_frequency"] is not None:
                values["billing_frequency"] = values["billing_frequency"].value
            for field, value in values.items():
                setattr(component, field, value)

        names = [component.fee_name.strip().casefold() for component in structure.components]
        if len(names) != len(set(names)):
            raise ConflictException("Fee component names must be unique within a structure.")

    def _append_component(
        self,
        structure: AdmissionFeeStructure | MonthlyFeeStructure,
        component: AdmissionFeeComponent | MonthlyFeeComponent,
    ) -> None:
        if isinstance(structure, AdmissionFeeStructure) and isinstance(
            component,
            AdmissionFeeComponent,
        ):
            structure.components.append(component)
            return
        if isinstance(structure, MonthlyFeeStructure) and isinstance(
            component,
            MonthlyFeeComponent,
        ):
            structure.components.append(component)
            return
        raise TypeError("Fee structure and component types do not match.")

    def _structure_snapshot(
        self,
        structure: AdmissionFeeStructure | MonthlyFeeStructure,
    ) -> dict[str, Any]:
        values: dict[str, Any] = {
            "class_id": structure.class_id,
            "academic_year": structure.academic_year,
            "structure_name": structure.structure_name,
            "description": structure.description,
            "is_active": structure.is_active,
            "components": [
                {
                    "id": component.id,
                    "fee_name": component.fee_name,
                    "amount": str(component.amount),
                    "is_optional": component.is_optional,
                    "description": component.description,
                }
                for component in structure.components
            ],
        }
        if isinstance(structure, AdmissionFeeStructure):
            for item, admission_component in zip(
                values["components"],
                structure.components,
                strict=True,
            ):
                item["is_refundable"] = admission_component.is_refundable
        if isinstance(structure, MonthlyFeeStructure):
            for item, monthly_component in zip(
                values["components"],
                structure.components,
                strict=True,
            ):
                item["billing_frequency"] = monthly_component.billing_frequency
        return values
