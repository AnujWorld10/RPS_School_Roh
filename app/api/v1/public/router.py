"""Aggregates all public (unauthenticated) v1 routes."""

from fastapi import APIRouter

from app.api.v1.public.student import routes as student_public_routes

public_router = APIRouter()
public_router.include_router(
    student_public_routes.router,
    prefix="/student",
)
