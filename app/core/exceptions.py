from typing import Any


class AppException(Exception):
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.errors = errors or [{"code": code, "message": message}]
        super().__init__(message)


class ValidationException(AppException):
    def __init__(self, message: str, field: str | None = None) -> None:
        errors = [{"code": "VALIDATION_ERROR", "message": message}]
        if field:
            errors[0]["field"] = field
        super().__init__(message, code="VALIDATION_ERROR", status_code=422, errors=errors)


class AuthenticationException(AppException):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(
            message,
            code="AUTH_INVALID_CREDENTIALS",
            status_code=401,
            errors=[{"code": "AUTH_INVALID_CREDENTIALS", "message": message}],
        )


class TokenExpiredException(AppException):
    def __init__(self, message: str = "Token has expired") -> None:
        super().__init__(
            message,
            code="AUTH_TOKEN_EXPIRED",
            status_code=401,
            errors=[{"code": "AUTH_TOKEN_EXPIRED", "message": message}],
        )


class TokenInvalidException(AppException):
    def __init__(self, message: str = "Token is invalid") -> None:
        super().__init__(
            message,
            code="AUTH_TOKEN_INVALID",
            status_code=401,
            errors=[{"code": "AUTH_TOKEN_INVALID", "message": message}],
        )


class AuthorizationException(AppException):
    def __init__(self, message: str = "Access forbidden") -> None:
        super().__init__(
            message,
            code="AUTH_FORBIDDEN",
            status_code=403,
            errors=[{"code": "AUTH_FORBIDDEN", "message": message}],
        )


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(
            message,
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            errors=[{"code": "RESOURCE_NOT_FOUND", "message": message}],
        )


class ConflictException(AppException):
    def __init__(self, message: str, field: str | None = None) -> None:
        errors = [{"code": "RESOURCE_CONFLICT", "message": message}]
        if field:
            errors[0]["field"] = field
        super().__init__(message, code="RESOURCE_CONFLICT", status_code=409, errors=errors)


class BusinessRuleException(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            code="BUSINESS_RULE_VIOLATION",
            status_code=422,
            errors=[{"code": "BUSINESS_RULE_VIOLATION", "message": message}],
        )
