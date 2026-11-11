from fastapi import APIRouter

from app.api.v1.admissions import routes as admissions_routes
from app.api.v1.auth import routes as auth_routes
from app.api.v1.classes import routes as classes_routes
from app.api.v1.dashboard import routes as dashboard_routes
from app.api.v1.fees import routes as fees_routes
from app.api.v1.inquiries import routes as inquiries_routes
from app.api.v1.interviews import routes as interviews_routes
from app.api.v1.public.router import public_router
from app.api.v1.role_portal import routes as role_portal_routes
from app.api.v1.students import routes as students_routes
from app.api.v1.subjects import routes as subjects_routes
from app.api.v1.teachers import routes as teachers_routes

api_router = APIRouter()
api_router.include_router(public_router, prefix="/public", tags=["public"])
api_router.include_router(role_portal_routes.router, tags=["role portals"])
api_router.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
api_router.include_router(classes_routes.router, prefix="/classes", tags=["classes"])
api_router.include_router(dashboard_routes.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(fees_routes.router, prefix="/fees", tags=["fees"])
api_router.include_router(inquiries_routes.router, prefix="/inquiries", tags=["inquiries"])
api_router.include_router(interviews_routes.router, prefix="/interviews", tags=["interviews"])
api_router.include_router(students_routes.router, prefix="/students", tags=["students"])
api_router.include_router(subjects_routes.router, prefix="/subjects", tags=["subjects"])
api_router.include_router(admissions_routes.router, tags=["admissions"])
api_router.include_router(teachers_routes.router, prefix="/teachers", tags=["teachers"])
