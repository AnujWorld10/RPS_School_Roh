from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.core.pagination import PaginationParams, pagination_params
from app.core.responses import paginated_response, success_response
from app.db.session import get_db
from app.models.user import User
from app.schemas.teachers import (
    AttendanceCreateRequest,
    AttendanceResponse,
    ClassAssignRequest,
    SalaryPaymentCreateRequest,
    SalaryPaymentResponse,
    SalaryResponse,
    SubjectAssignRequest,
    TeacherCreateRequest,
    TeacherResponse,
    TeacherUpdateRequest,
)
from app.services.teachers import TeacherService

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_teacher(
    payload: TeacherCreateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("teachers.create"))],
):
    teacher = TeacherService(db).create_teacher(payload, current_user.id, request)
    return success_response(
        "Teacher created successfully",
        TeacherResponse.model_validate(teacher).model_dump(),
        request,
    )


@router.get("")
def list_teachers(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("teachers.read"))],
    params: Annotated[PaginationParams, Depends(pagination_params)],
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
):
    result = TeacherService(db).list_teachers(params, status, search)
    data = [TeacherResponse.model_validate(item).model_dump() for item in result.items]
    return paginated_response(
        "Teachers fetched successfully",
        data,
        result.page,
        result.limit,
        result.total,
        request,
    )


@router.get("/{teacher_id}")
def get_teacher(
    teacher_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("teachers.read"))],
):
    teacher = TeacherService(db).get_teacher(teacher_id)
    return success_response(
        "Teacher fetched successfully",
        TeacherResponse.model_validate(teacher).model_dump(),
        request,
    )


@router.put("/{teacher_id}")
def update_teacher(
    teacher_id: int,
    payload: TeacherUpdateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("teachers.update"))],
):
    teacher = TeacherService(db).update_teacher(teacher_id, payload, current_user.id, request)
    return success_response(
        "Teacher updated successfully",
        TeacherResponse.model_validate(teacher).model_dump(),
        request,
    )


@router.post("/{teacher_id}/subject", status_code=status.HTTP_201_CREATED)
def assign_subject(
    teacher_id: int,
    payload: SubjectAssignRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("teachers.update"))],
):
    TeacherService(db).assign_subject(teacher_id, payload, current_user.id, request)
    return success_response("Subject assigned successfully", {"subject_id": payload.subject_id}, request)


@router.get("/{teacher_id}/subject")
def list_teacher_subjects(
    teacher_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("teachers.read"))],
):
    subjects = TeacherService(db).list_subjects(teacher_id)
    data = [{"id": s.id, "code": s.code, "name": s.name} for s in subjects]
    return success_response("Subjects fetched successfully", data, request)


@router.post("/{teacher_id}/class", status_code=status.HTTP_201_CREATED)
def assign_class(
    teacher_id: int,
    payload: ClassAssignRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("teachers.update"))],
):
    TeacherService(db).assign_class(teacher_id, payload, current_user.id, request)
    return success_response("Class assigned successfully", {"class_id": payload.class_id}, request)


@router.get("/{teacher_id}/class")
def list_teacher_classes(
    teacher_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("teachers.read"))],
):
    classes = TeacherService(db).list_classes(teacher_id)
    data = [
        {"id": c.id, "name": c.name, "section": c.section, "academic_year": c.academic_year}
        for c in classes
    ]
    return success_response("Classes fetched successfully", data, request)


@router.post("/{teacher_id}/attendance", status_code=status.HTTP_201_CREATED)
def record_attendance(
    teacher_id: int,
    payload: AttendanceCreateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("teachers.update"))],
):
    record = TeacherService(db).record_attendance(teacher_id, payload, current_user.id, request)
    return success_response(
        "Attendance recorded successfully",
        AttendanceResponse.model_validate(record).model_dump(),
        request,
    )


@router.get("/{teacher_id}/salary")
def get_teacher_salary(
    teacher_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("teachers.read"))],
):
    salary = TeacherService(db).get_salary(teacher_id)
    return success_response(
        "Salary fetched successfully",
        SalaryResponse.model_validate(salary).model_dump(),
        request,
    )


@router.post("/{teacher_id}/salary/payments", status_code=status.HTTP_201_CREATED)
def create_salary_payment(
    teacher_id: int,
    payload: SalaryPaymentCreateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("teachers.salary.pay"))],
):
    payment = TeacherService(db).create_salary_payment(
        teacher_id,
        payload,
        current_user.id,
        request,
    )
    return success_response(
        "Salary payment recorded successfully",
        SalaryPaymentResponse.model_validate(payment).model_dump(),
        request,
    )
