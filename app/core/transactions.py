from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.orm import Session


@contextmanager
def transaction(session: Session) -> Generator[Session, None, None]:
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
