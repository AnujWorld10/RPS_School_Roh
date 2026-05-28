from typing import Any, Generic, TypeVar

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.orm import Session

from app.core.pagination import PaginatedResult, PaginationParams
from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    def get_by_id(self, entity_id: int) -> ModelT | None:
        return self.session.get(self.model, entity_id)

    def create(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    def update(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    def delete(self, entity: ModelT) -> None:
        self.session.delete(entity)
        self.session.flush()

    def paginate(
        self,
        query: Select[Any],
        params: PaginationParams,
    ) -> PaginatedResult:
        count_query = select(func.count()).select_from(query.subquery())
        total = self.session.scalar(count_query) or 0
        sort_column = getattr(self.model, params.sort_by, None)
        if sort_column is not None:
            order = asc(sort_column) if params.sort_order == "asc" else desc(sort_column)
            query = query.order_by(order)
        items = list(
            self.session.scalars(query.offset(params.offset).limit(params.limit)).all()
        )
        return PaginatedResult(items=items, total=total, page=params.page, limit=params.limit)
