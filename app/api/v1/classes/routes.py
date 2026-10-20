from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.core.pagination import PaginationParams, pagination_params
from app.core.responses import paginated_response, success_response
from app.db.session import get_db
from app.models.enums import ClassStatus
from app.models.user import User
from app.schemas.classes import ClassCreateRequest, ClassResponse, ClassUpdateRequest
from app.schemas.subjects import (
    ClassSubjectAssignRequest,
    ClassTeacherAssignRequest,
    SubjectResponse,
)
from app.services.classes import ClassService

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_class(
    payload: ClassCreateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("classes.create"))],
):
    school_class = ClassService(db).create_class(payload, current_user.id, request)
    return success_response(
        "Class created successfully",
        ClassResponse.model_validate(school_class).model_dump(),
        request,
    )


@router.get("/")
def list_classes(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("classes.read"))],
    params: Annotated[PaginationParams, Depends(pagination_params)],
    academic_year: str | None = Query(
        default=None,
        description="Filter by academic year.",
        examples=["2026-2027"],
    ),
    status: Annotated[
        ClassStatus | None,
        Query(description="Filter by class state: active or inactive."),
    ] = None,
):
    result = ClassService(db).list_classes(params, academic_year, status)
    data = [ClassResponse.model_validate(item).model_dump() for item in result.items]
    return paginated_response(
        "Classes fetched successfully",
        data,
        result.page,
        result.limit,
        result.total,
        request,
    )


@router.get("/{class_id}")
def get_class(
    class_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("classes.read"))],
):
    school_class = ClassService(db).get_class(class_id)
    return success_response(
        "Class fetched successfully",
        ClassResponse.model_validate(school_class).model_dump(),
        request,
    )


@router.get("/{class_id}/readiness")
def get_class_academic_readiness(
    class_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("classes.read"))],
):
    readiness = ClassService(db).academic_readiness(class_id)
    return success_response("Class academic readiness fetched successfully", readiness, request)


@router.get("/{class_id}/subjects")
def list_class_subjects(
    class_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("classes.read"))],
):
    subjects = ClassService(db).list_subjects(class_id)
    data = [SubjectResponse.model_validate(subject).model_dump() for subject in subjects]
    return success_response("Class subjects fetched successfully", data, request)


@router.post("/{class_id}/subjects", status_code=status.HTTP_201_CREATED)
def assign_class_subject(
    class_id: int,
    payload: ClassSubjectAssignRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("classes.update"))],
):
    ClassService(db).assign_subject(
        class_id,
        payload.subject_id,
        current_user.id,
        request,
    )
    return success_response(
        "Subject assigned to class successfully",
        {"class_id": class_id, "subject_id": payload.subject_id},
        request,
    )


@router.delete("/{class_id}/subjects/{subject_id}")
def remove_class_subject(
    class_id: int,
    subject_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("classes.update"))],
):
    ClassService(db).remove_subject(class_id, subject_id, current_user.id, request)
    return success_response("Subject removed from class successfully", None, request)


@router.post("/{class_id}/class-teacher", status_code=status.HTTP_201_CREATED)
def assign_class_teacher(
    class_id: int,
    payload: ClassTeacherAssignRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("classes.update"))],
):
    ClassService(db).assign_class_teacher(
        class_id,
        payload.teacher_id,
        current_user.id,
        request,
    )
    return success_response(
        "Class teacher assigned successfully",
        {"class_id": class_id, "teacher_id": payload.teacher_id},
        request,
    )


@router.put("/{class_id}/class-teacher")
def replace_class_teacher(
    class_id: int,
    payload: ClassTeacherAssignRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("classes.update"))],
):
    ClassService(db).assign_class_teacher(
        class_id,
        payload.teacher_id,
        current_user.id,
        request,
        replace=True,
    )
    return success_response(
        "Class teacher updated successfully",
        {"class_id": class_id, "teacher_id": payload.teacher_id},
        request,
    )


@router.delete("/{class_id}/class-teacher")
def remove_class_teacher(
    class_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("classes.update"))],
):
    ClassService(db).remove_class_teacher(class_id, current_user.id, request)
    return success_response("Class teacher removed successfully", None, request)


@router.put("/{class_id}")
def update_class(
    class_id: int,
    payload: ClassUpdateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("classes.update"))],
):
    school_class = ClassService(db).update_class(class_id, payload, current_user.id, request)
    return success_response(
        "Class updated successfully",
        ClassResponse.model_validate(school_class).model_dump(),
        request,
    )


@router.delete("/{class_id}")
def delete_class(
    class_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("classes.delete"))],
):
    ClassService(db).delete_class(class_id, current_user.id, request)
    return success_response("Class deleted successfully", None, request)
