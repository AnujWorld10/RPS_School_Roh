from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.permission import Permission
from app.models.role import Role, UserRole
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, User)

    def get_by_email(self, email: str) -> User | None:
        stmt = (
            select(User)
            .where(User.email == email, User.deleted_at.is_(None))
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        return self.session.scalar(stmt)

    def get_with_roles(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id, User.deleted_at.is_(None))
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        return self.session.scalar(stmt)

    def email_exists(self, email: str, exclude_id: int | None = None) -> bool:
        stmt = select(User.id).where(User.email == email, User.deleted_at.is_(None))
        if exclude_id:
            stmt = stmt.where(User.id != exclude_id)
        return self.session.scalar(stmt) is not None

    def phone_exists(self, phone: str, exclude_id: int | None = None) -> bool:
        stmt = select(User.id).where(User.phone == phone, User.deleted_at.is_(None))
        if exclude_id:
            stmt = stmt.where(User.id != exclude_id)
        return self.session.scalar(stmt) is not None

    def assign_roles(self, user_id: int, role_ids: list[int]) -> None:
        for role_id in role_ids:
            self.session.merge(UserRole(user_id=user_id, role_id=role_id))
        self.session.flush()


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Role)

    def get_by_codes(self, codes: list[str]) -> list[Role]:
        stmt = select(Role).where(Role.code.in_(codes), Role.is_active.is_(True))
        return list(self.session.scalars(stmt).all())


class PermissionRepository(BaseRepository[Permission]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Permission)
