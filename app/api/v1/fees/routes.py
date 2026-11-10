from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.core.pagination import PaginationParams, pagination_params
from app.core.responses import paginated_response, success_response
from app.db.session import get_db
from app.models.user import User
from app.schemas.fees import (
    AdmissionFeeStructureCreate,
    AdmissionFeeStructureResponse,
    AdmissionFeeStructureUpdate,
    FeeStructureStatusUpdate,
    MonthlyFeeStructureCreate,
    MonthlyFeeStructureResponse,
    MonthlyFeeStructureUpdate,
)
from app.services.fees import FeeService

router = APIRouter()


@router.post(
    "/admission-structures",
    status_code=status.HTTP_201_CREATED,
    summary="Create an admission fee structure",
)
def create_admission_fee_structure(
    payload: AdmissionFeeStructureCreate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("fees.create"))],
):
    structure = FeeService(db).create_admission(payload, current_user.id, request)
    data = AdmissionFeeStructureResponse.model_validate(structure).model_dump()
    return success_response("Admission fee structure created successfully.", data, request)


@router.get(
    "/admission-structures",
    summary="List admission fee structures",
)
def list_admission_fee_structures(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("fees.read"))],
    params: Annotated[PaginationParams, Depends(pagination_params)],
    class_id: Annotated[int | None, Query(ge=1, description="Filter by class ID.")] = None,
    academic_year: Annotated[
        str | None,
        Query(min_length=4, max_length=20, description="Filter by class academic year."),
    ] = None,
    is_active: Annotated[bool | None, Query(description="Filter by active status.")] = None,
):
    result = FeeService(db).list_admission(params, class_id, academic_year, is_active)
    data = [
        AdmissionFeeStructureResponse.model_validate(item).model_dump() for item in result.items
    ]
    return paginated_response(
        "Admission fee structures fetched successfully.",
        data,
        result.page,
        result.limit,
        result.total,
        request,
    )


@router.get(
    "/admission-structures/{structure_id}",
    summary="Get an admission fee structure",
)
def get_admission_fee_structure(
    structure_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("fees.read"))],
):
    structure = FeeService(db).get_admission(structure_id)
    data = AdmissionFeeStructureResponse.model_validate(structure).model_dump()
    return success_response("Admission fee structure fetched successfully.", data, request)


@router.put(
    "/admission-structures/{structure_id}",
    summary="Update an admission fee structure",
)
def update_admission_fee_structure(
    structure_id: int,
    payload: AdmissionFeeStructureUpdate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("fees.update"))],
):
    structure = FeeService(db).update_admission(
        structure_id,
        payload,
        current_user.id,
        request,
    )
    data = AdmissionFeeStructureResponse.model_validate(structure).model_dump()
    return success_response("Admission fee structure updated successfully.", data, request)


@router.patch(
    "/admission-structures/{structure_id}/status",
    summary="Change an admission fee structure's active status",
)
def update_admission_fee_structure_status(
    structure_id: int,
    payload: FeeStructureStatusUpdate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("fees.update"))],
):
    structure = FeeService(db).set_admission_status(
        structure_id,
        payload.is_active,
        current_user.id,
        request,
    )
    data = AdmissionFeeStructureResponse.model_validate(structure).model_dump()
    return success_response("Admission fee structure status updated.", data, request)


@router.delete(
    "/admission-structures/{structure_id}",
    summary="Deactivate an admission fee structure",
)
def delete_admission_fee_structure(
    structure_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("fees.delete"))],
):
    structure = FeeService(db).delete_admission(structure_id, current_user.id, request)
    data = AdmissionFeeStructureResponse.model_validate(structure).model_dump()
    return success_response("Admission fee structure deactivated.", data, request)


@router.post(
    "/monthly-structures",
    status_code=status.HTTP_201_CREATED,
    summary="Create a monthly fee structure",
)
def create_monthly_fee_structure(
    payload: MonthlyFeeStructureCreate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("fees.create"))],
):
    structure = FeeService(db).create_monthly(payload, current_user.id, request)
    data = MonthlyFeeStructureResponse.model_validate(structure).model_dump()
    return success_response("Monthly fee structure created successfully.", data, request)


@router.get(
    "/monthly-structures",
    summary="List monthly fee structures",
)
def list_monthly_fee_structures(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("fees.read"))],
    params: Annotated[PaginationParams, Depends(pagination_params)],
    class_id: Annotated[int | None, Query(ge=1, description="Filter by class ID.")] = None,
    academic_year: Annotated[
        str | None,
        Query(min_length=4, max_length=20, description="Filter by class academic year."),
    ] = None,
    is_active: Annotated[bool | None, Query(description="Filter by active status.")] = None,
):
    result = FeeService(db).list_monthly(params, class_id, academic_year, is_active)
    data = [MonthlyFeeStructureResponse.model_validate(item).model_dump() for item in result.items]
    return paginated_response(
        "Monthly fee structures fetched successfully.",
        data,
        result.page,
        result.limit,
        result.total,
        request,
    )


@router.get(
    "/monthly-structures/{structure_id}",
    summary="Get a monthly fee structure",
)
def get_monthly_fee_structure(
    structure_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("fees.read"))],
):
    structure = FeeService(db).get_monthly(structure_id)
    data = MonthlyFeeStructureResponse.model_validate(structure).model_dump()
    return success_response("Monthly fee structure fetched successfully.", data, request)


@router.put(
    "/monthly-structures/{structure_id}",
    summary="Update a monthly fee structure",
)
def update_monthly_fee_structure(
    structure_id: int,
    payload: MonthlyFeeStructureUpdate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("fees.update"))],
):
    structure = FeeService(db).update_monthly(
        structure_id,
        payload,
        current_user.id,
        request,
    )
    data = MonthlyFeeStructureResponse.model_validate(structure).model_dump()
    return success_response("Monthly fee structure updated successfully.", data, request)


@router.patch(
    "/monthly-structures/{structure_id}/status",
    summary="Change a monthly fee structure's active status",
)
def update_monthly_fee_structure_status(
    structure_id: int,
    payload: FeeStructureStatusUpdate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("fees.update"))],
):
    structure = FeeService(db).set_monthly_status(
        structure_id,
        payload.is_active,
        current_user.id,
        request,
    )
    data = MonthlyFeeStructureResponse.model_validate(structure).model_dump()
    return success_response("Monthly fee structure status updated.", data, request)


@router.delete(
    "/monthly-structures/{structure_id}",
    summary="Deactivate a monthly fee structure",
)
def delete_monthly_fee_structure(
    structure_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("fees.delete"))],
):
    structure = FeeService(db).delete_monthly(structure_id, current_user.id, request)
    data = MonthlyFeeStructureResponse.model_validate(structure).model_dump()
    return success_response("Monthly fee structure deactivated.", data, request)
