from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestIDMiddleware
from app.core.responses import success_response
from app.db.seed import seed_database
from app.db.session import check_database_connection

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup_logging()
    if settings.seed_on_startup:
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


@app.get("/health")
def health_check(request: Request):
    db_ok = False
    try:
        db_ok = check_database_connection()
    except Exception:
        db_ok = False
    status_value = "healthy" if db_ok else "degraded"
    return success_response(
        "Health check completed",
        {"status": status_value, "database": db_ok},
        request,
    )
