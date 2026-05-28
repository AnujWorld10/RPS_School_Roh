from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions, require_roles
from app.core.pagination import PaginationParams, pagination_params
from app.core.responses import paginated_response, success_response
from app.db.session import get_db
from app.models.user import User
from app.schemas.classes import ClassCreateRequest, ClassResponse, ClassUpdateRequest
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
    academic_year: str | None = Query(default=None),
    status: str | None = Query(default=None),
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
