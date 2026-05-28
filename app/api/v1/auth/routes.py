from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.responses import success_response
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth import AuthService, _collect_roles_and_permissions

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserRegisterRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles("SUPER_ADMIN", "ADMIN"))],
):
    user = AuthService(db).register(payload, current_user.id, request)
    roles, _ = _collect_roles_and_permissions(user)
    data = {
        "id": user.id,
        "email": user.email,
        "roles": roles,
        "status": user.status,
    }
    return success_response("User registered successfully", data, request)


@router.post("/login")
def login_user(
    payload: LoginRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    data = AuthService(db).login(payload, request)
    return success_response("Login successful", data, request)


@router.post("/refresh-token")
def refresh_token(
    payload: RefreshTokenRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    data = AuthService(db).refresh(payload.refresh_token)
    return success_response("Token refreshed successfully", data, request)


@router.get("/me")
def get_me(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
):
    roles, permissions = _collect_roles_and_permissions(current_user)
    data = UserResponse(
        id=current_user.id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
        phone=current_user.phone,
        roles=roles,
        permissions=permissions,
        status=current_user.status,
    )
    return success_response("User fetched successfully", data.model_dump(), request)


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    AuthService(db).change_password(current_user.id, payload, request)
    return success_response("Password changed successfully", None, request)


@router.post("/logout")
def logout_user(
    payload: LogoutRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    AuthService(db).logout(payload.refresh_token, current_user.id, request)
    return success_response("Logout successful", None, request)


@router.get("/verify-token")
def verify_token(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
):
    return success_response(
        "Token is valid",
        {"valid": True, "user_id": current_user.id},
        request,
    )
