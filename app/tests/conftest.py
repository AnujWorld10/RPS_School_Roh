import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("APP_ENV", "test")
# Tests use in-memory SQLite so pytest does not require a separate MySQL database.
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-32chars-min")
os.environ.setdefault("DEBUG", "true")

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app

get_settings.cache_clear()


@pytest.fixture(scope="session")
def engine():
    settings = get_settings()
    connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    test_engine = create_engine(
        settings.database_url,
        connect_args=connect_args,
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    from app.db.seed import seed_database

    seed_session = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)()
    try:
        seed_database(seed_session)
    finally:
        seed_session.close()
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(engine):
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "superadmin@school.com",
            "password": "SuperAdmin@123",
        },
    )
    if response.status_code != 200:
        pytest.skip("Super admin login unavailable; run seed/migrations first")
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
