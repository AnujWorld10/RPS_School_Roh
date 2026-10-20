from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.core.pagination import PaginationParams, pagination_params
from app.core.responses import paginated_response, success_response
from app.db.session import get_db
from app.models.user import User
from app.schemas.subjects import SubjectCreateRequest, SubjectResponse, SubjectUpdateRequest
from app.services.subjects import SubjectService

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_subject(
    payload: SubjectCreateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("subjects.create"))],
):
    subject = SubjectService(db).create(payload, current_user.id, request)
    return success_response(
        "Subject created successfully",
        SubjectResponse.model_validate(subject).model_dump(),
        request,
    )


@router.get("")
def list_subjects(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("subjects.read"))],
    params: Annotated[PaginationParams, Depends(pagination_params)],
    active: bool | None = Query(default=None, description="Filter by active state."),
    search: str | None = Query(default=None, min_length=1, description="Search code or name."),
):
    result = SubjectService(db).list(params, active, search)
    data = [SubjectResponse.model_validate(subject).model_dump() for subject in result.items]
    return paginated_response(
        "Subjects fetched successfully",
        data,
        result.page,
        result.limit,
        result.total,
        request,
    )


@router.get("/{subject_id}")
def get_subject(
    subject_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("subjects.read"))],
):
    subject = SubjectService(db).get(subject_id)
    return success_response(
        "Subject fetched successfully",
        SubjectResponse.model_validate(subject).model_dump(),
        request,
    )


@router.put("/{subject_id}")
def update_subject(
    subject_id: int,
    payload: SubjectUpdateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("subjects.update"))],
):
    subject = SubjectService(db).update(subject_id, payload, current_user.id, request)
    return success_response(
        "Subject updated successfully",
        SubjectResponse.model_validate(subject).model_dump(),
        request,
    )


@router.delete("/{subject_id}")
def deactivate_subject(
    subject_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("subjects.delete"))],
):
    subject = SubjectService(db).deactivate(subject_id, current_user.id, request)
    return success_response(
        "Subject deactivated successfully",
        SubjectResponse.model_validate(subject).model_dump(),
        request,
    )


@router.post("/{subject_id}/activate")
def activate_subject(
    subject_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("subjects.update"))],
):
    subject = SubjectService(db).activate(subject_id, current_user.id, request)
    return success_response(
        "Subject activated successfully",
        SubjectResponse.model_validate(subject).model_dump(),
        request,
    )
