import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import AppException
from app.core.logging.context import request_log_extra
from app.core.responses import error_response

logger = logging.getLogger("app.errors")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        extra = request_log_extra(request, error_code=exc.code)
        if exc.status_code >= 500:
            logger.error(
                "application error: %s",
                exc.message,
                extra={**extra, "event": "exception.app"},
            )
        else:
            logger.warning(
                "application error: %s",
                exc.message,
                extra={**extra, "event": "exception.app"},
            )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(exc.message, exc.errors, request),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        extra = request_log_extra(request, event="exception.validation")
        logger.warning(
            "validation failed",
            extra={**extra, "error_count": len(exc.errors())},
        )
        errors = [
            {
                "code": "VALIDATION_ERROR",
                "field": ".".join(str(loc) for loc in err.get("loc", [])),
                "message": err.get("msg", "Validation error"),
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=error_response("Validation failed", errors, request),
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        logger.exception(
            "database integrity error",
            exc_info=exc,
            extra={**request_log_extra(request), "event": "exception.integrity"},
        )
        return JSONResponse(
            status_code=409,
            content=error_response(
                "Resource conflict",
                [{"code": "RESOURCE_CONFLICT", "message": "Database constraint violation"}],
                request,
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "unhandled exception",
            exc_info=exc,
            extra={**request_log_extra(request), "event": "exception.unhandled"},
        )
        return JSONResponse(
            status_code=500,
            content=error_response(
                "Internal server error",
                [{"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred"}],
                request,
            ),
        )
