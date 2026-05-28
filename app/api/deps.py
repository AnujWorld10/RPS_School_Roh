from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import AuthorizationException, TokenInvalidException
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.services.auth import AuthService, _collect_roles_and_permissions

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None or not credentials.credentials:
        raise TokenInvalidException("Valid access token is required")
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise TokenInvalidException("Valid access token is required")
    user = AuthService(db).get_current_user(int(payload["sub"]))
    return user


def require_roles(*role_codes: str) -> Callable:
    def dependency(user: Annotated[User, Depends(get_current_user)]) -> User:
        roles, _ = _collect_roles_and_permissions(user)
        if not any(role in roles for role in role_codes):
            raise AuthorizationException()
        return user

    return dependency


def require_permissions(*permission_codes: str) -> Callable:
    def dependency(user: Annotated[User, Depends(get_current_user)]) -> User:
        _, permissions = _collect_roles_and_permissions(user)
        if not any(permission in permissions for permission in permission_codes):
            raise AuthorizationException()
        return user

    return dependency
