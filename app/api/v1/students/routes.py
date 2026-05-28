from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.core.pagination import PaginationParams, pagination_params
from app.core.responses import paginated_response, success_response
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import StatusUpdateRequest
from app.schemas.students import (
    StudentClassAssignRequest,
    StudentCreateRequest,
    StudentResponse,
    StudentUpdateRequest,
)
from app.services.students import StudentService

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_student(
    payload: StudentCreateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("students.create"))],
):
    student = StudentService(db).create_student(payload, current_user.id, request)
    return success_response(
        "Student created successfully",
        StudentResponse.model_validate(student).model_dump(),
        request,
    )


@router.get("")
def list_students(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("students.read"))],
    params: Annotated[PaginationParams, Depends(pagination_params)],
    status: str | None = Query(default=None),
    current_class_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
):
    result = StudentService(db).list_students(params, status, current_class_id, search)
    data = [StudentResponse.model_validate(item).model_dump() for item in result.items]
    return paginated_response(
        "Students fetched successfully",
        data,
        result.page,
        result.limit,
        result.total,
        request,
    )


@router.get("/{student_id}")
def get_student(
    student_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("students.read"))],
):
    student = StudentService(db).get_student(student_id)
    return success_response(
        "Student fetched successfully",
        StudentResponse.model_validate(student).model_dump(),
        request,
    )


@router.put("/{student_id}")
def update_student(
    student_id: int,
    payload: StudentUpdateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("students.update"))],
):
    student = StudentService(db).update_student(student_id, payload, current_user.id, request)
    return success_response(
        "Student updated successfully",
        StudentResponse.model_validate(student).model_dump(),
        request,
    )


@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("students.delete"))],
):
    StudentService(db).soft_delete(student_id, current_user.id, request)
    return success_response("Student deleted successfully", None, request)


@router.put("/{student_id}/status")
def update_student_status(
    student_id: int,
    payload: StatusUpdateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("students.update"))],
):
    student = StudentService(db).update_status(
        student_id,
        payload.status,
        current_user.id,
        request,
        payload.reason,
    )
    return success_response(
        "Student status updated successfully",
        StudentResponse.model_validate(student).model_dump(),
        request,
    )


@router.put("/{student_id}/class")
def assign_student_class(
    student_id: int,
    payload: StudentClassAssignRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("students.update"))],
):
    student = StudentService(db).assign_class(student_id, payload, current_user.id, request)
    return success_response(
        "Student class assigned successfully",
        StudentResponse.model_validate(student).model_dump(),
        request,
    )
