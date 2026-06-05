# School Management System (SMS) — Enterprise Technical Documentation

**Document version:** 0.2.0  
**Last updated:** May 2026  
**API base URL (local):** `http://127.0.0.1:8000`  
**API prefix:** `/api/v1`  
**Interactive OpenAPI (Swagger):** `http://127.0.0.1:8000/docs`  
**ReDoc:** `http://127.0.0.1:8000/redoc`

> This document is aligned with the current repository structure and runtime behavior, including:  
> - layered architecture (`Routes → Schemas → Services → Repositories → ORM → MySQL`)  
> - JWT authentication + RBAC authorization  
> - daily file logging in `logs/` (including error-only logs + retention)  
> - inquiry → interview → admission → document verification → enrollment workflow

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Environment Setup & Prerequisites](#3-prerequisites--environment-setup)
4. [Complete Project Folder Structure](#4-project-folder-structure)
5. [Configuration & Settings](#5-configuration--settings)
6. [Database Documentation](#6-database-documentation)
7. [API Documentation](#7-api-documentation)
8. [Authentication & Authorization](#8-authentication--authorization)
9. [Application Workflow Documentation](#9-application-workflows)
10. [Middleware & Exception Handling](#10-middleware--exception-handling)
11. [Logging & Monitoring](#11-logging--monitoring)
12. [File Upload & Storage](#12-file-upload--storage)
13. [Background Jobs & Services](#13-background-jobs--services)
14. [Testing Documentation](#14-testing-documentation)
15. [Deployment Documentation](#15-deployment-documentation)
16. [Performance & Scalability](#16-performance--scalability)
17. [Security Best Practices](#17-security-best-practices)
18. [Important Libraries & Utilities](#18-libraries--utilities)
19. [Future Enhancements](#19-future-enhancements)
20. [README Alignment](#20-readme-documentation)
21. [Diagrams](#21-diagrams--visual-documentation)
22. [Appendix](#22-appendix)

---

## 1. Project Overview

### 1.1 Purpose

The **School Management System (SMS) Backend** is a production-oriented REST API that digitizes the full student admission lifecycle—from public inquiry through interview, document verification, enrollment, and ongoing school operations (classes, students, teachers).

The system is designed for:

- **Parents / applicants** — submit and track admission inquiries without login.
- **Admission staff** — review inquiries, schedule interviews, manage admissions and documents.
- **Administrators** — manage users, roles, classes, teachers, and operational data.
- **Auditors** — trace status changes and sensitive actions via audit logs.

### 1.2 Business Requirements (Summary)

| Domain | Requirement |
|--------|-------------|
| Public inquiry | Capture student/parent details; generate trackable `inquiry_code` |
| Inquiry lifecycle | Multi-step status pipeline with history |
| Interview | Schedule tests; record pass/fail/absent |
| Admission | Application after interview pass; required documents |
| Document verification | Staff verify/reject uploads before enrollment |
| Enrollment | Generate `student_code`, `roll_number`, assign class |
| RBAC | Role + permission based API protection |
| Audit | Log state-changing operations |
| Operations | Classes, students, teachers (profile, attendance, salary) |

**Planned (not yet implemented):** Career/HR hiring module, results, academic sessions as first-class entities, notifications, fee management.

### 1.3 Main Modules

| Module | Responsibility |
|--------|----------------|
| **Public** | Unauthenticated inquiry, status, update, admission submit |
| **Auth** | Login, refresh, logout, register (staff-only), password change |
| **Inquiries** | Staff review, status transitions, rejection |
| **Interviews** | Schedule, list, record results |
| **Admissions** | Inquiry-linked admission, documents, approve, enroll |
| **Classes** | CRUD, capacity, soft delete |
| **Students** | CRUD, status, class assignment, soft delete |
| **Teachers** | Profile, subject/class assignment, attendance, salary payments |
| **Core** | Config, security, logging, middleware, responses, exceptions |

### 1.4 Architecture Overview

Layered architecture with clear separation of concerns:

```text
HTTP Request
    → FastAPI Route (api/v1/...)
        → Pydantic Schema (validation)
            → Service (business rules, transactions)
                → Repository (SQL queries)
                    → SQLAlchemy ORM → MySQL
        ← Standardized JSON Response
```

```mermaid
flowchart TB
    subgraph Client
        WEB[Web / Mobile Client]
        PUB[Public Forms]
    end
  subgraph API["FastAPI Application"]
        R[Routes]
        S[Services]
        REP[Repositories]
    end
    subgraph Data
        MY[(MySQL)]
        FS[Local uploads/]
    end
    PUB --> R
    WEB --> R
    R --> S
    S --> REP
    REP --> MY
    S --> FS
```

**Design principles:**

- Single responsibility per layer
- Services own transaction boundaries
- Repositories do not commit; no business logic in routes
- Standard response envelope on all API responses
- Soft delete for business-critical entities where applicable

---

## 2. Technology Stack

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| Language | Python | 3.12+ | Modern typing, ecosystem, team familiarity |
| API framework | FastAPI | 0.115+ | Performance, OpenAPI auto-docs, Pydantic integration |
| ASGI server | Uvicorn | 0.32+ | Standard for FastAPI; supports `--reload` in dev |
| Database | MySQL | 8+ | Relational data, school ops, widely deployed |
| ORM | SQLAlchemy | 2.x | Mature 2.0 style, migrations via Alembic |
| Migrations | Alembic | 1.14+ | Versioned schema changes |
| Validation | Pydantic | v2 | Request/response DTOs, settings |
| Auth | JWT (python-jose) | — | Stateless access tokens + refresh flow |
| Password hashing | Passlib + Argon2 | — | Strong adaptive hashing |
| MySQL driver | PyMySQL | — | Pure Python MySQL connector |
| Testing | Pytest + HTTPX | — | Unit and integration tests |
| Linting | Ruff | — | Fast Python linter |
| Containerization | Docker + Compose | — | Reproducible DB/API environments |

**Production recommendations (not all wired in code yet):** Gunicorn + Uvicorn workers, Nginx reverse proxy, Redis cache, Celery for background jobs.

---

## 3. Environment Setup & Prerequisites

### 3.1 Required Software

| Software | Minimum version |
|----------|-----------------|
| Python | 3.12 |
| pip | Latest |
| MySQL Server | 8.0 |
| Git | Any recent |

Optional: Docker Desktop, VS Code / Cursor.

### 3.2 Database Setup

```sql
CREATE DATABASE IF NOT EXISTS school_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

Default local credentials (see `.env`):

- User: `root`
- Password: `mysql`
- Database: `school_db`
- Host: `localhost:3306`

### 3.3 Virtual Environment

```powershell
cd D:\SCHOOL_MANAGEMENT
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### 3.4 Environment Variables

Copy `.env.example` to `.env` and update the settings for your machine:

| Variable | Description | Example |
|----------|-------------|---------|
| `APP_NAME` | Application name | `school-management-api` |
| `APP_ENV` | `development` / `test` / `staging` / `production` | `development` |
| `DEBUG` | FastAPI debug | `true` |
| `API_V1_PREFIX` | API version prefix | `/api/v1` |
| `DATABASE_URL` | SQLAlchemy URL | `mysql+pymysql://root:mysql@localhost:3306/school_db` |
| `JWT_SECRET_KEY` | Signing secret (min 16 chars) | Long random string |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `30` |
| `PASSWORD_HASH_SCHEME` | Hash scheme | `argon2` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `http://localhost:3000` |
| `UPLOAD_DIR` | Document storage path | `uploads` (optional) |
| `MAX_UPLOAD_SIZE_MB` | Max upload size | `5` (optional) |
| `ALLOWED_UPLOAD_EXTENSIONS` | Allowed extensions | `pdf,jpg,jpeg,png` |

### 3.5 Migrations & Seed

```powershell
alembic upgrade head
python scripts/seed_db.py
```

Seeding is now manual by default. The `SEED_ON_STARTUP` environment variable controls whether the application seeds at startup, and it defaults to `false`.

The manual seed creates:

- Default roles and permissions
- **Super admin user** (if not exists):
  - Email: `superadmin@school.com` (legacy seed: `superadmin@school.local` also accepted at login)
  - Password: `SuperAdmin@123`

### 3.6 Run Locally

```powershell
cd D:\SCHOOL_MANAGEMENT
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Important:** Run from project root with `app.main:app`, not `main:app` from inside `app/`.

### 3.7 Docker Setup

This project supports both local and Docker database deployment modes.

#### 3.7.1 Docker container + local MySQL

Use this when your application runs in Docker but your MySQL server stays on the host machine.

1. Ensure your host MySQL is running and the `school_db` database exists.
2. Update `.env` to point to the host database from inside Docker:

```env
DATABASE_URL=mysql+pymysql://root:mysql@host.docker.internal:3306/school_db
JWT_SECRET_KEY=your-long-random-secret-key-here
```

3. Build the Docker image:

```powershell
docker build -t school_api_image -f docker/Dockerfile .
```

4. Run the container with the `.env` file:

```powershell
docker run --rm -p 8000:8000 --env-file .env school_api_image
```

5. Open the app:

```text
http://localhost:8000/health
```

#### 3.7.2 Docker container + Docker MySQL

Use this when both the API and MySQL run inside Docker.

1. Start Docker Compose from the project root:

```powershell
docker compose -f docker/docker-compose.yml up -d
```

2. Confirm services:

```powershell
docker compose -f docker/docker-compose.yml ps
```

You should see:
- `db` (MySQL)
- `api` (FastAPI)

3. Inspect logs:

```powershell
docker compose -f docker/docker-compose.yml logs -f api
```

4. Open the health endpoint:

```text
http://localhost:8000/health
```

5. Connect to Docker MySQL from Windows if needed:

- Host: `127.0.0.1`
- Port: `3307`
- User: `root`
- Password: `mysql`
- Database: `school_db`

6. Stop services:

```powershell
docker compose -f docker/docker-compose.yml down
```

7. Remove the MySQL volume for a fresh start:

```powershell
docker compose -f docker/docker-compose.yml down -v
```

---

## 4. Complete Project Folder Structure

```text
SCHOOL_MANAGEMENT/
├── app/                          # Application package
│   ├── main.py                   # FastAPI app, lifespan, health, middleware
│   ├── api/
│   │   ├── deps.py               # get_current_user, require_roles, require_permissions
│   │   └── v1/
│   │       ├── router.py         # Aggregates all v1 routers
│   │       ├── auth/             # Authentication routes
│   │       ├── public/           # Unauthenticated public routes
│   │       ├── inquiries/        # Staff inquiry management
│   │       ├── interviews/       # Interview scheduling
│   │       ├── admissions/       # Admission & documents & enrollment
│   │       ├── classes/
│   │       ├── students/
│   │       └── teachers/
│   ├── core/                     # Cross-cutting concerns
│   │   ├── config.py             # Pydantic settings (env-driven)
│   │   ├── security.py           # JWT, password hashing, token helpers
│   │   ├── permissions.py        # RBAC permission catalog + default role mapping
│   │   ├── logging/              # Centralized structured logging (daily files + retention)
│   │   │   ├── setup.py          # setup_logging()
│   │   │   ├── formatters.py     # JSON formatter with source + request context
│   │   │   ├── handlers.py       # daily named file handler + cleanup utilities
│   │   │   └── context.py        # request/endpoint extraction helpers
│   │   ├── middleware.py         # Request ID + request lifecycle logging
│   │   ├── responses.py          # Standard API envelope
│   │   ├── exceptions.py         # Custom exception types
│   │   ├── handlers.py           # Global exception handlers
│   │   ├── pagination.py         # Pagination helpers
│   │   └── transactions.py       # DB transaction context manager
│   ├── db/
│   │   ├── base.py               # Declarative Base, mixins
│   │   ├── session.py            # Engine, SessionLocal, get_db
│   │   └── seed.py               # Roles, permissions, super admin
│   ├── models/                   # SQLAlchemy ORM models
│   ├── schemas/                  # Pydantic request/response DTOs
│   ├── repositories/             # Data access layer
│   ├── services/                 # Business logic layer
│   ├── utils/                    # ID generation, file storage
│   └── tests/                    # Pytest tests
├── alembic/                      # Database migrations
│   └── versions/
├── docker/                       # Dockerfile, docker-compose.yml
├── docs/                         # Technical documentation
├── logs/                         # Daily log files (gitignored; .gitkeep kept)
├── uploads/                      # Local file uploads (gitignored)
├── scripts/                      # Operational scripts (seed_db.py, cleanup_logs.py)
├── .env.example
├── alembic.ini
├── pyproject.toml
└── README.md
```

### Layer Responsibilities

| Layer | Does | Does not |
|-------|------|----------|
| **Routes** | HTTP, status codes, Depends() | Business rules, SQL |
| **Schemas** | Input/output validation | Database access |
| **Services** | Rules, transactions, audit | Raw HTTP |
| **Repositories** | Queries, CRUD | Commit (usually), business decisions |
| **Models** | Table mapping | API shapes |

---

## 5. Configuration & Settings

Settings are loaded via `app.core.config.Settings` (Pydantic Settings) from environment variables and `.env`.

| Area | Location | Notes |
|------|----------|-------|
| Application | `config.py` | `app_name`, `debug`, `api_v1_prefix` |
| Database | `DATABASE_URL` | SQLAlchemy connection string |
| JWT | `JWT_*` | Secret, algorithm, expiry |
| CORS | `CORS_ORIGINS` | Comma-separated list |
| Uploads | `UPLOAD_DIR`, `MAX_UPLOAD_SIZE_MB` | Admission documents |
| Logging | `LOG_*` | Daily file logs, error-only logs, retention |

**Security:** Never commit `.env` or production secrets. Use strong `JWT_SECRET_KEY` in production.

### 5.1 Logging Configuration (Daily Files + Error-Only + Retention)

Logging is configured centrally in `app.core.logging.setup.setup_logging()` and is controlled via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Root logger level |
| `LOG_DIR` | `logs` | Directory for log files |
| `LOG_FILE_PREFIX` | `RPS` | Main daily log filename prefix |
| `LOG_ERROR_FILE_PREFIX` | `RPS_ERROR` | Error-only daily log filename prefix |
| `LOG_RETENTION_DAYS` | `30` | Deletes files older than N days (0 disables) |
| `LOG_TO_CONSOLE` | `true` | Emit logs to stdout (recommended in dev) |
| `LOG_TO_FILE` | `true` | Emit logs to daily log files |

Generated log files (daily):

- `logs/RPS_YYYY-MM-DD.log` (all levels)
- `logs/RPS_ERROR_YYYY-MM-DD.log` (only `ERROR` and `CRITICAL`)

Manual cleanup utility:

```powershell
python scripts/cleanup_logs.py
```

---

## 6. Database Documentation

### 6.1 Migration Order

| Revision | File | Description |
|----------|------|-------------|
| `000_base` | `000_base_tables.py` | users, roles, permissions, classes, teachers, students, audit, refresh_tokens |
| `001_student_inquiry` | `001_student_inquiry_module.py` | student_inquiries, inquiry_status_history |
| `002_phase2` | `002_phase2_interview_admission_enrollment.py` | interviews, inquiry_admissions, documents, student extensions |
| `003_align_permissions` | `003_align_permissions_schema.py` | Align `permissions` with ORM (`module`, `action`) |
| `004_soft_delete` | `004_align_soft_delete_columns.py` | Add soft-delete columns (`deleted_by`, `is_active`) to key tables |
| `005_inquiry_history` | `005_create_inquiry_status_history.py` | Recovery: create `inquiry_status_history` if missing |
| `006_audit_logs` | `006_align_audit_logs.py` | Align `audit_logs` table with ORM fields |
| `007_refresh_tokens` | `007_align_refresh_tokens.py` | Align `refresh_tokens` (`token_hash`, `updated_at`) and remove raw token storage |

#### Migration Safety Notes (Important)

- **Do not delete old Alembic revisions** in `alembic/versions/`. Alembic needs them to resolve the revision graph.
- The database stores the active revision in `alembic_version.version_num` and Alembic must be able to locate that revision file.
- For major schema refactors, prefer a planned **baseline/squash** approach (new base revision + controlled DB rebuild) rather than ad-hoc deletion.

### 6.2 Entity Relationship Diagram

```mermaid
erDiagram
    users ||--o{ user_roles : has
    roles ||--o{ user_roles : has
    roles ||--o{ role_permissions : has
    permissions ||--o{ role_permissions : has
    users ||--o{ refresh_tokens : has
    users ||--o{ audit_logs : performs

    student_inquiries ||--o{ inquiry_status_history : logs
    student_inquiries ||--o{ interview_schedules : has
    student_inquiries ||--o| inquiry_admissions : has
    classes ||--o{ student_inquiries : target
    teachers ||--o{ interview_schedules : conducts

    inquiry_admissions ||--o{ admission_documents : contains
    inquiry_admissions }o--|| classes : for
    inquiry_admissions }o--o| students : enrolls

    classes ||--o{ students : contains
    students ||--o{ student_admissions : legacy

    teachers ||--o{ teacher_subjects : teaches
    subjects ||--o{ teacher_subjects : taught
    teachers ||--o{ teacher_classes : assigned
    teachers ||--o| teacher_salary : has
    teachers ||--o{ teacher_attendance : has
    teachers ||--o{ teacher_salary_payments : receives
```

### 6.3 Core Tables

#### `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGINT | PK, AI | Internal ID |
| first_name | VARCHAR(100) | NOT NULL | |
| last_name | VARCHAR(100) | NOT NULL | |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Login identifier |
| phone | VARCHAR(30) | UNIQUE, NULL | |
| password_hash | VARCHAR(255) | NOT NULL | Argon2 hash |
| status | VARCHAR(50) | NOT NULL | active, inactive, locked |
| last_login_at | DATETIME | NULL | |
| deleted_at | DATETIME | NULL | Soft delete |
| created_at, updated_at | DATETIME | | Audit timestamps |

#### `roles` / `permissions` / `user_roles` / `role_permissions`

Standard RBAC junction model. Permission code format: `module.action` (e.g. `students.create`).

#### `student_inquiries`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGINT | PK | |
| inquiry_code | VARCHAR(20) | UNIQUE | e.g. INQ202600001 |
| serial_number | INT | UNIQUE | Year-scoped serial |
| first_name, middle_name, last_name | VARCHAR | | Student name |
| gender | VARCHAR(20) | | |
| father_name | VARCHAR(200) | | |
| date_of_birth | DATE | | |
| student_mobile, parent_mobile | VARCHAR(30) | | |
| email | VARCHAR(255) | | |
| address | TEXT | | |
| last_school, current_class, admission_for_class | VARCHAR | | Applicant text |
| admission_for_class_id | BIGINT | FK → classes.id | Optional catalog link |
| status | VARCHAR(50) | INDEX | Pipeline status |
| rejection_reason, internal_notes | TEXT | | |

**Indexes:** status, parent_mobile, email, admission_for_class_id

#### `inquiry_status_history`

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT PK | |
| inquiry_id | BIGINT FK → student_inquiries | CASCADE |
| from_status | VARCHAR(50) NULL | Previous |
| to_status | VARCHAR(50) | New status |
| changed_by | BIGINT FK → users NULL | Staff or system |
| change_reason | TEXT | |
| created_at | DATETIME | |

#### `interview_schedules`

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT PK | |
| inquiry_id | BIGINT FK | CASCADE |
| schedule_date | DATE | |
| schedule_time | TIME | |
| location | VARCHAR(255) | |
| mode | VARCHAR(20) | ONLINE / OFFLINE |
| interviewer_teacher_id | BIGINT FK → teachers | NULL |
| remarks | TEXT | |
| result | VARCHAR(20) | SCHEDULED, PASSED, FAILED, ABSENT |

#### `inquiry_admissions`

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT PK | |
| admission_code | VARCHAR(20) UNIQUE | ADM202600001 |
| inquiry_id | BIGINT FK UNIQUE | One admission per inquiry |
| class_id | BIGINT FK | Target class |
| section | VARCHAR(20) | |
| academic_year | VARCHAR(20) | |
| status | VARCHAR(50) | draft → submitted → … → approved |
| permanent_address, temporary_address | TEXT | |
| nationality, disability, blood_group | VARCHAR | |
| reason_for_school_change | TEXT | |
| student_id | BIGINT FK UNIQUE | Set after enrollment |
| approved_by, approved_at | | Staff approval |

#### `admission_documents`

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT PK | |
| admission_id | BIGINT FK | |
| document_type | VARCHAR(50) | progress_report, transfer_certificate, … |
| file_name, file_path | VARCHAR | Storage metadata |
| verification_status | VARCHAR(20) | PENDING, VERIFIED, REJECTED |
| verified_by, verified_at | | |

**Unique:** `(admission_id, document_type)`

#### `students` (extended)

| Column | Type | Description |
|--------|------|-------------|
| student_code | VARCHAR(20) UNIQUE | STU202600001 |
| inquiry_id | BIGINT FK UNIQUE | Source inquiry |
| roll_number | INT | Unique per class + academic_year |
| class_id, academic_year | | Enrollment target |

See ORM models in `app/models/` for full field lists on `classes`, `teachers`, `subjects`, `audit_logs`, `refresh_tokens`.

### 6.4 Inquiry Status Values

`PENDING` → `UNDER_REVIEW` → `PROCESSING` → `INTERVIEW_SCHEDULED` → `INTERVIEW_PASS` | `INTERVIEW_FAIL` → `DOCUMENT_PENDING` → `DOCUMENT_VERIFICATION` → `ADMISSION_SUCCESS` | `REJECTED`

---

## 7. API Documentation

### 7.1 Standard Response Envelope

All endpoints return:

**Success:**

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { },
  "errors": null,
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-05-26T10:00:00Z"
  }
}
```

**Paginated:**

```json
{
  "success": true,
  "message": "Records fetched successfully",
  "data": [],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_records": 100,
    "total_pages": 10
  },
  "errors": null,
  "meta": { "request_id": "...", "timestamp": "..." }
}
```

**Error:**

```json
{
  "success": false,
  "message": "Validation failed",
  "data": null,
  "errors": [
    { "code": "VALIDATION_ERROR", "field": "email", "message": "Invalid email" }
  ],
  "meta": { "request_id": "...", "timestamp": "..." }
}
```

### 7.2 Common Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Protected routes | `Bearer <access_token>` |
| `Content-Type` | POST/PUT with body | `application/json` or `multipart/form-data` |
| `X-Request-ID` | Optional | Client-supplied; echoed in response |

### 7.3 Error Codes

| Code | HTTP | Meaning |
|------|------|---------|
| `VALIDATION_ERROR` | 422 | Pydantic / business validation |
| `AUTH_INVALID_CREDENTIALS` | 401 | Bad login |
| `AUTH_TOKEN_EXPIRED` | 401 | JWT expired |
| `AUTH_TOKEN_INVALID` | 401 | Invalid JWT |
| `AUTH_FORBIDDEN` | 403 | Missing permission |
| `RESOURCE_NOT_FOUND` | 404 | Entity not found |
| `RESOURCE_CONFLICT` | 409 | Duplicate / constraint |
| `BUSINESS_RULE_VIOLATION` | 422 | Workflow rule failed |
| `INTERNAL_SERVER_ERROR` | 500 | Unhandled error |

### 7.4 Endpoint Catalog

Base: `/api/v1` unless noted. **Auth:** None | Bearer | Permission code.

#### Health

| Method | URL | Auth | Purpose |
|--------|-----|------|---------|
| GET | `/health` | None | Health + DB connectivity |

#### Public — Student

| Method | URL | Auth | Purpose |
|--------|-----|------|---------|
| POST | `/public/student/inquiry` | None | Submit inquiry |
| GET | `/public/student/inquiry/status/{inquiry_code}` | None | Track status |
| PUT | `/public/student/inquiry/update` | None | Update inquiry (verified) |
| POST | `/public/student/admission` | None | Submit admission (form) |

**Example — Create inquiry:**

```http
POST /api/v1/public/student/inquiry
Content-Type: application/json

{
  "first_name": "Aarav",
  "last_name": "Sharma",
  "gender": "male",
  "father_name": "Rohit Sharma",
  "dob": "2018-04-10",
  "parent_mobile": "+911234567890",
  "email": "parent@example.com",
  "address": "123 School Road",
  "last_school": "ABC School",
  "current_class": "Grade 4",
  "admission_for_class": "Grade 5"
}
```

**Success `data`:**

```json
{
  "inquiry_code": "INQ202600001",
  "status": "PENDING"
}
```

#### Auth

| Method | URL | Auth | Permission |
|--------|-----|------|------------|
| POST | `/auth/login` | None | — |
| POST | `/auth/refresh-token` | None | — |
| POST | `/auth/register` | Bearer | SUPER_ADMIN, ADMIN |
| GET | `/auth/me` | Bearer | Any active user |
| POST | `/auth/change-password` | Bearer | Any active user |
| POST | `/auth/logout` | Bearer | Any active user |
| GET | `/auth/verify-token` | Bearer | Any active user |

**Login body:**

```json
{ "email": "superadmin@school.com", "password": "SuperAdmin@123" }
```

**Login success `data`:**

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### Inquiries (Staff)

| Method | URL | Permission |
|--------|-----|------------|
| GET | `/inquiries` | inquiries.read |
| GET | `/inquiries/{id}` | inquiries.read |
| PUT | `/inquiries/{id}` | inquiries.update |
| POST | `/inquiries/{id}/review/start` | inquiries.update |
| POST | `/inquiries/{id}/review/process` | inquiries.update |
| POST | `/inquiries/{id}/reject` | inquiries.reject |

Query params for list: `page`, `limit`, `status`, `admission_for_class_id`, `search`

#### Interviews

| Method | URL | Permission |
|--------|-----|------------|
| POST | `/interviews/inquiries/{inquiry_id}/schedule` | interviews.schedule |
| GET | `/interviews/inquiries/{inquiry_id}` | interviews.read |
| POST | `/interviews/{interview_id}/result` | interviews.update |
| GET | `/interviews/{interview_id}` | interviews.read |

**Schedule body:**

```json
{
  "schedule_date": "2026-06-15",
  "schedule_time": "10:30:00",
  "location": "Room 101",
  "mode": "OFFLINE",
  "interviewer_teacher_id": 1,
  "remarks": "Bring previous report card"
}
```

**Result body:**

```json
{ "result": "PASSED", "remarks": "Good performance" }
```

#### Admissions & Enrollment

| Method | URL | Permission |
|--------|-----|------------|
| GET | `/inquiry-admissions` | admissions.read |
| POST | `/inquiries/{inquiry_id}/admission` | admissions.create |
| GET | `/inquiry-admissions/{id}` | admissions.read |
| PUT | `/inquiry-admissions/{id}` | admissions.update |
| POST | `/inquiry-admissions/{id}/documents` | admissions.update (multipart) |
| POST | `/documents/{id}/verify?verified=true` | admissions.verify_documents |
| GET | `/documents/required` | None |
| POST | `/inquiry-admissions/{id}/approve` | admissions.approve |
| POST | `/inquiry-admissions/{id}/reject` | admissions.reject |
| POST | `/inquiry-admissions/{id}/enroll` | enrollment.create |

**Required document types:** `progress_report`, `transfer_certificate`, `migration_certificate`, `character_certificate`, `student_aadhar`, `parent_aadhar`

**Enrollment success `data`:**

```json
{
  "student_id": 1,
  "student_code": "STU202600001",
  "admission_code": "ADM202600001",
  "inquiry_code": "INQ202600001",
  "class_id": 1,
  "section": "A",
  "academic_year": "2026-2027",
  "roll_number": 1
}
```

#### Classes, Students, Teachers

See OpenAPI at `/docs` for full request schemas. Summary:

| Module | Base path | Key operations |
|--------|-----------|----------------|
| Classes | `/classes` | CRUD, list with filters |
| Students | `/students` | CRUD, status, class assign, soft delete |
| Teachers | `/teachers` | CRUD, subject/class assign, attendance, salary |

---

## 8. Authentication & Authorization

### 8.1 JWT Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant API as API
    participant DB as MySQL

    C->>API: POST /auth/login (email, password)
    API->>DB: Validate user + hash
    API->>DB: Store refresh token hash
    API-->>C: access_token + refresh_token

    C->>API: GET /resource (Bearer access_token)
    API-->>C: 200 + data

    C->>API: POST /auth/refresh-token
    API->>DB: Validate refresh hash
    API-->>C: new access_token

    C->>API: POST /auth/logout (refresh_token)
    API->>DB: Revoke refresh token
```

### 8.2 Token Claims (Access)

```json
{
  "sub": "1",
  "email": "superadmin@school.com",
  "roles": ["ADMIN"],
  "permissions": ["students.create", "..."],
  "type": "access",
  "exp": 1770000000
}
```

Refresh tokens include `type: "refresh"` and `jti`; only a **hash** is stored in `refresh_tokens`.

### 8.3 RBAC

- **Roles:** SUPER_ADMIN, ADMIN, PRINCIPAL, TEACHER, ACCOUNTANT, ADMISSION_OFFICER, STUDENT, PARENT
- **Permissions:** Fine-grained `module.action` codes
- **Dependencies:** `get_current_user()`, `require_roles()`, `require_permissions()`

Seed data: `app/core/permissions.py`

### 8.4 Default User

| Email | Password | Role |
|-------|----------|------|
| superadmin@school.com | SuperAdmin@123 | SUPER_ADMIN |

Registration requires existing SUPER_ADMIN or ADMIN.

---

## 9. Application Workflow Documentation

### 9.1 Student Inquiry Workflow

```mermaid
stateDiagram-v2
    [*] --> PENDING: Public submit
    PENDING --> UNDER_REVIEW: Staff review start
    UNDER_REVIEW --> PROCESSING: Mark eligible
    PROCESSING --> INTERVIEW_SCHEDULED: Schedule interview
    INTERVIEW_SCHEDULED --> INTERVIEW_PASS: Pass
    INTERVIEW_SCHEDULED --> INTERVIEW_FAIL: Fail/Absent
    INTERVIEW_PASS --> DOCUMENT_PENDING: Admission submitted
    DOCUMENT_PENDING --> DOCUMENT_VERIFICATION: All docs verified
    DOCUMENT_VERIFICATION --> ADMISSION_SUCCESS: Enroll student
    PENDING --> REJECTED: Reject
    UNDER_REVIEW --> REJECTED: Reject
    PROCESSING --> REJECTED: Reject
```

### 9.2 Interview Workflow

1. Inquiry in `PROCESSING` or `INTERVIEW_SCHEDULED`
2. Staff schedules interview → `INTERVIEW_SCHEDULED`
3. Staff records PASSED / FAILED / ABSENT
4. Pass → `INTERVIEW_PASS`; Fail → `INTERVIEW_FAIL` (terminal for applicant)

### 9.3 Admission & Document Workflow

1. After `INTERVIEW_PASS`, submit admission (public or staff)
2. Upload 6 required document types
3. Staff verifies each document
4. When all verified → inquiry `DOCUMENT_VERIFICATION`, admission ready
5. Staff approves admission → `APPROVED`
6. Staff enrolls → student created, roll number assigned, `ADMISSION_SUCCESS`

### 9.4 Employee Hiring Workflow

**Status:** Planned (Phase 4). Not implemented in current codebase.

---

## 10. Middleware & Exception Handling

### 10.1 Request/Response Lifecycle

Request processing flow:

```mermaid
sequenceDiagram
    participant C as Client
    participant M as Middleware
    participant R as Route
    participant S as Service
    participant DB as MySQL

    C->>M: HTTP request
    M->>M: Assign request_id (X-Request-ID)
    M->>R: Forward request
    R->>R: Schema validation (Pydantic)
    R->>S: Call business service
    S->>DB: Repository queries/commands
    DB-->>S: ORM results
    S-->>R: Domain result
    R-->>M: Standard JSON envelope
    M-->>C: Response + X-Request-ID
```

### 10.2 Middleware Architecture

| Component | Location | Purpose |
|----------|----------|---------|
| Request ID + request logging middleware | `app/core/middleware.py` | Adds `X-Request-ID`, logs request received/completed/failed + duration |
| CORS middleware | `app/main.py` | Allowed origins configured by `CORS_ORIGINS` |

### 10.3 Global Exception Handling

Global handlers are registered in `app/core/handlers.py` and ensure:

- a consistent error envelope
- exception tracebacks are logged server-side
- clients never receive raw stack traces

| Exception | HTTP | Notes |
|----------|------|------|
| `AppException` subclasses | per exception | Business/auth/validation errors with structured payload |
| `RequestValidationError` | 422 | Pydantic validation errors |
| `IntegrityError` | 409 | DB constraint violations |
| `Exception` | 500 | Unhandled failures |

### 10.4 Standardized Error Response

All errors are returned in the same envelope shape (see Section 7.1). For example:

```json
{
  "success": false,
  "message": "Validation failed",
  "data": null,
  "errors": [
    { "code": "VALIDATION_ERROR", "field": "body.email", "message": "Invalid email" }
  ],
  "meta": {
    "request_id": "..."
  }
}
```

| Aspect | Implementation |
|--------|----------------|
| Format | JSON lines to daily files under `logs/` (and optional stdout) |
| Main daily file | `logs/RPS_YYYY-MM-DD.log` |
| Error-only file | `logs/RPS_ERROR_YYYY-MM-DD.log` |
| Retention | `LOG_RETENTION_DAYS` (startup cleanup + manual script `scripts/cleanup_logs.py`) |
| Request ID | `RequestIDMiddleware` — header `X-Request-ID` |
| Audit | `audit_logs` table via `AuditService` |
| Health | `GET /health` — DB ping |

**Recommendations (production):** ship JSON logs to a centralized platform (ELK/OpenSearch, Loki, CloudWatch, Datadog), add error tracking (Sentry), and metrics/tracing (Prometheus + OpenTelemetry).

---

## 11. Logging & Monitoring

### 11.1 Logging Strategy (Production-Oriented)

The system uses **structured JSON logs** for:

- request lifecycle events
- application/business errors
- unhandled exceptions (with tracebacks)
- operational events (startup, retention cleanup)

Logs are written to:

- **daily files** under `logs/` (recommended for local ops and server environments)
- optionally to **stdout** (recommended for containerized deployments + log shipping)

### 11.2 Daily Log Files (Current Implementation)

| File | Contents | Rotation | Retention |
|------|----------|----------|----------|
| `logs/RPS_YYYY-MM-DD.log` | all application logs | daily | by `LOG_RETENTION_DAYS` |
| `logs/RPS_ERROR_YYYY-MM-DD.log` | only `ERROR`/`CRITICAL` | daily | by `LOG_RETENTION_DAYS` |

If a daily file does not exist, it is created automatically. If it exists, new lines append.

### 11.3 Logged Fields (JSON)

The JSON formatter includes:

- timestamp, level, logger, message
- **endpoint name**, method, path template, request_id
- file, line, function
- duration_ms, status_code (for request completion logs)
- full exception and traceback for `.exception()` calls

### 11.4 Request/Response Logging

Request lifecycle events are produced by `RequestIDMiddleware`:

- `request.received`
- `request.completed`
- `request.failed`

### 11.5 Audit Logging (Database)

In addition to runtime logs, sensitive actions are captured in the **`audit_logs`** table via `AuditService`.

Use audit logs for compliance and business traceability; use file/stdout logs for operational troubleshooting.

### 11.6 Monitoring Recommendations (Enterprise)

Recommended observability stack options:

- **Centralized logs**: ELK / OpenSearch, Grafana Loki, CloudWatch, Datadog
- **Error tracking**: Sentry
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry

For production, the most scalable pattern is:

> JSON logs to stdout + log shipper/agent + centralized log platform  
> (optionally keep daily files on the node for local forensics)

Global handlers in `app/core/handlers.py`:

| Exception | Handler | HTTP |
|-----------|---------|------|
| `AppException` subclasses | Custom handler | Per exception |
| `RequestValidationError` | Pydantic errors | 422 |
| `IntegrityError` | DB constraint | 409 |
| `Exception` | Generic | 500 (no stack trace exposed) |

Custom types: `app/core/exceptions.py`

---

## 12. File Upload & Storage

| Setting | Default |
|---------|---------|
| Allowed | pdf, jpg, jpeg, png |
| Max size | 5 MB |
| Path | `uploads/admissions/{admission_id}/` |

Validation: `app/utils/file_storage.py` — extension and size checks.

**Security:** Store outside web root in production; scan files; use S3 with pre-signed URLs for scale.

---

## 13. Background Jobs & Services

**Status:** Not implemented (current codebase). This section defines recommended enterprise patterns for future work.

### 13.1 When to Use Background Jobs

Use a background/job system for:

- email/SMS notifications (admission status updates, interview reminders)
- virus scanning for uploaded documents
- report generation (admission lists, analytics)
- long-running exports/imports

### 13.2 Recommended Architecture Options

| Option | Best for | Notes |
|--------|----------|------|
| FastAPI `BackgroundTasks` | simple in-process tasks | not reliable across restarts; not for critical jobs |
| Celery + Redis/RabbitMQ | production-grade async jobs | retries, scheduling, concurrency control |
| RQ + Redis | simpler job queue | fewer features than Celery but easy to operate |

### 13.3 Enterprise Best Practices

- Prefer an **outbox pattern** for reliable notifications
- Store job state in DB for auditability (or use queue tooling)
- Ensure idempotency (jobs can retry)
- Add dead-letter queues for poison messages

---

## 14. Testing Documentation

```powershell
pytest
pytest app/tests/unit -v
pytest app/tests/integration -v
```

| Path | Purpose |
|------|---------|
| `app/tests/conftest.py` | SQLite in-memory DB, TestClient, seed |
| `app/tests/unit/` | Security, ID generation |
| `app/tests/integration/` | Health, auth, public inquiry |

**Default test login:** Uses seeded super admin when MySQL seed available; SQLite for isolated tests.

---

## 15. Deployment Documentation

### 14.1 Local

```powershell
pip install -e .
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 14.2 Docker Compose

```powershell
docker compose -f docker/docker-compose.yml up -d
```

This starts two containers:

- `db` → Dockerized MySQL
- `api` → FastAPI application

When using Compose:

- The API connects to MySQL at `mysql+pymysql://root:mysql@db:3306/school_db`
- The host maps MySQL container port `3306` to host port `3307`
- The API is available on host port `8000`

To watch the API logs:

```powershell
docker compose -f docker/docker-compose.yml logs -f api
```

To stop and remove the containers:

```powershell
docker compose -f docker/docker-compose.yml down
```

To reset the Docker MySQL database data:

```powershell
docker compose -f docker/docker-compose.yml down -v
```

### 14.3 Production (Recommended)

```text
Nginx (TLS) → Gunicorn (UvicornWorker) → FastAPI
                ↓
              MySQL (managed)
              S3 (uploads)
              Redis (cache/sessions — future)
```

Example Gunicorn:

```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000
```

### 14.4 CI

`.github/workflows/ci.yml` — MySQL service, Ruff, pytest, Alembic.

---

## 16. Performance & Scalability

| Feature | Status |
|---------|--------|
| Pagination | `page`, `limit` (max 100), `sort_by`, `sort_order` |
| DB pooling | SQLAlchemy `pool_pre_ping`, `pool_recycle` |
| Caching | Recommended (Redis) — not implemented |
| Background jobs | Recommended (Celery) for email/SMS — not implemented |
| Async endpoints | FastAPI async; DB sync sessions |

**Query tips:** Use `selectinload` for relationships; index filter columns; avoid N+1 in list endpoints.

---

## 17. Security Best Practices

| Area | Implementation |
|------|----------------|
| Passwords | Argon2 via Passlib |
| JWT | Short-lived access; refresh stored hashed |
| SQL injection | SQLAlchemy parameterized queries |
| Input validation | Pydantic v2 on all inputs |
| RBAC | Permission checks on protected routes |
| CORS | Configurable allowlist |
| Secrets | Environment variables only |
| Public updates | inquiry_code + email + parent_mobile verification |
| File upload | Extension whitelist, size limit |

**Recommended additions:** Rate limiting (login), HTTPS only, rotate JWT secret, WAF, forgot-password flow.

---

## 18. Important Libraries & Utilities

| Module | Purpose |
|--------|---------|
| `app/utils/inquiry_ids.py` | INQ code generation |
| `app/utils/business_ids.py` | ADM, STU codes, roll numbers |
| `app/utils/file_storage.py` | Save uploads |
| `app/schemas/inquiry_mappers.py` | Public/staff response mapping |
| `app/services/audit.py` | Audit log writes |
| `app/core/transactions.py` | `with transaction(session)` |

---

## 19. Future Enhancements

- Career / HR hiring module (employee inquiry, interview, onboarding)
- Academic sessions and sections as dedicated tables
- Results and report cards
- Student attendance
- Notifications (email/SMS) with outbox pattern
- Parent and student portals
- Fee management
- Redis caching and Celery workers
- S3/Azure blob for documents
- Forgot / reset password
- API rate limiting and OAuth2 social login

---

## 20. README Documentation

The repository `README.md` is the operational entry point for developers. It should remain consistent with this technical documentation:

- **Quick Start**: venv, install, `alembic upgrade head`, run with `uvicorn app.main:app --reload`
- **Default login**: `superadmin@school.com` / `SuperAdmin@123`
- **Logging**: daily files in `logs/` + cleanup script `python scripts/cleanup_logs.py`
- **References**: link to `docs/TECHNICAL_DOCUMENTATION.md` and OpenAPI `/docs`

If a conflict exists, prefer codebase truth:

1. OpenAPI (`/docs`) for endpoint shapes
2. `app/core/config.py` and `.env.example` for configuration
3. Alembic migration files for DB schema evolution

---

## 21. Diagrams & Visual Documentation

### 19.1 Request Lifecycle

```mermaid
sequenceDiagram
    participant C as Client
    participant M as Middleware
    participant R as Route
    participant S as Service
    participant DB as Database

    C->>M: HTTP Request
    M->>M: Assign request_id
    M->>R: Forward
    R->>R: Validate schema / auth
    R->>S: Call service
    S->>DB: Repository queries
    DB-->>S: ORM models
    S-->>R: Domain result
    R-->>M: JSON envelope
    M-->>C: Response + X-Request-ID
```

### 19.2 Module Dependencies

```mermaid
flowchart LR
    subgraph API
        PUB[public]
        AUTH[auth]
        INQ[inquiries]
        INT[interviews]
        ADM[admissions]
    end
    subgraph Services
        IS[InquiryService]
        IVS[InterviewService]
        IAS[InquiryAdmissionService]
        ES[EnrollmentService]
    end
    PUB --> IS
    INQ --> IS
    INT --> IS
    INT --> IVS
    ADM --> IAS
    ADM --> ES
    ES --> IS
```

---

## 22. Appendix

### A. Related Documents

- `SCHOOL_MANAGEMENT_BACKEND_BLUEPRINT.md` — Original API blueprint
- `README.md` — Quick start
- OpenAPI: `/docs` and `/redoc`

### B. Pagination Defaults

- `page=1`, `limit=10`, `max_limit=100`
- `sort_by=created_at`, `sort_order=desc`

### C. Business ID Formats

| Entity | Format | Example |
|--------|--------|---------|
| Inquiry | INQ{YYYY}{5-digit} | INQ202600001 |
| Admission | ADM{YYYY}{5-digit} | ADM202600001 |
| Student | STU{YYYY}{5-digit} | STU202600001 |
| Roll number | Integer per class+year | 1, 2, 3… |

---

*End of Technical Documentation*
