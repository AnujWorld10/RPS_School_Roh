from pydantic import BaseModel, Field, field_validator

from app.schemas.email import AppEmail


class UserRegisterRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="User's given name.")
    last_name: str = Field(..., min_length=1, max_length=100, description="User's family name.")
    email: AppEmail = Field(description="Unique email address used to sign in.")
    phone: str | None = Field(
        default=None,
        max_length=30,
        description="Optional contact phone number.",
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Initial password; use at least 8 characters and follow password policy.",
    )
    role_codes: list[str] = Field(
        ...,
        min_length=1,
        description=(
            "One or more active role codes to assign. Examples: SUPER_ADMIN, ADMIN, "
            "PRINCIPAL, TEACHER, ACCOUNTANT, ADMISSION_OFFICER, STUDENT, PARENT. "
            "Use role codes, not numeric role IDs."
        ),
        examples=[["TEACHER"]],
    )

    @field_validator("first_name", "last_name", "phone", mode="before")
    @classmethod
    def strip_strings(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value


class LoginRequest(BaseModel):
    email: AppEmail = Field(description="Email address registered to the account.")
    password: str = Field(..., description="Account password.")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(
        ...,
        description="Refresh token returned by login.",
    )


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., description="Current account password.")
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password; must meet the configured password policy.",
    )


class LogoutRequest(BaseModel):
    refresh_token: str = Field(
        ...,
        description="Refresh token to revoke.",
    )


class TokenResponse(BaseModel):
    access_token: str = Field(
        ...,
        description="Short-lived bearer access token.",
    )
    refresh_token: str | None = Field(
        default=None,
        description="Refresh token, when included by the endpoint.",
    )
    token_type: str = Field(
        default="bearer",
        description="Token type to use in the Authorization header.",
    )
    expires_in: int = Field(..., description="Access-token lifetime in seconds.")


class RefreshTokenResponse(BaseModel):
    access_token: str = Field(
        ...,
        description="New short-lived bearer access token.",
    )
    token_type: str = Field(
        default="bearer",
        description="Token type to use in the Authorization header.",
    )
    expires_in: int = Field(..., description="Access-token lifetime in seconds.")


class UserResponse(BaseModel):
    id: int = Field(..., description="Internal user ID.")
    first_name: str = Field(..., description="User's given name.")
    last_name: str = Field(..., description="User's family name.")
    email: str = Field(..., description="User's email address.")
    phone: str | None = Field(..., description="User's contact phone, if provided.")
    roles: list[str] = Field(..., description="Assigned role codes.")
    permissions: list[str] | None = Field(
        default=None,
        description="Effective permission codes, when included.",
    )
    status: str = Field(
        ...,
        description="Account lifecycle status: active, inactive, or locked.",
    )


class RegisterUserResponse(BaseModel):
    id: int = Field(..., description="Internal user ID.")
    email: str = Field(..., description="Registered email address.")
    roles: list[str] = Field(..., description="Assigned role codes.")
    status: str = Field(
        ...,
        description="Account lifecycle status: active, inactive, or locked.",
    )


class VerifyTokenResponse(BaseModel):
    valid: bool = Field(..., description="Whether the supplied access token is valid.")
    user_id: int = Field(..., description="Internal ID of the token owner.")
