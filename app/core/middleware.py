import logging
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging.context import request_log_extra, resolve_path_template

logger = logging.getLogger("app.request")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Assign request IDs and log inbound/outbound HTTP traffic."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        path = resolve_path_template(request)
        base_extra = request_log_extra(request)

        logger.info(
            "request received",
            extra={**base_extra, "event": "request.received"},
        )

        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.exception(
                "request failed",
                extra={
                    **base_extra,
                    "event": "request.failed",
                    "duration_ms": duration_ms,
                },
            )
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response_size = response.headers.get("content-length")
        response.headers["X-Request-ID"] = request_id

        log_extra = {
            **base_extra,
            "event": "request.completed",
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "response_size": int(response_size) if response_size else None,
        }

        if response.status_code >= 500:
            logger.error("request completed", extra=log_extra)
        elif response.status_code >= 400:
            logger.warning("request completed", extra=log_extra)
        else:
            logger.info("request completed", extra=log_extra)

        return response
