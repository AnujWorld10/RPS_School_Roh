# School Management System API

A FastAPI backend for school admissions and core school operations. It supports public
student inquiries, staff review and interviews, admission documents, enrollment, classes,
students, teachers, attendance, salary payments, authentication, and role-based permissions.

The API contract is available at `/docs` and `/openapi.json` when the service is running.
See the [technical guide](docs/technical-documentation.md) for architecture and operations,
the [API reference](docs/api-reference.md) for endpoint and schema details, and the
[database schema reference](docs/database-schema-reference.md) for the configured database
snapshot.

## Technology

Python 3.12+, FastAPI, SQLAlchemy 2.x, MySQL 8.0.16+, Alembic, Pydantic v2, JWT, Argon2,
Pytest, Ruff, and optional Docker Compose.

## Quick start (Windows PowerShell)

### Prerequisites

- Python 3.12 or later
- MySQL 8.0.16 or later, or Docker Desktop with Docker Compose
- A MySQL database and account for this application

### 1. Create the database

Create an empty database in MySQL, for example:

```sql
CREATE DATABASE school_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Configure the environment

From the repository root:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set a database URL matching your local MySQL account and a unique
`JWT_SECRET_KEY`. Do not copy sample values or commit `.env`. To bootstrap the first
administrator, set both `INITIAL_ADMIN_EMAIL` and `INITIAL_ADMIN_PASSWORD`; the seed step
uses these values. They are not created simply by starting the API.

### 3. Install, migrate, and seed

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
alembic upgrade head
python -m scripts.seed_db
```

If PowerShell blocks environment activation for this session, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

### 4. Start and check the API

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` for Swagger UI. Check `http://127.0.0.1:8000/live`
for process liveness and `/ready` for database readiness. The API does not automatically
run migrations at startup; migrate the target database before deploying a version that
requires schema changes.

### Basic API checks

Use Swagger UI to try public endpoints without a token. Protected endpoints require the
`Authorization: Bearer <access-token>` header from `POST /api/v1/auth/login`. Inquiry
status lookup also requires the parent email and mobile originally submitted with that
inquiry; the operation details are in the [API reference](docs/api-reference.md).

## Tests and code quality

```powershell
pytest
ruff check app
```

CI runs Ruff, applies Alembic migrations to MySQL 8.4, and runs pytest. Tests use isolated
SQLite fixtures for most unit and API integration scenarios; verify deployment-specific
database and upload behavior in the target environment as well.

## Docker Compose

Set `MYSQL_ROOT_PASSWORD` in `.env`, then use the release migration service before starting
the API:

```powershell
docker compose -f docker/docker-compose.yml up -d db
docker compose -f docker/docker-compose.yml --profile release run --rm migrate
docker compose -f docker/docker-compose.yml up -d api
docker compose -f docker/docker-compose.yml ps
```

The API is published on port 8000 and Docker MySQL on host port 3307. Uploaded files use a
persistent named volume. `docker compose down -v` deletes database and upload volumes; use
it only when deleting that data is intended. See the [technical guide](docs/technical-documentation.md)
for deployment details and local-MySQL container scenarios.

## Common setup issues

- **Database connection fails:** Check that MySQL is running, the database exists, and
  `DATABASE_URL` uses the correct username, password, host, port, and database name.
- **Unknown column or missing table:** Apply migrations to the same database configured in
  `.env` with `alembic upgrade head`; the API does not migrate automatically.
- **Alembic reports a revision but application tables are missing:** Confirm the API and
  Alembic use the intended database. Only for a disposable database with no application
  tables, remove its stale `alembic_version` table and rerun `alembic upgrade head`. Do not
  reset the marker on a database containing data; see the
  [migration recovery notes](docs/technical-documentation.md#alembic-revision-and-schema-mismatch).
- **No administrator can log in:** Run `python -m scripts.seed_db` and configure both
  initial-admin values before seeding.
- **Seed command fails with `No module named 'app'`:** Run it from the repository root as
  `python -m scripts.seed_db`, not as `python scripts\seed_db.py`.
- **Import errors or incompatible Python:** Use Python 3.12+, activate the project virtual
  environment, and install `pip install -e ".[dev]"` from the repository root.

## Documentation maintenance

The API and database reference Markdown files are generated snapshots and are committed
alongside their source generators. After changing routes/schemas or database migrations,
refresh them as described in the
[technical guide](docs/technical-documentation.md#20-documentation-maintenance).
