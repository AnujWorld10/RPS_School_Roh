import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import TokenExpiredException, TokenInvalidException

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def generate_refresh_token_value() -> str:
    return secrets.token_urlsafe(48)


def create_access_token(
    *,
    user_id: int,
    email: str,
    roles: list[str],
    permissions: list[str],
) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "email": email,
        "roles": roles,
        "permissions": permissions,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(*, user_id: int) -> tuple[str, str]:
    settings = get_settings()
    jti = str(uuid4())
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": jti,
        "exp": expire,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, jti


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        message = str(exc).lower()
        if "expired" in message:
            raise TokenExpiredException() from exc
        raise TokenInvalidException() from exc


def validate_password_strength(password: str) -> None:
    from app.core.exceptions import ValidationException

    if len(password) < 8:
        raise ValidationException("Password must be at least 8 characters", field="password")
    if not any(c.isupper() for c in password):
        raise ValidationException("Password must contain an uppercase letter", field="password")
    if not any(c.islower() for c in password):
        raise ValidationException("Password must contain a lowercase letter", field="password")
    if not any(c.isdigit() for c in password):
        raise ValidationException("Password must contain a digit", field="password")
    if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password):
        raise ValidationException("Password must contain a special character", field="password")
