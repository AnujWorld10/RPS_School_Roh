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

## Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12+ |
| Framework | FastAPI |
| Server | Uvicorn |
| Database | MySQL 8+ |
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
cd D:\SCHOOL_MANAGEMENT
copy .env.example .env
```

Edit `.env` — default local connection:

```env
DATABASE_URL=mysql+pymysql://root:mysql@localhost:3306/school_db
JWT_SECRET_KEY=your-long-random-secret-key-here
```


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
> 
> ```
> 
> 
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

**Important:** Run from the **project root** using `app.main:app`, not `uvicorn main:app` from inside the `app/` folder.

---

## Default Login

On first startup, a super admin user is seeded automatically:

| Field | Value |
|-------|-------|
| Email | `superadmin@school.com` |
| Password | `SuperAdmin@123` |

If you seeded earlier with `superadmin@school.local`, that address still works for login, or update the row in MySQL:

```sql
UPDATE users SET email = 'superadmin@school.com' WHERE email = 'superadmin@school.local';
```

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "superadmin@school.com",
  "password": "SuperAdmin@123"
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
app/
  api/           # Routes and dependencies
  core/          # Config, security, logging, middleware
  db/            # Session, seed, base
  models/        # SQLAlchemy ORM
  schemas/       # Pydantic DTOs
  repositories/  # Data access
  services/      # Business logic
  utils/         # IDs, file storage
  tests/         # Pytest
alembic/         # Migrations
docker/          # Docker Compose
docs/            # Technical documentation
```

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
