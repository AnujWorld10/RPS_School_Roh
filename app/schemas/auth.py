from pydantic import BaseModel, Field, field_validator

from app.schemas.email import AppEmail


class UserRegisterRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: AppEmail
    phone: str | None = Field(default=None, max_length=30)
    password: str = Field(..., min_length=8)
    role_codes: list[str] = Field(..., min_length=1)

    @field_validator("first_name", "last_name", "phone", mode="before")
    @classmethod
    def strip_strings(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value


class LoginRequest(BaseModel):
    email: AppEmail
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str | None
    roles: list[str]
    permissions: list[str] | None = None
    status: str


class RegisterUserResponse(BaseModel):
    id: int
    email: str
    roles: list[str]
    status: str


class VerifyTokenResponse(BaseModel):
    valid: bool
    user_id: int
