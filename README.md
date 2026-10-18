# School Management System API

A production-oriented **School Management System (SMS)** backend built with **FastAPI**, **SQLAlchemy 2.0**, **MySQL**, **Alembic**, **JWT authentication**, and **role-based access control (RBAC)**.

The API supports the full student admission pipeline: public inquiry → staff review → interview → admission & document verification → enrollment with roll number assignment—plus operational modules for classes, students, and teachers.

---

## Features

- Public student inquiry and status tracking (no login required)
- Multi-step inquiry lifecycle with append-only status history
- Interview scheduling and result recording (pass / fail / absent)
- Inquiry-linked admission with document upload and verification
- Student enrollment with business IDs (`INQ`, `ADM`, `STU`) and roll numbers
- JWT access + refresh tokens with hashed refresh storage
- Fine-grained RBAC (roles + permissions)
- Standardized JSON API responses and structured logging
- Audit logging for sensitive operations
- Docker Compose for optional MySQL + API

---

## Changelog and Technical Notes

### Phase 3 — Schema alignment, query loading, and financial validation

- Added Alembic revision `009_reconcile_orm_schema` after revision 008. It aligns legacy
  student and teacher columns with the current ORM, retains legacy columns as nullable where
  the current models no longer use them, and backfills required identity fields from linked
  legacy accounts. Unknown teacher phone numbers and joining dates remain nullable instead of
  being replaced with invented contact or employment data.
- The revision creates the missing `student_admissions`, `teacher_subjects`, `teacher_classes`,
  `teacher_attendance`, `teacher_salary`, and `teacher_salary_payments` tables, with the
  relationships, uniqueness rules, indexes, and constraints required by current services.
- Inquiry list queries batch-load status history and interviews; inquiry-admission lists
  batch-load documents; student lists batch-load their current class. Collection loading uses
  `selectinload` to avoid per-record lazy-load queries.
- Salary-payment requests require amounts with at most two decimal places and require
  `net_amount = gross_amount - deduction_amount`. Database check constraints enforce the
  same arithmetic and nonnegative/range rules if data is written outside the API.
- Class, teacher, attendance, salary, and payment states are validated against domain enums at
  the API boundary and corresponding database checks where appropriate.

Back up the database before upgrading, then apply the new forward migration from the repository
root after configuring the target database URL:

```powershell
alembic upgrade head
alembic current
```

The new database checks require a database engine that enforces `CHECK` constraints (MySQL
8.0.16 or later). Revision 009 is forward-only once the application writes data under the
reconciled schema; use a pre-upgrade backup to roll back rather than downgrading it.

### Phase 4 — Deployment and operational hardening

- API containers now start Uvicorn directly; they never run Alembic automatically. In Compose,
  the one-shot `migrate` service is enabled only through the `release` profile. Run it as a
  release step after the database is healthy and before deploying/scaling API replicas.
- Compose persists `/app/uploads` in the dedicated `school_uploads` named volume. Recreating
  or replacing the API container does not remove uploaded documents; `docker compose down -v`
  intentionally removes the volume and its data.
- `/live` is a process-only liveness probe. `/ready` and `/health` execute a database `SELECT 1`
  and return HTTP 503 with the standard error envelope when the database is unavailable. The
  Compose API healthcheck uses `/ready`.
- Public admission form fields use request-level validation and malformed multipart form values
  return the standard HTTP 422 envelope. Admission document uploads continue to enforce the
  configured extension and maximum file-size rules.
- Rate limiting is an ingress responsibility so limits apply consistently across replicas.
  Apply per-client limits to public inquiry/admission routes at the reverse proxy or WAF, set a
  request-body cap slightly above the configured upload limit for multipart overhead, and
  configure trusted proxy client-IP forwarding before enabling IP-based limits.

Compose release workflow (from the repository root):

```powershell
docker compose -f docker/docker-compose.yml up -d db
docker compose -f docker/docker-compose.yml --profile release run --rm migrate
docker compose -f docker/docker-compose.yml up -d api
docker compose -f docker/docker-compose.yml ps
```

Example Nginx ingress policy (place the `limit_req_zone` directive inside the `http` block and
the location directives inside the relevant `server` block):

```nginx
limit_req_zone $binary_remote_addr zone=school_public_forms:10m rate=10r/m;

location ~ ^/api/v1/public/student/(inquiry(?:/.*)?|admission)$ {
    client_max_body_size 6m;
    limit_req zone=school_public_forms burst=10 nodelay;
    limit_req_status 429;
    proxy_pass http://school_api;
}
```

This is a deployment starting point, not a substitute for tuning limits to expected traffic.
If the service is behind a load balancer, configure trusted real-IP sources before using the
forwarded client address for rate limiting.

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12+ |
| Framework | FastAPI |
| Server | Uvicorn |
| Database | MySQL 8.0.16+ |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (HS256) + Argon2 passwords |

---

## Quick Start

### Prerequisites

- Python 3.12+
- MySQL 8+ running locally

### 1. Create database

```sql
CREATE DATABASE IF NOT EXISTS school_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Configure environment

```powershell
"Navigate to the project root directory (where pyproject.toml is located)"
cd D:\SCHOOL_MANAGEMENT
copy .env.example .env "It will Create a local environment file from the sample configuration"
```
Edit `.env` — default local connection:

```env
DATABASE_URL=mysql+pymysql://root:mysql@localhost:3306/school_db
JWT_SECRET_KEY=your-long-random-secret-key-here
INITIAL_ADMIN_EMAIL=admin@example.com
INITIAL_ADMIN_PASSWORD=<unique-strong-password>
```

`INITIAL_ADMIN_EMAIL` and `INITIAL_ADMIN_PASSWORD` must be configured together.
The password must meet the application's strength requirements. The first startup
creates this super admin; remove both settings after the account is created.
For upgrades from versions that created `superadmin@school.com` with a built-in
password, set `INITIAL_ADMIN_EMAIL` to that address and provide a new strong
password for one startup; remove both settings afterward.

### 3. Install and Migrate

Follow these steps to set up your local development environment and initialize the database.

#### 3.1 Create and Activate Virtual Environment

```powershell
# Create the virtual environment
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

```

> **Note:** If you encounter an error stating *"...cannot be loaded because running scripts is disabled on this system,"* run the following command to allow scripts for your current session:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
> ```
> After running this, try activating the environment again with `.\.venv\Scripts\Activate.ps1`.

#### 3.2 Install Dependencies

Ensure you are in the project root directory and run:

```powershell
pip install -e ".[dev]"

```

#### 3.3 Configure Environment Variables

Before running the application, you must create your environment configuration file:

1. Navigate to the project root directory.
2. Create a file named `.env` (you can base it on the provided `.env.example` file).
3. Ensure your `DATABASE_URL` and `JWT_SECRET_KEY` are correctly configured for your local machine.

#### 3.4 Database Migrations

Once dependencies are installed and your `.env` file is configured, apply the database migrations to create the schema:

```powershell
alembic upgrade head
```

Seed the default roles, permissions, and admin data manually:

```powershell
python scripts/seed_db.py
```

If you want the app to seed on startup in development only, set `SEED_ON_STARTUP=true` in `.env`. For production, leave it `false` and run seeding manually when needed.

### 4. Run the application

```powershell
uvicorn app.main:app --reload
```

| Resource | URL |
|----------|-----|
| API | http://127.0.0.1:8000 |
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| Health check | http://127.0.0.1:8000/health |
| Readiness probe | http://127.0.0.1:8000/ready |
| Liveness probe | http://127.0.0.1:8000/live |

**Important:** Run from the **project root** using `uvicorn app.main:app`.

---

## Run with Docker

This project supports two Docker-based scenarios:

1. Docker image/container with a local MySQL database.
2. Docker image/container with Docker-managed MySQL.

### Scenario 2: Docker container + local MySQL

Use this when you want the app to run inside Docker, but your MySQL server remains on your host machine.

1. Ensure your host MySQL is running and the `school_db` database exists.
2. Update `.env` to point the container to your host database:

```env
DATABASE_URL=mysql+pymysql://root:mysql@host.docker.internal:3306/school_db
JWT_SECRET_KEY=your-long-random-secret-key-here
```

3. Build the Docker image from the project root:

```powershell
docker build -t school_api_image -f docker/Dockerfile .
```

4. Run the container using your `.env` file:

```powershell
docker run --rm -p 8000:8000 --env-file .env school_api_image
```

5. Open the app:

```text
http://localhost:8000/health
```

Notes:
- `host.docker.internal` allows the container to access MySQL on the Windows host.
- Run `alembic upgrade head` as a separate release step before starting the container.

### Scenario 3: Docker container + Docker MySQL

Use this when you want both the API and database to run entirely in Docker.

1. From the project root, start the database:

```powershell
docker compose -f docker/docker-compose.yml up -d db
```

2. Apply migrations once as a release step before starting API replicas:

```powershell
docker compose -f docker/docker-compose.yml --profile release run --rm migrate
```

3. Start the API:

```powershell
docker compose -f docker/docker-compose.yml up -d api
```

4. Check service health and watch API logs:

```powershell
docker compose -f docker/docker-compose.yml ps
docker compose -f docker/docker-compose.yml logs -f api
```

The API readiness check is available at `/ready` (and `/health`); `/live` checks only that the
API process responds. Uploaded documents persist in the `school_uploads` named volume.

5. Open the app:

```text
http://localhost:8000/health
```

5. If you need to connect to the Docker MySQL server from Windows, use:

- Host: `127.0.0.1`
- Port: `3307`
- User: `root`
- Password: `mysql`
- Database: `school_db`

6. To stop the Docker environment:

```powershell
docker compose -f docker/docker-compose.yml down
```

7. To remove the MySQL data volume and reset the database:

```powershell
docker compose -f docker/docker-compose.yml down -v
```

Important:
- Docker Compose already sets the API service `DATABASE_URL` to use the internal MySQL service host `db`.
- Compose constructs the database URL from `MYSQL_ROOT_PASSWORD`; URL-encode reserved characters
  in the password before using it in this URL.
- Do not use `localhost` inside the API container for the database when using Docker Compose.
- Re-running API containers does not run migrations; execute the release migration service before
  deploying code that needs a schema change.

---

## Initial Admin Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "the-email-configured-in-INITIAL_ADMIN_EMAIL",
  "password": "the-password-configured-in-INITIAL_ADMIN_PASSWORD"
}
```

Use the returned `access_token` as `Authorization: Bearer <token>` for protected endpoints.

New users are created via `POST /api/v1/auth/register` (requires SUPER_ADMIN or ADMIN).

---

## API Overview

| Area | Base path | Auth |
|------|-----------|------|
| Public inquiry | `/api/v1/public/student` | None |
| Authentication | `/api/v1/auth` | Mixed |
| Inquiries | `/api/v1/inquiries` | Bearer + permissions |
| Interviews | `/api/v1/interviews` | Bearer + permissions |
| Admissions | `/api/v1/inquiry-admissions` | Bearer + permissions |
| Classes | `/api/v1/classes` | Bearer + permissions |
| Students | `/api/v1/students` | Bearer + permissions |
| Teachers | `/api/v1/teachers` | Bearer + permissions |

Full endpoint catalog, schemas, workflows, and database design:

**[docs/TECHNICAL_DOCUMENTATION.md](docs/TECHNICAL_DOCUMENTATION.md)**

---

## Project Structure

```text
SCHOOL_MANAGEMENT/
|-- .github/
|   \-- workflows/
|       \-- ci.yml
|-- .vscode/
|   \-- settings.json
|-- alembic/
|   |-- versions/
|   |   |-- 000_base_tables.py
|   |   |-- 001_student_inquiry_module.py
|   |   |-- 002_phase2_interview_admission_enrollment.py
|   |   |-- 003_align_permissions_schema.py
|   |   |-- 004_align_soft_delete_columns.py
|   |   |-- 005_create_inquiry_status_history.py
|   |   |-- 006_align_audit_logs.py
|   |   |-- 007_align_refresh_tokens.py
|   |   |-- 008_inquiry_duplicate_key.py
|   |   \-- 009_reconcile_orm_schema.py
|   |-- env.py
|   \-- script.py.mako
|-- app/
|   |-- api/
|   |   |-- v1/
|   |   |   |-- admissions/
|   |   |   |   |-- __init__.py
|   |   |   \-- routes.py
|   |   |-- auth/
|   |   |   |-- __init__.py
|   |   |   \-- routes.py
|   |   |-- classes/
|   |   |   |-- __init__.py
|   |   |   \-- routes.py
|   |   |-- inquiries/
|   |   |   |-- __init__.py
|   |   |   \-- routes.py
|   |   |-- interviews/
|   |   |   |-- __init__.py
|   |   |   \-- routes.py
|   |   |-- public/
|   |   |   |-- student/
|   |   |   |   |-- __init__.py
|   |   |   |   \-- routes.py
|   |   |   |-- __init__.py
|   |   |   \-- router.py
|   |   |-- students/
|   |   |   |-- __init__.py
|   |   |   \-- routes.py
|   |   |-- teachers/
|   |   |   |-- __init__.py
|   |   |   \-- routes.py
|   |   |-- __init__.py
|   |   \-- deps.py
|   |-- core/
|   |   |-- logging/
|   |   |   |-- __init__.py
|   |   |   |-- context.py
|   |   |   |-- formatters.py
|   |   |   |-- handlers.py
|   |   |   \-- setup.py
|   |   |-- __init__.py
|   |   |-- config.py
|   |   |-- exceptions.py
|   |   |-- handlers.py
|   |   |-- middleware.py
|   |   |-- pagination.py
|   |   |-- permissions.py
|   |   |-- responses.py
|   |   |-- security.py
|   |   \-- transactions.py
|   |-- db/
|   |   |-- __init__.py
|   |   |-- base.py
|   |   |-- seed.py
|   |   \-- session.py
|   |-- models/
|   |   |-- __init__.py
|   |   |-- admission.py
|   |   |-- audit_log.py
|   |   |-- class_model.py
|   |   |-- enums.py
|   |   |-- interview.py
|   |   |-- permission.py
|   |   |-- refresh_token.py
|   |   |-- role.py
|   |   |-- student.py
|   |   |-- student_inquiry.py
|   |   |-- subject.py
|   |   |-- teacher.py
|   |   \-- user.py
|   |-- repositories/
|   |   |-- __init__.py
|   |   |-- admissions.py
|   |   |-- audit.py
|   |   |-- base.py
|   |   |-- classes.py
|   |   |-- inquiries.py
|   |   |-- inquiry_admissions.py
|   |   |-- interviews.py
|   |   |-- students.py
|   |   |-- teachers.py
|   |   |-- tokens.py
|   |   \-- users.py
|   |-- schemas/
|   |   |-- __init__.py
|   |   |-- admissions.py
|   |   |-- auth.py
|   |   |-- classes.py
|   |   |-- common.py
|   |   |-- email.py
|   |   |-- enrollment.py
|   |   |-- inquiries.py
|   |   |-- inquiry_mappers.py
|   |   |-- interviews.py
|   |   |-- students.py
|   |   \-- teachers.py
|   |-- services/
|   |   |-- __init__.py
|   |   |-- admissions.py
|   |   |-- audit.py
|   |   |-- auth.py
|   |   |-- classes.py
|   |   |-- enrollment.py
|   |   |-- inquiries.py
|   |   |-- inquiry_admissions.py
|   |   |-- interviews.py
|   |   |-- students.py
|   |   \-- teachers.py
|   |-- tests/
|   |   |-- integration/
|   |   |   |-- test_admission_flow.py
|   |   |   |-- test_auth.py
|   |   |   |-- test_auth_success.py
|   |   |   |-- test_health.py
|   |   |   |-- test_inquiry_validation.py
|   |   |   |-- test_interview_workflow.py
|   |   |   |-- test_phase1_access_controls.py
|   |   |   |-- test_phase2_workflows.py
|   |   |   |-- test_phase4_public_validation.py
|   |   |   |-- test_public_inquiry.py
|   |   |   \-- test_rbac.py
|   |   |-- unit/
|   |   |   |-- test_duplicate_inquiry_detection.py
|   |   |   |-- test_file_storage.py
|   |   |   |-- test_inquiry_ids.py
|   |   |   |-- test_inquiry_service.py
|   |   |   |-- test_inquiry_service_extended.py
|   |   |   |-- test_logging.py
|   |   |   |-- test_phase3_schemas.py
|   |   |   \-- test_security.py
|   |   |-- __init__.py
|   |   |-- conftest.py
|   |   \-- temp_public_inquiry_debug.py
|   |-- utils/
|   |   |-- __init__.py
|   |   |-- business_ids.py
|   |   |-- file_storage.py
|   |   \-- inquiry_ids.py
|   |-- __init__.py
|   \-- main.py
|-- docker/
|   |-- docker-compose.yml
|   \-- Dockerfile
|-- docs/
|   \-- TECHNICAL_DOCUMENTATION.md
|-- scripts/
|   |-- cleanup_logs.py
|   \-- seed_db.py
|-- .env.example
|-- .gitignore
|-- alembic.ini
|-- COMPREHENSIVE_TEST_REVIEW_REPORT.md
|-- DUPLICATE_INQUIRY_DETECTION.md
|-- Functionality & architecture.md
|-- IMPLEMENTATION_SUMMARY.md
|-- pyproject.toml
|-- README.md
\-- SCHOOL_MANAGEMENT_BACKEND_BLUEPRINT.md
```

Local-only files such as `.env`, uploaded documents, logs, and generated caches are excluded.

---

## Testing

```powershell
pytest
ruff check app
```

---

## Logging

- Daily application logs: `logs/RPS_YYYY-MM-DD.log`
- Daily error-only logs: `logs/RPS_ERROR_YYYY-MM-DD.log`
- Old logs are auto-cleaned at startup based on `LOG_RETENTION_DAYS`

Example `.env` logging settings:

```env
LOG_LEVEL=INFO
LOG_DIR=logs
LOG_FILE_PREFIX=RPS
LOG_ERROR_FILE_PREFIX=RPS_ERROR
LOG_RETENTION_DAYS=30
LOG_TO_CONSOLE=true
LOG_TO_FILE=true
```

Manual cleanup:

```powershell
python scripts/cleanup_logs.py
```

---

## Docker (optional)

Set `MYSQL_ROOT_PASSWORD` in the project `.env` file before starting Compose.

```powershell
docker compose -f docker/docker-compose.yml up -d
```

Uses MySQL on host port **3307** to avoid conflicting with a local MySQL on 3306.

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/TECHNICAL_DOCUMENTATION.md](docs/TECHNICAL_DOCUMENTATION.md) | Complete technical documentation (architecture, DB, APIs, security, deployment) |
| [SCHOOL_MANAGEMENT_BACKEND_BLUEPRINT.md](SCHOOL_MANAGEMENT_BACKEND_BLUEPRINT.md) | Original API blueprint reference |
| `/docs` (runtime) | Interactive OpenAPI documentation |

---

## License

Proprietary — internal school management project.
