import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestIDMiddleware
from app.core.responses import error_response, success_response
from app.db.seed import seed_database
from app.db.session import check_database_connection

settings = get_settings()
logger = logging.getLogger("app.health")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup_logging()
    if settings.app_env != "test" and settings.seed_on_startup:
        seed_database()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_v1_prefix)


def _readiness_response(request: Request) -> JSONResponse | dict:
    try:
        database_available = check_database_connection()
    except SQLAlchemyError:
        logger.exception("readiness check failed: database unavailable")
        database_available = False
    if not database_available:
        return JSONResponse(
            status_code=503,
            content=error_response(
                "Service unavailable",
                [
                    {
                        "code": "DATABASE_UNAVAILABLE",
                        "message": "Database connection is unavailable",
                    }
                ],
                request,
            ),
        )
    return success_response(
        "Service ready",
        {"status": "ready", "database": True},
        request,
    )


@app.get("/health")
@app.get("/ready")
def readiness_check(request: Request):
    """Readiness probe; returns 503 when the database cannot execute SELECT 1."""
    return _readiness_response(request)


@app.get("/live")
def liveness_check(request: Request):
    """Liveness probe; checks only that the API process can serve requests."""
    return success_response("Service alive", {"status": "alive"}, request)
