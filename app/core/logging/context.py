"""Helpers for attaching HTTP request context to log records."""

from __future__ import annotations

from fastapi import Request


def resolve_endpoint(request: Request) -> str | None:
    """Return the FastAPI route name, if available."""
    route = request.scope.get("route")
    if route is None:
        return None
    return getattr(route, "name", None)


def resolve_path_template(request: Request) -> str:
    """Return the route path template (e.g. ``/api/v1/inquiries/{id}``)."""
    route = request.scope.get("route")
    if route is not None and getattr(route, "path", None):
        return route.path
    return request.url.path


def request_log_extra(request: Request, **fields) -> dict:
    """Build a standard ``extra`` dict for request-scoped log records."""
    extra = {
        "request_id": getattr(request.state, "request_id", None),
        "method": request.method,
        "path": resolve_path_template(request),
        "endpoint": resolve_endpoint(request),
        "client_ip": request.client.host if request.client else None,
    }
    extra.update(fields)
    return extra
