from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, RefreshToken)

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        return self.session.scalar(stmt)

    def revoke_all_for_user(self, user_id: int) -> None:
        stmt = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
        tokens = self.session.scalars(stmt).all()
        now = datetime.now(UTC)
        for token in tokens:
            token.revoked_at = now
        self.session.flush()
