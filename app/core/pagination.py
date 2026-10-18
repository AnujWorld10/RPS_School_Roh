from dataclasses import dataclass
from typing import Literal

from fastapi import Query
from pydantic import BaseModel, Field

DEFAULT_PAGE = 1
DEFAULT_LIMIT = 10
MAX_LIMIT = 100
DEFAULT_SORT_BY = "created_at"
DEFAULT_SORT_ORDER: Literal["asc", "desc"] = "desc"


class PaginationParams(BaseModel):
    page: int = Field(
        default=DEFAULT_PAGE,
        ge=1,
        description="1-based page number to return.",
    )
    limit: int = Field(
        default=DEFAULT_LIMIT,
        ge=1,
        le=MAX_LIMIT,
        description=f"Number of records per page, from 1 to {MAX_LIMIT}.",
    )
    sort_by: str = Field(
        default=DEFAULT_SORT_BY,
        description="Field used to sort results; supported fields depend on the endpoint.",
    )
    sort_order: Literal["asc", "desc"] = Field(
        default=DEFAULT_SORT_ORDER,
        description="Sort direction: asc or desc.",
    )

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


@dataclass
class PaginatedResult:
    items: list
    total: int
    page: int
    limit: int


def pagination_params(
    page: int = Query(
        DEFAULT_PAGE,
        ge=1,
        description="1-based page number to return.",
    ),
    limit: int = Query(
        DEFAULT_LIMIT,
        ge=1,
        le=MAX_LIMIT,
        description=f"Number of records per page, from 1 to {MAX_LIMIT}.",
    ),
    sort_by: str = Query(
        DEFAULT_SORT_BY,
        description="Field used to sort results; supported fields depend on the endpoint.",
    ),
    sort_order: Literal["asc", "desc"] = Query(
        DEFAULT_SORT_ORDER,
        description="Sort direction: asc or desc.",
    ),
) -> PaginationParams:
    return PaginationParams(page=page, limit=limit, sort_by=sort_by, sort_order=sort_order)
