# School Management System — Technical Documentation

**Last updated:** October 2026  
**API base URL (local):** `http://127.0.0.1:8000`  
**API prefix:** `/api/v1`  
**Interactive OpenAPI (Swagger):** `http://127.0.0.1:8000/docs`  
**ReDoc:** `http://127.0.0.1:8000/redoc`

> This guide documents the current implementation. Use the generated API and database
> references for exhaustive field-level details and inspect source where a snapshot or an
> example needs confirmation. The implemented architecture includes:
> - layered architecture (`Routes → Schemas → Services → Repositories → ORM → MySQL`)
> - JWT authentication + RBAC authorization  
> - daily file logging in `logs/` (including error-only logs + retention)  
> - inquiry → interview → admission → document verification → enrollment workflow

> This repository previously contained design proposals and historical test and implementation
> reports. Their unverified or superseded details are not current specifications; current
> behavior below is based on source, migrations, tests, and the generated references.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Environment Setup & Prerequisites](#3-environment-setup--prerequisites)
4. [Complete Project Folder Structure](#4-complete-project-folder-structure)
5. [Configuration & Settings](#5-configuration--settings)
6. [Database Documentation](#6-database-documentation)
7. [API Documentation](#7-api-documentation)
8. [Authentication & Authorization](#8-authentication--authorization)
9. [Application Workflow Documentation](#9-application-workflow-documentation)
10. [Middleware & Exception Handling](#10-middleware--exception-handling)
11. [Logging & Monitoring](#11-logging--monitoring)
12. [File Upload & Storage](#12-file-upload--storage)
13. [Background Jobs & Services](#13-background-jobs--services)
14. [Testing Documentation](#14-testing-documentation)
15. [Deployment Documentation](#15-deployment-documentation)
16. [Performance & Scalability](#16-performance--scalability)
17. [Security Best Practices](#17-security-best-practices)
18. [Important Libraries & Utilities](#18-important-libraries--utilities)
19. [Future Enhancements](#19-future-enhancements)
20. [Documentation Maintenance](#20-documentation-maintenance)
21. [Diagrams](#21-diagrams--visual-documentation)
22. [Appendix](#22-appendix)
23. [Verification Checklist](#23-verification-checklist)

---

## 1. Project Overview

### 1.1 Purpose

The **School Management System (SMS) backend** is a REST API that digitizes the full student admission lifecycle—from public inquiry through interview, document verification, enrollment, and ongoing school operations (classes, students, teachers).

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
| Operations | Classes, subjects, students, teachers (profile, attendance, salary) |

**Planned (not yet implemented):** Career/HR hiring module, results, academic sessions as first-class entities, notifications, fee management.

### 1.3 Main Modules

| Module | Responsibility |
|--------|----------------|
| **Public** | Unauthenticated inquiry, status, update, admission submit |
| **Auth** | Login, refresh, logout, register (staff-only), password change |
| **Inquiries** | Staff review, status transitions, rejection |
| **Interviews** | Schedule, list, record results |
| **Admissions** | Inquiry-linked admission, documents, approve, enroll |
| **Classes** | CRUD, capacity, class teacher, subject offerings, readiness, soft delete |
| **Subjects** | Subject catalog CRUD, search, activation/deactivation |
| **Students** | CRUD, status, class assignment, soft delete |
| **Teachers** | Profile, legacy subject/class links, class-scoped subject teaching, attendance, salary payments |
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
| Database | MySQL | 8.0.16+ | Relational data, school operations, enforced check constraints |
| ORM | SQLAlchemy | 2.x | Mature 2.0 style, migrations via Alembic |
| Migrations | Alembic | 1.14+ | Versioned schema changes |
| Validation | Pydantic | v2 | Request/response DTOs, settings |
| Auth | JWT (python-jose) | — | Stateless access tokens + refresh flow |
| Password hashing | Passlib + Argon2 | — | Strong adaptive hashing |
| MySQL driver | PyMySQL | — | Pure Python MySQL connector |
| Testing | Pytest + HTTPX | — | Unit and integration tests |
| Linting | Ruff | — | Fast Python linter |
| Containerization | Docker + Compose | — | Reproducible DB/API environments |

**Deployment options, not bundled application components:** Gunicorn with Uvicorn workers
and Nginx can be used in a production deployment. Redis and a job queue are not currently
implemented.

---

## 3. Environment Setup & Prerequisites

### 3.1 Required Software

| Software | Minimum version |
|----------|-----------------|
| Python | 3.12 |
| pip | Latest |
| MySQL Server | 8.0.16 |
| Git | Any recent |

Optional: Docker Desktop, VS Code / Cursor.

### 3.2 Database Setup

```sql
CREATE DATABASE IF NOT EXISTS school_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

Configure the database URL in `.env` for your own MySQL account and database. Do not rely
on example credentials; the project does not provision a production database account.

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
| `DATABASE_URL` | SQLAlchemy URL for your database | `mysql+pymysql://<user>:<password>@localhost:3306/school_db` |
| `JWT_SECRET_KEY` | Signing secret; at least 32 random characters in production | Unique random string |
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
python -m scripts.seed_db
```

Seeding is now manual by default. The `SEED_ON_STARTUP` environment variable controls whether the application seeds at startup, and it defaults to `false`.

The manual seed creates:

- Default roles and permissions
- **Initial super admin** only when `INITIAL_ADMIN_EMAIL` and
  `INITIAL_ADMIN_PASSWORD` are both configured. Use a unique strong password and
  remove both settings after the account is created. The settings are consumed when the
  seed operation runs; setting them alone does not create an account. No default
  administrator credentials are shipped.

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

4. Run the migration as an explicit release step:

```powershell
docker run --rm --env-file .env school_api_image alembic upgrade head
```

5. Start the API with a persistent uploads volume:

```powershell
docker volume create school_uploads
docker run --rm -p 8000:8000 --env-file .env `
  -v school_uploads:/app/uploads school_api_image
```

6. Open the app:

```text
http://localhost:8000/health
```

#### 3.7.2 Docker container + Docker MySQL

Use this when both the API and MySQL run inside Docker.

1. Start MySQL from the project root:

```powershell
docker compose -f docker/docker-compose.yml up -d db
```

2. Apply migrations once, before starting or scaling API instances:

```powershell
docker compose -f docker/docker-compose.yml --profile release run --rm migrate
```

3. Start API instances:

```powershell
docker compose -f docker/docker-compose.yml up -d api
```

4. Check service state and inspect logs:

```powershell
docker compose -f docker/docker-compose.yml ps
docker compose -f docker/docker-compose.yml logs -f api
```

5. Open the readiness endpoint:

```text
http://localhost:8000/ready
```

6. Connect to Docker MySQL from Windows if needed:

- Host: `127.0.0.1`
- Port: `3307`
- User: `root`
- Password: the `MYSQL_ROOT_PASSWORD` value configured for Compose
- Database: `school_db`

7. Stop services:

```powershell
docker compose -f docker/docker-compose.yml down
```

8. Remove the database and uploads volumes for a destructive fresh start:

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
│   │   └── seed.py               # Roles, permissions, initial admin, class catalog
│   ├── models/                   # SQLAlchemy ORM models
│   ├── schemas/                  # Pydantic request/response DTOs
│   ├── repositories/             # Data access layer
│   ├── services/                 # Business logic layer
│   ├── utils/                    # ID generation, file storage
│   └── tests/                    # Pytest tests
├── alembic/                      # Database migrations
│   └── versions/
├── docker/                       # Dockerfile, docker-compose.yml
├── docs/
│   ├── api-reference.md                    # Generated from FastAPI OpenAPI
│   ├── database-schema-reference.md         # Generated from configured live schema
│   └── technical-documentation.md           # Current implementation and operations guide
├── logs/                         # Daily log files (gitignored; .gitkeep kept)
├── uploads/                      # Local file uploads (gitignored)
├── scripts/
│   ├── generate_api_reference.py
│   ├── generate_database_reference.py
│   ├── seed_db.py
│   └── cleanup_logs.py
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
| `008_duplicate_key` | `008_inquiry_duplicate_key.py` | Add nullable inquiry identity hash and unique duplicate guard |
| `009_reconcile_orm` | `009_reconcile_orm_schema.py` | Reconcile legacy schema with current ORM and add operational tables/constraints |
| `010_subject_academic_map` | `010_subject_class_academic_mappings.py` | Add designated class teachers, class subject offerings, class-scoped teacher teaching assignments, and subject-management permissions |

#### Migration Safety Notes (Important)

- **Do not delete old Alembic revisions** in `alembic/versions/`. Alembic needs them to resolve the revision graph.
- The database stores the active revision in `alembic_version.version_num` and Alembic must be able to locate that revision file.
- For major schema refactors, prefer a planned **baseline/squash** approach (new base revision + controlled DB rebuild) rather than ad-hoc deletion.

#### Alembic Revision and Schema Mismatch

Alembic uses `alembic_version` to decide which migrations to apply; it does not verify that
all tables from earlier revisions still exist before moving to the next revision. If
`alembic upgrade head` fails because a table is missing, first confirm that the command and
the API target the same database. Inspect the current revision and MySQL schema:

```powershell
alembic current
```

```sql
SELECT DATABASE();
SELECT version_num FROM alembic_version;
SHOW TABLES;
```

If the database is explicitly disposable and `SHOW TABLES` lists only `alembic_version`,
remove that stale marker in the confirmed target database, then rebuild and seed from the
repository root:

```sql
DROP TABLE alembic_version;
```

```powershell
alembic upgrade head
python -m scripts.seed_db
```

This reset is destructive to migration history and is only appropriate when there is no
application data or schema to preserve. Do not drop or stamp the version table on a database
with application tables or data; take a backup and have the schema and migration state
reconciled deliberately instead. MySQL DDL may not roll back when a migration fails, so
inspect the tables again before retrying after a partially applied migration.

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

    classes ||--o{ students : enrolled_students_inherit_offerings
    students ||--o{ student_admissions : legacy

    teachers ||--o{ teacher_subjects : legacy_subject_link
    subjects ||--o{ teacher_subjects : legacy_subject_link
    teachers ||--o{ teacher_classes : assigned
    teachers ||--o| classes : designated_class_teacher
    classes ||--o{ class_subjects : offers
    subjects ||--o{ class_subjects : offered_to
    teachers ||--o{ teacher_class_subjects : teaches
    class_subjects ||--o{ teacher_class_subjects : staffed_by
    teachers ||--o| teacher_salary : has
    teachers ||--o{ teacher_attendance : has
    teachers ||--o{ teacher_salary_payments : receives
```

### 6.3 Table and Column Reference

The [generated database schema reference](database-schema-reference.md) is the detailed
field-level catalog: every table and column, live MySQL type, nullability, default,
auto-generation, primary/foreign keys, unique/index/check constraints, descriptions, and
detected ORM differences. It is a snapshot of the configured database, not a migration
specification. Regenerate it only after confirming the configured database is the intended
target:

```powershell
python scripts\generate_database_reference.py
```

The script inspects schema metadata and the applied Alembic revision; it does not migrate
the database or read application records. The source migrations under `alembic/versions/`
remain the authority for schema history, and the database snapshot is the authority for the
currently configured database.

Migration `010_subject_class_academic_mappings` is additive and preserves existing
`teacher_subjects` rows as legacy global teacher/subject associations. Apply migrations to
the intended database before regenerating the live schema snapshot; until then, its listed
revision and table set intentionally describe the database as it currently exists.

Revision `009_reconcile_orm_schema` adds operational teacher/student tables and constraints
while retaining some legacy columns. Before upgrading a real database, take a backup and
review the migration. It relies on MySQL `CHECK` enforcement (MySQL 8.0.16+); once the
application has written data under the reconciled schema, use a tested backup restore for
rollback rather than assuming a downgrade is safe.

### 6.4 Relationships and Enumerations

The entity relationships are shown in the ER diagram above. Database-enforced keys and
constraints are listed in the [database schema reference](database-schema-reference.md);
API enum values and field validation are in the [API reference](api-reference.md).

---

## 7. API Documentation

The generated [API reference](api-reference.md) is the operation-level catalog for the
current OpenAPI contract: method/path, authentication and permission notes, parameters,
request schema, field-level types and constraints, response status/schema, and illustrative
request/success/error bodies. The running `/openapi.json` and `/docs` remain authoritative.
Refresh the checked-in Markdown snapshot after route or schema changes with:

```powershell
python scripts\generate_api_reference.py
```

The API uses a shared JSON envelope. Success responses contain `success`, `message`,
`data`, and request metadata; paginated responses also include `pagination`. Error responses
contain `success: false`, `message`, `data: null`, `errors[]`, and request metadata. The
reference contains representative examples; exact error statuses still depend on each
route's rules and runtime handlers.

Clients send `Authorization: Bearer <access-token>` to protected routes. Public inquiry
status lookup and update use the applicant's inquiry code, email, and parent mobile for
verification; see the operation-specific header/body details in the API reference.

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
  "email": "admin@example.com",
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
- Teacher salary reads and payments have separate permissions; salary access is
  limited to finance and administrative roles.

Seed data: `app/core/permissions.py`

### 8.4 Initial Admin

The seed operation creates or updates the initial SUPER_ADMIN only when both
`INITIAL_ADMIN_EMAIL` and `INITIAL_ADMIN_PASSWORD` are configured. Seeding is manual unless
`SEED_ON_STARTUP=true`; configuring the values alone does not create an account. There are
no built-in default credentials.

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

### 9.5 Current implementation rules verified from source

- Duplicate identity is based on first name, last name, father/guardian name, and date of
  birth. The three names have whitespace collapsed and are case-folded; DOB is serialized as
  ISO date. The canonical identity JSON is SHA-256 hashed into `duplicate_key`. Email,
  phone, middle name, and gender are not part of duplicate identity.
- The nullable unique index on `duplicate_key` is the concurrency guard for active keyed
  inquiries. The repository also checks legacy rows without relying on a key. If a database
  integrity error occurs during submission, the service checks whether a duplicate explains
  the conflict and returns the duplicate conflict when it does; unrelated integrity errors
  are not silently converted.
- `REJECTED` and `INTERVIEW_FAIL` inquiries release the identity key and allow a new
  application. Those original inquiry records remain locked; reapplication creates a new
  inquiry. An identical first/last/guardian/DOB combination—including twins with identical
  names and DOB—cannot be distinguished by the current identity fields and may be treated
  as a duplicate; this requires a separate identity policy if it must be supported.
- An admission can be opened only after `INTERVIEW_PASS`. Creating it sets the admission
  to `submitted` and moves the inquiry to `DOCUMENT_PENDING`.
- The six required document types are `progress_report`, `transfer_certificate`,
  `migration_certificate`, `character_certificate`, `student_aadhar`, and `parent_aadhar`.
  All six must be uploaded and verified before the admission can be approved. Replacing a
  document resets its verification and may return the workflow to document pending.
- Enrollment requires an approved admission, all six documents verified, an active target
  class that is academically ready, and available class capacity. Enrollment creates the
  student and class/year roll number, links the student to the admission, and moves the
  inquiry to `ADMISSION_SUCCESS`.
- `INTERVIEW_FAIL`, `REJECTED`, and `ADMISSION_SUCCESS` are locked states for edits to the
  original inquiry. Reapplication, when allowed by the duplicate-key rule above, is a new
  inquiry rather than an edit to that locked record.

The duplicate behavior is covered by unit tests for exact and case-insensitive matches,
different names/DOB, reapplication after rejection/interview failure, and the service
conflict path. A duplicate submission returns HTTP 409 with the standard error envelope;
see the shared runtime error examples in the API reference.

### 9.6 Class, subject, teacher, and student academic mapping

Class setup remains intentionally incremental: creating an active class does not require
its class teacher or subject catalog to exist yet. `GET /api/v1/classes/{class_id}/readiness`
reports whether the class is ready: it must be active, have one active designated class
teacher, and have at least one active subject offering. Setting an inactive class active is
rejected until those requirements are met. Student class assignment and admission enrollment
are also blocked while the selected class is not ready.

The designated class teacher is stored on `classes.class_teacher_id`, separate from the
teacher-to-class and teacher-to-subject teaching assignments. A teacher may be the designated
class teacher for at most one non-deleted class. The teacher can still teach multiple
class/subject combinations through `teacher_class_subjects`.
`GET /api/v1/teachers/{teacher_id}/academic-readiness` reports whether an active teacher has
at least one active class/subject teaching assignment; teacher creation remains available
during setup so administrators can complete mappings afterward.

`class_subjects` records curriculum offerings. A teacher's class-scoped assignment is accepted
only when the class already offers that active subject; the composite foreign key and primary
key prevent assignments to a non-offered subject and duplicate teacher/class/subject rows.
The existing `teacher_subjects` table and `POST /api/v1/teachers/{teacher_id}/subject` endpoint
remain for compatibility with older global teacher/subject links. They do not replace the
new class-scoped teaching assignment and should not be used to determine a class timetable.

Students inherit the active subjects offered to their enrolled class through `class_id`;
`GET /api/v1/students/{student_id}/subjects` returns those offerings. The current project has
no elective-selection workflow, so student-specific subject choices are not stored separately.
Removing a class offering is blocked while active students are enrolled, and a subject cannot
be deactivated while it is offered to an active class. Readiness is computed from current
relationships rather than stored as a boolean, avoiding stale readiness flags.

Setup sequence:

1. Create subjects with `POST /api/v1/subjects`.
2. Create the class; incomplete initial setup is allowed.
3. Assign its designated teacher with `POST /api/v1/classes/{class_id}/class-teacher`.
4. Offer subjects with `POST /api/v1/classes/{class_id}/subjects`.
5. Assign teaching responsibility with `POST /api/v1/teachers/{teacher_id}/class-subjects`.
6. Confirm class readiness before enrolling or assigning active students.

Creating subjects requires `subjects.create`; listing and retrieving them requires
`subjects.read`. Code/name updates and reactivation require `subjects.update`, while soft
deactivation requires `subjects.delete`. Class curriculum and class-teacher assignments use
`classes.update`; teacher teaching assignments use `teachers.update`. Migration 010 grants
the new subject permissions to existing `ADMIN` and `SUPER_ADMIN` roles; the normal seed
routine also includes them for fresh installations.

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

All errors are returned in the shared envelope described in Section 7 and illustrated in
the API reference:

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

| Concern | Implementation |
|---------|----------------|
| Request correlation | `RequestIDMiddleware` sets/echoes `X-Request-ID` |
| Retention | `LOG_RETENTION_DAYS`; startup cleanup and `python scripts/cleanup_logs.py` |
| Audit trail | `audit_logs` table via `AuditService` |
| Liveness | `GET /live` does not require the database |
| Readiness | `GET /ready` and `GET /health` execute `SELECT 1`; HTTP 503 when unavailable |

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

Compose mounts the named volume `school_uploads` at `/app/uploads`; replacing the API container
preserves uploaded files. The destructive `docker compose down -v` command removes this volume.

**Security:** Store outside web root in production; scan files; use S3 with pre-signed URLs for scale.
Apply a reverse-proxy or WAF request-body limit slightly above the configured upload size to
allow multipart overhead and reject oversized requests before parsing.

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
ruff check app
```

CI runs Ruff, applies Alembic migrations to its MySQL 8.4 service, and runs pytest. The test
suite uses in-memory SQLite fixtures for isolation and includes coverage for:

- Auth tokens and RBAC/access controls.
- Public inquiry validation, duplicate identity, status history and transitions.
- Interview scheduling and pass/fail/absent outcomes.
- Admission submission, required documents, and workflow restrictions.
- File upload size/extension handling, security helpers and structured logging.
- Salary amount calculations, enum validation, schema/database constraints, and health probes.

The test suite is not a substitute for deployment-specific checks against the configured
MySQL version and storage environment. Use CI as the current test result authority; old
test counts and production-readiness ratings in the removed historical review are not
current project measurements.

---

## 15. Deployment Documentation

### 15.1 Local

```powershell
pip install -e .
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 15.2 Docker Compose and Release Migrations

```powershell
docker compose -f docker/docker-compose.yml up -d db
docker compose -f docker/docker-compose.yml --profile release run --rm migrate
docker compose -f docker/docker-compose.yml up -d api
```

The API image starts Uvicorn directly and does not run Alembic on startup. Run the one-shot
`migrate` service once as part of each release, after the database is healthy and before deploying
or scaling API replicas. Do not launch migrations independently from API replicas.

Compose provides these services:

- `db` → Dockerized MySQL
- `migrate` → one-shot Alembic task, enabled with the `release` profile
- `api` → FastAPI application

When using Compose:

- The API connects to MySQL at `mysql+pymysql://root:mysql@db:3306/school_db`
- The host maps MySQL container port `3306` to host port `3307`
- The API is available on host port `8000`
- Compose builds the internal database URL from `MYSQL_ROOT_PASSWORD`; URL-encode reserved
  characters in the password before using it in the URL.
- The `school_uploads` named volume persists files mounted at `/app/uploads`
- The API healthcheck uses `/ready` and remains unhealthy while the database is unavailable

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

The `down -v` command also deletes uploaded documents from `school_uploads`; use it only when
deleting both database and file data is intentional.

### 15.3 Health Probes and Public Endpoint Protection

| Endpoint | Probe purpose | Database required | Failure behavior |
|----------|---------------|-------------------|------------------|
| `GET /live` | Process liveness | No | 200 while the API responds |
| `GET /ready` | Readiness for traffic | Yes (`SELECT 1`) | 503 with standard error envelope |
| `GET /health` | Backward-compatible readiness alias | Yes (`SELECT 1`) | 503 with standard error envelope |

Rate-limit public inquiry/admission traffic at a shared ingress or WAF so the policy covers all
API replicas. Apply per-client limits to public submission routes, set a request-body cap slightly
above `MAX_UPLOAD_SIZE_MB` for multipart overhead, and trust forwarded client-IP headers only from
known proxy or load-balancer addresses. Tune thresholds against expected production traffic.

### 15.4 Production (Recommended)

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

### 15.5 CI

`.github/workflows/ci.yml` runs Ruff, migrations, and pytest against MySQL 8.4. The CI
workflow is the canonical automated test and migration check.

#### Migration and schema change notes

Revision `009_reconcile_orm_schema` aligned operational tables and constraints with the
registered models, retained selected legacy columns, and backfilled required identity fields
from linked accounts. It added teacher/class assignments, attendance, and salary tables;
the API and database both enforce salary payment arithmetic
`net_amount = gross_amount - deduction_amount` and the applicable nonnegative amount bounds.
The migration is forward-only after writes rely on the reconciled schema; back up first and
use a tested restore for rollback.

Collection queries use `selectinload` for inquiry history/interviews, admission documents,
and student classes to avoid per-record relationship queries.

#### Reverse-proxy protection for public routes

Public route rate limiting belongs at a shared ingress/WAF so it applies across API replicas.
Set the body-size cap slightly above `MAX_UPLOAD_SIZE_MB` to account for multipart overhead,
and trust forwarded client IP headers only from known proxies. Example Nginx starting point:

```nginx
limit_req_zone $binary_remote_addr zone=school_public_forms:10m rate=10r/m;

location ~ ^/api/v1/public/student/(inquiry(?:/.*)?|admission)$ {
    client_max_body_size 6m;
    limit_req zone=school_public_forms burst=10 nodelay;
    limit_req_status 429;
    proxy_pass http://school_api;
}
```

Tune thresholds for expected traffic and configure trusted real-IP sources before relying on
forwarded addresses.

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

**Recommended additions:** HTTPS-only ingress, JWT secret rotation, and a WAF. Public-form
rate limiting is configured at ingress; password recovery is not implemented.

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

- **Not implemented:** Career/HR hiring, academic sessions/sections, student attendance,
  results/report cards, fees, notifications, and parent/student portals.
- **Operational improvements under consideration:** Redis caching, a background job system,
  object storage, password recovery, API rate limiting inside the application, and social
  login. Public endpoint rate limiting is currently an ingress responsibility.
- **Unapproved proposal ideas:** Multi-school tenancy, report exports, calendar/timetable,
  bus tracking, library, and online exams. These originated in design material and are not
  committed product requirements.

---

## 20. Documentation Maintenance

The root [README](../README.md) is the concise project overview and quick-start guide.
This technical guide is the authoritative architecture, workflow, operations, and
maintenance document. The [API reference](api-reference.md) and
[database schema reference](database-schema-reference.md) are separate generated snapshots
because they use different sources and change on different schedules.

### Reference generator behavior

| Generator | Input and output | What is automated | What remains manually curated |
|-----------|------------------|-------------------|-------------------------------|
| `scripts/generate_api_reference.py` | Imports the FastAPI app and writes `docs/api-reference.md`. | Reads OpenAPI paths, parameters, request schemas, field constraints, security declarations; inspects route handlers for declared permissions; builds illustrative request/success/error examples. | Response-model mappings, custom response payload mappings, sample values, and some success-model examples are explicit script metadata. Review these mappings when handler output changes. |
| `scripts/generate_database_reference.py` | Connects to `DATABASE_URL` and writes `docs/database-schema-reference.md`. | Introspects the configured live database for tables, columns, types, nullability, defaults, primary/foreign keys, unique constraints, indexes, checks, current Alembic revision, and differences from registered ORM models. | Table/field descriptions and selected API-rule notes are maintained in the generator. The script does not infer undocumented business meaning or migration intent. |

The generated Markdown files are checked into version control so reviewers and users can
read the references without running the generators. Keep the scripts: they reduce drift and
provide repeatable reference output, but they do not remove the need to review hand-curated
metadata or confirm the target database.

After route/schema changes, regenerate the API reference from the repository root:

```powershell
python scripts\generate_api_reference.py
```

After database migrations, confirm `.env` points to the intended database, then regenerate
the live database snapshot:

```powershell
python scripts\generate_database_reference.py
```

The database generator performs schema inspection and reads the current Alembic revision;
it does not migrate the database or read application records. Never run it against a
production or customer database unless that target is explicitly intended for the
documentation snapshot. Review generated diffs, verify examples/constraints, and commit
the updated Markdown together with relevant source changes.

For disagreements, use the runtime `/openapi.json` and source for API behavior, migration
files for schema history, and database inspection for the live target schema. Generated
examples are illustrative and are not captured business transactions.

---

## 21. Diagrams & Visual Documentation

### 21.1 Request Lifecycle

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

### 21.2 Module Dependencies

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

- [README](../README.md) — Project overview and quick start
- [API reference](api-reference.md) — Generated operation/schema catalog and examples
- [Database schema reference](database-schema-reference.md) — Configured live schema snapshot
- `scripts/generate_api_reference.py` and `scripts/generate_database_reference.py` —
  Reference documentation generators; see Section 20
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

## 23. Verification Checklist

Use this checklist for a deployment or release review. Environment-dependent checks must
be repeated against the target environment; generated references are snapshots, not live
monitoring.

| Check | Status | What to verify |
|---|---|---|
| Documentation source of truth | Documented | Use source/OpenAPI/migrations for current behavior; proposal-era details are labeled as unapproved ideas or superseded history. |
| API contract | Generated | Review all operations, fields, constraints, route permissions, and illustrative examples in [the API reference](api-reference.md); compare with the running `/openapi.json` after API changes. |
| Database schema | Snapshot generated | Compare [the database reference](database-schema-reference.md) with the target database after migrations; resolve model/database differences before relying on ORM fields. |
| Configuration and secrets | Environment-specific | Set required environment variables securely; use strong production secrets and never copy example credentials into deployment settings. |
| Migrations and seeding | Environment-specific | Apply Alembic migrations as a release step. Run seeding only when intended; configure both initial-admin values to create the bootstrap administrator. |
| Inquiry-to-enrollment flow | Source reviewed | Test duplicate inquiry handling, interview outcomes, all six document uploads and verifications, approval, active-class capacity, and resulting student/roll assignment. |
| File upload controls | Documented limitation | Confirm configured extension/size limits and private storage behavior; malware scanning and MIME-signature verification are not implemented by the application. |
| Authentication and authorization | Source documented | Verify login/token lifecycle and expected role/permission access using deployment-specific accounts. |
| Tests and deployment smoke checks | Run per release | Execute CI tests, then verify health/readiness, database connectivity, API docs, and representative protected/public routes in the target environment. |

---

*End of Technical Documentation*
