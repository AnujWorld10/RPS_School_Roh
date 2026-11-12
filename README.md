# School Management System API

A FastAPI backend for school admissions, class curriculum, and examination results. It
supports public student inquiries, staff review and interviews, admission documents,
enrollment, classes, subjects, teachers, attendance, salary payments, authentication, and
role-based permissions.

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

## Frontend

The React application lives in `frontend/` and is a standalone Vite project. It uses the
backend bearer-token authentication API and supports teacher, class, subject, student,
inquiry, interview, admission, admission-document, and academic results workflows.

Install Node.js LTS, then from the repository root:

```powershell
Set-Location frontend
Copy-Item .env.example .env
npm install
npm run dev
```

The development server prints its local URL (Vite defaults to `http://localhost:5173`).
`VITE_API_BASE_URL` in `frontend/.env` defaults to
`http://127.0.0.1:8000/api/v1`. Before using the login page, ensure the backend's
`CORS_ORIGINS` setting includes the exact frontend origin (for example
`http://localhost:5173`; add `http://127.0.0.1:5173` too if you open Vite by that address),
then restart the API. The root `.env.example` lists both Vite origins; if you already have
a backend `.env`, add them to its comma-separated `CORS_ORIGINS` value rather than
replacing your other allowed origins.

The frontend uses the real `/auth/login`, `/auth/me`, `/auth/refresh-token`, and
`/auth/logout` bearer-token endpoints. Tokens are held in memory only, so a page reload
requires signing in again. The school modules load and update records through the backend:

- Teachers: search, paginate, create, edit, and assign teachers to class-specific subjects.
- Classes: filter, paginate, create, edit, delete, check readiness, assign one class teacher,
  and manage subject offerings.
- Subjects: search, paginate, create, edit, activate, and deactivate catalog subjects.
- Students: search, paginate, filter by status/class, view profiles and class subjects, edit
  profiles, assign enrollment, update supported status transitions, and soft-delete.
- Inquiries: submit public intake, search and filter staff inquiries, review/status transitions,
  internal notes, class mapping, and start an admission after an interview pass.
- Interviews: schedule and record results from an inquiry's interview history. The backend
  has no global interview list, so an inquiry must be selected first.
- Admissions: list and edit inquiry-linked applications, review/reject/approve, enroll approved
  applications, and upload/verify four required document types; migration and character
  certificates are optional.
- Dashboard: permission-scoped counts and admission-status totals from
  `GET /api/v1/dashboard/summary`, plus recent inquiries from the inquiry-list API.
  Upcoming interviews show the count and next five schedules in the configured
  `SCHOOL_TIMEZONE`; applicant names are included only for accounts with both
  `interviews.read` and `inquiries.read`. Unauthorized metrics are returned as `null` and
  hidden by the frontend.

Relationship selectors use the available list APIs and are limited to the first 100 records;
the backend has no bulk-assignment or dedicated lookup endpoints. Class lists support academic
year and status filters, but not name search. Staff inquiry editing is limited to internal
notes and requested-class mapping; applicant profile editing is not available in the staff
API. The backend does not expose a document download endpoint, so stored paths are shown as
status only, not as browser links. Attendance and salary pages remain placeholders.

Run frontend checks from `frontend/`:

```powershell
npm run typecheck
npm run lint
npm run test:run
npm run build
```

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
