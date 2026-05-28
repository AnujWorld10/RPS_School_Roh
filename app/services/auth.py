from datetime import UTC, datetime

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import (
    AuthenticationException,
    ConflictException,
    NotFoundException,
    TokenInvalidException,
    ValidationException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token,
    validate_password_strength,
    verify_password,
)
from app.core.transactions import transaction
from app.models.enums import UserStatus
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.tokens import RefreshTokenRepository
from app.repositories.users import RoleRepository, UserRepository
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    UserRegisterRequest,
)
from app.services.audit import AuditService


def _collect_roles_and_permissions(user: User) -> tuple[list[str], list[str]]:
    roles = [role.code for role in user.roles if role.is_active]
    permissions: set[str] = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.code)
    return roles, sorted(permissions)


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.roles = RoleRepository(session)
        self.tokens = RefreshTokenRepository(session)
        self.audit = AuditService(session)
        self.settings = get_settings()

    def register(self, payload: UserRegisterRequest, actor_id: int, request: Request) -> User:
        validate_password_strength(payload.password)
        if self.users.email_exists(payload.email):
            raise ConflictException("Email already exists", field="email")
        if payload.phone and self.users.phone_exists(payload.phone):
            raise ConflictException("Phone already exists", field="phone")

        roles = self.roles.get_by_codes(payload.role_codes)
        if len(roles) != len(set(payload.role_codes)):
            raise ValidationException("One or more role codes are invalid", field="role_codes")

        with transaction(self.session):
            user = self.users.create(
                User(
                    first_name=payload.first_name,
                    last_name=payload.last_name,
                    email=payload.email,
                    phone=payload.phone,
                    password_hash=hash_password(payload.password),
                    status=UserStatus.ACTIVE.value,
                )
            )
            self.users.assign_roles(user.id, [role.id for role in roles])
            user = self.users.get_with_roles(user.id)
            assert user is not None
            self.audit.log(
                action="user.register",
                entity_type="user",
                entity_id=user.id,
                actor_user_id=actor_id,
                new_values={"email": user.email, "roles": payload.role_codes},
                request=request,
            )
            return user

    def login(self, payload: LoginRequest, request: Request) -> dict:
        user = self.users.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise AuthenticationException("Invalid email or password")
        if user.status != UserStatus.ACTIVE.value:
            raise AuthenticationException("User account is not active")

        roles, permissions = _collect_roles_and_permissions(user)
        access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            roles=roles,
            permissions=permissions,
        )
        refresh_token, _jti = create_refresh_token(user_id=user.id)

        with transaction(self.session):
            user.last_login_at = datetime.now(UTC)
            self.users.update(user)
            self.tokens.create(
                RefreshToken(
                    user_id=user.id,
                    token_hash=hash_token(refresh_token),
                    expires_at=datetime.now(UTC) + self._refresh_delta(),
                )
            )
            self.audit.log(
                action="user.login",
                entity_type="user",
                entity_id=user.id,
                actor_user_id=user.id,
                request=request,
            )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.settings.access_token_expire_minutes * 60,
        }

    def refresh(self, refresh_token: str) -> dict:
        from app.core.security import decode_token

        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise TokenInvalidException("Refresh token is invalid or revoked")

        stored = self.tokens.get_by_hash(hash_token(refresh_token))
        if not stored or stored.revoked_at is not None:
            raise TokenInvalidException("Refresh token is invalid or revoked")

        user = self.users.get_with_roles(int(payload["sub"]))
        if not user or user.status != UserStatus.ACTIVE.value:
            raise TokenInvalidException("Refresh token is invalid or revoked")

        roles, permissions = _collect_roles_and_permissions(user)
        access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            roles=roles,
            permissions=permissions,
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.settings.access_token_expire_minutes * 60,
        }

    def logout(self, refresh_token: str, user_id: int, request: Request) -> None:
        stored = self.tokens.get_by_hash(hash_token(refresh_token))
        if not stored:
            raise NotFoundException("Refresh token was not found")
        with transaction(self.session):
            stored.revoked_at = datetime.now(UTC)
            self.tokens.update(stored)
            self.audit.log(
                action="user.logout",
                entity_type="user",
                entity_id=user_id,
                actor_user_id=user_id,
                request=request,
            )

    def change_password(
        self,
        user_id: int,
        payload: ChangePasswordRequest,
        request: Request,
    ) -> None:
        validate_password_strength(payload.new_password)
        if payload.current_password == payload.new_password:
            raise ValidationException(
                "New password cannot equal current password",
                field="new_password",
            )
        user = self.users.get_with_roles(user_id)
        if not user or not verify_password(payload.current_password, user.password_hash):
            raise ValidationException("Current password is incorrect", field="current_password")

        with transaction(self.session):
            user.password_hash = hash_password(payload.new_password)
            self.users.update(user)
            self.tokens.revoke_all_for_user(user_id)
            self.audit.log(
                action="user.change_password",
                entity_type="user",
                entity_id=user_id,
                actor_user_id=user_id,
                request=request,
            )

    def get_current_user(self, user_id: int) -> User:
        user = self.users.get_with_roles(user_id)
        if not user or user.status != UserStatus.ACTIVE.value:
            raise AuthenticationException("User account is not active")
        return user

    def _refresh_delta(self):
        from datetime import timedelta

        return timedelta(days=self.settings.refresh_token_expire_days)
