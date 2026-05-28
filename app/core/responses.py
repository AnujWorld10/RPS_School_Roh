from datetime import UTC, datetime
from typing import Any

from fastapi import Request
from pydantic import BaseModel, Field


class ResponseMeta(BaseModel):
    request_id: str
    timestamp: str


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total_records: int
    total_pages: int


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Any = None
    errors: list[dict[str, Any]] | None = None
    meta: ResponseMeta | None = None
    pagination: PaginationMeta | None = None
    warnings: list[dict[str, str]] | None = None


def _timestamp() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _request_id(request: Request | None) -> str:
    if request is None:
        return "unknown"
    return getattr(request.state, "request_id", "unknown")


def success_response(
    message: str,
    data: Any = None,
    request: Request | None = None,
    warnings: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    return APIResponse(
        success=True,
        message=message,
        data=data,
        errors=None,
        meta=ResponseMeta(request_id=_request_id(request), timestamp=_timestamp()),
        warnings=warnings,
    ).model_dump(exclude_none=True)


def paginated_response(
    message: str,
    data: list[Any],
    page: int,
    limit: int,
    total_records: int,
    request: Request | None = None,
) -> dict[str, Any]:
    total_pages = (total_records + limit - 1) // limit if limit > 0 else 0
    return APIResponse(
        success=True,
        message=message,
        data=data,
        errors=None,
        pagination=PaginationMeta(
            page=page,
            limit=limit,
            total_records=total_records,
            total_pages=total_pages,
        ),
        meta=ResponseMeta(request_id=_request_id(request), timestamp=_timestamp()),
    ).model_dump(exclude_none=True)


def error_response(
    message: str,
    errors: list[dict[str, Any]],
    request: Request | None = None,
) -> dict[str, Any]:
    return APIResponse(
        success=False,
        message=message,
        data=None,
        errors=errors,
        meta=ResponseMeta(request_id=_request_id(request), timestamp=_timestamp()),
    ).model_dump(exclude_none=True)
