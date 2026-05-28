# School Management System Backend Blueprint

## 1. Project Overview

Build a production-grade School Management System backend using Python, FastAPI, MySQL, SQLAlchemy or SQLModel, Alembic, JWT authentication, and role-based access control.

The backend must support authentication, classes, inquiries, students, admissions, teachers, subject/class assignments, attendance, salary management, audit history, logging, validation, transactions, and deployment-ready operational standards.

Primary architectural flow:

```text
Route -> Schema Validation -> Service -> Repository -> Database -> Response
```

Core goals:

- Clean modular architecture.
- Consistent naming across routes, services, repositories, models, schemas, and tables.
- Strong database constraints and relationships.
- JWT access and refresh token flow.
- Role and permission-based authorization.
- Standardized responses, errors, logging, auditing, and exception handling.
- Soft delete where business data should be retained.
- Pagination, filtering, and sorting for list APIs.

All APIs use this prefix:

```text
/api/v1
```

## 2. Recommended Development Order

1. Initialize project structure, dependency management, linting, formatting, and test setup.
2. Configure environment settings, database connection, SQLAlchemy or SQLModel base, Alembic, and health check.
3. Implement shared utilities: response wrapper, exceptions, logging, pagination, request ID middleware, transaction helpers.
4. Create core RBAC tables: users, roles, permissions, user_roles.
5. Implement authentication: password hashing, login, JWT access token, refresh token, logout, current user.
6. Implement authorization dependencies: authenticated user, role checks, permission checks.
7. Build class module.
8. Build inquiry module with approval and rejection workflow.
9. Build student module with lifecycle, class assignment, status changes, and soft delete.
10. Build student admission module with approval and rejection workflow.
11. Build teacher module with profile, subject assignment, class assignment, attendance, salary, and salary payments.
12. Add audit logging and history tracking across state-changing APIs.
13. Add monitoring, structured logs, error reporting hooks, and production middleware.
14. Add integration tests, migration tests, authorization tests, and workflow tests.
15. Prepare deployment configuration, CI/CD, database migration process, and release checklist.

## 3. Technology Stack

| Area | Recommended Tool |
|---|---|
| Language | Python 3.12+ |
| API Framework | FastAPI |
| ASGI Server | Uvicorn or Gunicorn with Uvicorn workers |
| Database | MySQL 8+ |
| ORM | SQLAlchemy 2.x or SQLModel |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT access tokens and refresh tokens |
| Password Hashing | Argon2 or bcrypt through Passlib |
| Logging | Python logging with JSON formatter |
| Testing | Pytest, HTTPX, factory_boy |
| Static Analysis | Ruff, mypy |
| Deployment | Docker, Docker Compose, CI/CD |

## 4. Folder Structure

```text
app/
  main.py
  api/
    deps.py
    v1/
      router.py
      auth/routes.py
      classes/routes.py
      inquiries/routes.py
      students/routes.py
      admissions/routes.py
      teachers/routes.py
  core/
    config.py
    security.py
    permissions.py
    logging.py
    exceptions.py
    responses.py
    pagination.py
    middleware.py
    transactions.py
  db/
    base.py
    session.py
    migrations/
  models/
    user.py
    role.py
    permission.py
    class_model.py
    student.py
    admission.py
    inquiry.py
    teacher.py
    subject.py
    audit_log.py
    refresh_token.py
  schemas/
    auth.py
    common.py
    classes.py
    inquiries.py
    students.py
    admissions.py
    teachers.py
  repositories/
    base.py
    users.py
    classes.py
    inquiries.py
    students.py
    admissions.py
    teachers.py
  services/
    auth.py
    classes.py
    inquiries.py
    students.py
    admissions.py
    teachers.py
    audit.py
  tests/
    integration/
    unit/
alembic/
  versions/
docker/
  Dockerfile
  docker-compose.yml
alembic.ini
pyproject.toml
.env.example
```

## 5. Environment Configuration

Required settings:

```env
APP_NAME=school-management-api
APP_ENV=development
DEBUG=false
API_V1_PREFIX=/api/v1
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/school_db
JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
PASSWORD_HASH_SCHEME=argon2
LOG_LEVEL=INFO
```

Rules:

- Never commit real secrets.
- Validate settings at startup using Pydantic settings.
- Use separate values for local, test, staging, and production.
- Fail fast if required config is missing.

## 6. Database Design

Common audit columns where applicable:

```text
id BIGINT PRIMARY KEY AUTO_INCREMENT
created_at DATETIME NOT NULL
updated_at DATETIME NULL
created_by BIGINT NULL
updated_by BIGINT NULL
deleted_at DATETIME NULL
deleted_by BIGINT NULL
is_active BOOLEAN NOT NULL DEFAULT TRUE
status VARCHAR(50) NOT NULL
```

### users

| Column | Type | Constraint |
|---|---|---|
| id | BIGINT | PK |
| first_name | VARCHAR(100) | NOT NULL |
| last_name | VARCHAR(100) | NOT NULL |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| phone | VARCHAR(30) | UNIQUE, NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| status | VARCHAR(50) | active, inactive, locked |
| last_login_at | DATETIME | NULL |
| created_at | DATETIME | NOT NULL |
| updated_at | DATETIME | NULL |
| deleted_at | DATETIME | NULL |

Indexes:

- Unique index on `email`.
- Unique index on `phone`.
- Index on `status`.

### roles

| Column | Type | Constraint |
|---|---|---|
| id | BIGINT | PK |
| code | VARCHAR(50) | UNIQUE, NOT NULL |
| name | VARCHAR(100) | NOT NULL |
| description | VARCHAR(255) | NULL |
| is_active | BOOLEAN | DEFAULT TRUE |

Default roles:

- `SUPER_ADMIN`
- `ADMIN`
- `PRINCIPAL`
- `TEACHER`
- `ACCOUNTANT`
- `ADMISSION_OFFICER`
- `STUDENT`
- `PARENT`

### permissions

| Column | Type | Constraint |
|---|---|---|
| id | BIGINT | PK |
| code | VARCHAR(100) | UNIQUE, NOT NULL |
| module | VARCHAR(100) | NOT NULL |
| action | VARCHAR(50) | NOT NULL |

Example permission codes:

- `students.create`
- `students.read`
- `students.update`
- `students.delete`
- `admissions.approve`
- `teachers.salary.pay`

### user_roles

| Column | Type | Constraint |
|---|---|---|
| user_id | BIGINT | FK users.id |
| role_id | BIGINT | FK roles.id |

Constraints:

- Composite primary key on `user_id`, `role_id`.

### classes

| Column | Type | Constraint |
|---|---|---|
| id | BIGINT | PK |
| name | VARCHAR(100) | NOT NULL |
| section | VARCHAR(20) | NULL |
| academic_year | VARCHAR(20) | NOT NULL |
| capacity | INT | NOT NULL |
| status | VARCHAR(50) | active, inactive |
| created_at | DATETIME | NOT NULL |
| updated_at | DATETIME | NULL |
| deleted_at | DATETIME | NULL |

Constraints:

- Unique `name`, `section`, `academic_year`.
- Index on `academic_year`.

### students

| Column | Type | Constraint |
|---|---|---|
| id | BIGINT | PK |
| admission_no | VARCHAR(50) | UNIQUE |
| first_name | VARCHAR(100) | NOT NULL |
| last_name | VARCHAR(100) | NOT NULL |
| date_of_birth | DATE | NOT NULL |
| gender | VARCHAR(20) | NOT NULL |
| email | VARCHAR(255) | NULL |
| phone | VARCHAR(30) | NULL |
| current_class_id | BIGINT | FK classes.id, NULL |
| status | VARCHAR(50) | prospective, active, inactive, graduated, transferred |
| created_at | DATETIME | NOT NULL |
| updated_at | DATETIME | NULL |
| deleted_at | DATETIME | NULL |

Indexes:

- Unique `admission_no`.
- Index on `current_class_id`.
- Index on `status`.

### student_admissions

| Column | Type | Constraint |
|---|---|---|
| id | BIGINT | PK |
| student_id | BIGINT | FK students.id |
| class_id | BIGINT | FK classes.id |
| academic_year | VARCHAR(20) | NOT NULL |
| status | VARCHAR(50) | draft, submitted, approved, rejected |
| rejection_reason | TEXT | NULL |
| approved_by | BIGINT | FK users.id, NULL |
| approved_at | DATETIME | NULL |
| created_at | DATETIME | NOT NULL |

Constraints:

- Unique active admission per student per academic year.

### inquiries

| Column | Type | Constraint |
|---|---|---|
| id | BIGINT | PK |
| student_name | VARCHAR(200) | NOT NULL |
| parent_name | VARCHAR(200) | NOT NULL |
| phone | VARCHAR(30) | NOT NULL |
| email | VARCHAR(255) | NULL |
| interested_class_id | BIGINT | FK classes.id |
| message | TEXT | NULL |
| status | VARCHAR(50) | new, contacted, approved, rejected |
| rejection_reason | TEXT | NULL |
| created_at | DATETIME | NOT NULL |

Indexes:

- Index on `status`.
- Index on `phone`.

### teachers

| Column | Type | Constraint |
|---|---|---|
| id | BIGINT | PK |
| user_id | BIGINT | FK users.id, UNIQUE, NULL |
| employee_no | VARCHAR(50) | UNIQUE, NOT NULL |
| first_name | VARCHAR(100) | NOT NULL |
| last_name | VARCHAR(100) | NOT NULL |
| email | VARCHAR(255) | UNIQUE |
| phone | VARCHAR(30) | UNIQUE |
| joining_date | DATE | NOT NULL |
| status | VARCHAR(50) | active, inactive, resigned |

### subjects

| Column | Type | Constraint |
|---|---|---|
| id | BIGINT | PK |
| code | VARCHAR(50) | UNIQUE, NOT NULL |
| name | VARCHAR(100) | NOT NULL |
| is_active | BOOLEAN | DEFAULT TRUE |

### teacher_subjects

| Column | Type | Constraint |
|---|---|---|
| teacher_id | BIGINT | FK teachers.id |
| subject_id | BIGINT | FK subjects.id |

Constraint:

- Composite unique `teacher_id`, `subject_id`.

### teacher_classes

| Column | Type | Constraint |
|---|---|---|
| teacher_id | BIGINT | FK teachers.id |
| class_id | BIGINT | FK classes.id |

Constraint:

- Composite unique `teacher_id`, `class_id`.

### teacher_attendance

| Column | Type | Constraint |
|---|---|---|
| id | BIGINT | PK |
| teacher_id | BIGINT | FK teachers.id |
| attendance_date | DATE | NOT NULL |
| status | VARCHAR(50) | present, absent, leave, half_day |
| remarks | VARCHAR(255) | NULL |

Constraint:

- Unique `teacher_id`, `attendance_date`.

### teacher_salary

| Column | Type | Constraint |
|---|---|---|
| id | BIGINT | PK |
| teacher_id | BIGINT | FK teachers.id, UNIQUE |
| base_salary | DECIMAL(12,2) | NOT NULL |
| allowance | DECIMAL(12,2) | DEFAULT 0 |
| deduction | DECIMAL(12,2) | DEFAULT 0 |
| effective_from | DATE | NOT NULL |
| status | VARCHAR(50) | active, inactive |

### teacher_salary_payments

| Column | Type | Constraint |
|---|---|---|
| id | BIGINT | PK |
| teacher_id | BIGINT | FK teachers.id |
| salary_id | BIGINT | FK teacher_salary.id |
| payment_month | VARCHAR(7) | YYYY-MM |
| gross_amount | DECIMAL(12,2) | NOT NULL |
| deduction_amount | DECIMAL(12,2) | DEFAULT 0 |
| net_amount | DECIMAL(12,2) | NOT NULL |
| status | VARCHAR(50) | pending, paid, failed |
| paid_at | DATETIME | NULL |

Constraint:

- Unique `teacher_id`, `payment_month`.

### refresh_tokens

| Column | Type | Constraint |
|---|---|---|
| id | BIGINT | PK |
| user_id | BIGINT | FK users.id |
| token_hash | VARCHAR(255) | UNIQUE |
| expires_at | DATETIME | NOT NULL |
| revoked_at | DATETIME | NULL |
| created_at | DATETIME | NOT NULL |

### audit_logs

| Column | Type | Constraint |
|---|---|---|
| id | BIGINT | PK |
| actor_user_id | BIGINT | FK users.id, NULL |
| action | VARCHAR(100) | NOT NULL |
| entity_type | VARCHAR(100) | NOT NULL |
| entity_id | BIGINT | NULL |
| old_values | JSON | NULL |
| new_values | JSON | NULL |
| request_id | VARCHAR(100) | NOT NULL |
| ip_address | VARCHAR(100) | NULL |
| user_agent | VARCHAR(255) | NULL |
| created_at | DATETIME | NOT NULL |

## 7. Entity Relationships

- A user can have many roles through `user_roles`.
- A role can map to many permissions through a recommended `role_permissions` table, even if not listed in the minimum table list.
- A class can have many students.
- A student can have one current class and many historical admissions.
- An inquiry can be approved into a student creation workflow.
- A teacher can be linked to one user account.
- A teacher can teach many subjects and many classes.
- A teacher can have many attendance records.
- A teacher can have one active salary setup and many salary payments.

## 8. Authentication & Authorization

Authentication flow:

1. User submits email and password.
2. Service validates user status and password hash.
3. API returns short-lived access token and long-lived refresh token.
4. Refresh token is stored as a hash in `refresh_tokens`.
5. Logout revokes the active refresh token.
6. Protected routes require a valid access token.

Access token claims:

```json
{
  "sub": "123",
  "email": "admin@example.com",
  "roles": ["ADMIN"],
  "permissions": ["students.create"],
  "type": "access",
  "exp": 1770000000
}
```

Refresh token claims:

```json
{
  "sub": "123",
  "type": "refresh",
  "jti": "uuid",
  "exp": 1770000000
}
```

## 9. Role-Based Access Control

Use dependencies:

```text
get_current_user()
require_roles("ADMIN", "SUPER_ADMIN")
require_permissions("students.create")
```

Recommended permission model:

- Roles are broad business identities.
- Permissions are exact capabilities.
- Routes should prefer permission checks for sensitive actions and role checks for coarse access.

## 10. API Response Standard

Success:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {},
  "errors": null,
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-05-24T10:00:00Z"
  }
}
```

Paginated:

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
  "errors": null
}
```

Error:

```json
{
  "success": false,
  "message": "Validation failed",
  "data": null,
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "field": "email",
      "message": "Invalid email address"
    }
  ],
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-05-24T10:00:00Z"
  }
}
```

## 11. Error and Warning Message Standard

Use stable error codes:

| Code | Meaning |
|---|---|
| VALIDATION_ERROR | Request validation failed |
| AUTH_INVALID_CREDENTIALS | Email or password is invalid |
| AUTH_TOKEN_EXPIRED | Token has expired |
| AUTH_TOKEN_INVALID | Token is invalid |
| AUTH_FORBIDDEN | User lacks required access |
| RESOURCE_NOT_FOUND | Resource does not exist |
| RESOURCE_CONFLICT | Unique or business constraint conflict |
| BUSINESS_RULE_VIOLATION | Workflow rule failed |
| INTERNAL_SERVER_ERROR | Unexpected server error |

Warnings should be returned only when the operation succeeds but requires attention:

```json
{
  "code": "CAPACITY_WARNING",
  "message": "Class is close to maximum capacity"
}
```

## 12. Exception Handling Strategy

Create custom exceptions:

- `AppException`
- `ValidationException`
- `AuthenticationException`
- `AuthorizationException`
- `NotFoundException`
- `ConflictException`
- `BusinessRuleException`

Register global handlers for:

- FastAPI validation errors.
- SQLAlchemy integrity errors.
- Custom application exceptions.
- Unhandled exceptions.

Never expose database traces or stack traces in API responses.

## 13. Input Validation Rules

General:

- Trim strings.
- Validate email format.
- Validate phone format.
- Use enums for status fields.
- Validate IDs are positive integers.
- Validate dates are logical and not impossible.
- Validate pagination limits.

Recommended pagination defaults:

```text
page=1
limit=10
max_limit=100
sort_by=created_at
sort_order=desc
```

## 14. Transaction Handling

Rules:

- One request should generally use one database session.
- State-changing service methods own transaction boundaries.
- Repository methods should not commit directly.
- Roll back on exceptions.
- Use row locks for approval flows where double approval could occur.
- Write audit logs in the same transaction as the business change when possible.

## 15. Logging and Monitoring

Log as structured JSON:

- request_id
- method
- path
- status_code
- user_id
- duration_ms
- client_ip
- error_code

Do not log passwords, raw tokens, or sensitive personal data.

Monitoring:

- Health endpoint.
- Database connectivity check.
- Error rate.
- Latency percentiles.
- Authentication failures.
- Failed approval flows.

## 16. Audit / History Tracking

Audit these actions:

- User login and logout.
- Password change.
- Class create, update, delete.
- Inquiry approve and reject.
- Student create, update, status change, class assignment, soft delete.
- Admission create, update, approve, reject.
- Teacher create, update, subject assignment, class assignment.
- Teacher attendance and salary payment.

Each audit record must include actor, action, entity, previous values, new values, request ID, IP, user agent, and timestamp.

## 17. Security Best Practices

- Hash passwords using Argon2 or bcrypt.
- Store only hashed refresh tokens.
- Use short access token expiry.
- Revoke refresh tokens on logout and password change.
- Validate token type.
- Enforce HTTPS in production.
- Use CORS allowlists.
- Add rate limiting for login and refresh token endpoints.
- Use secure, httpOnly cookies if browser clients are used.
- Avoid returning whether an email exists during login.
- Apply least-privilege database user permissions.
- Sanitize logs.

## 18. Real-World Workflows and Edge Cases

Inquiry approval:

1. Inquiry is submitted with parent and student details.
2. Staff reviews and updates status to contacted if needed.
3. Staff approves inquiry.
4. System can create a prospective student or link to admission creation.
5. Audit log is written.

Student admission:

1. Student exists or is created from inquiry.
2. Admission is submitted for class and academic year.
3. Approver checks capacity, duplicates, documents, and student status.
4. Approval sets admission status to approved.
5. Student status becomes active.
6. Student current class is assigned.

Edge cases:

- Duplicate phone or email.
- Class capacity exceeded.
- Approval attempted twice.
- Rejection without reason.
- Deleted student cannot be admitted.
- Inactive teacher cannot receive new salary payments.
- Attendance cannot be recorded twice for same date.
- Salary cannot be paid twice for same month.

## 19. Module-wise Architecture

Each module follows the same structure:

```text
routes.py      HTTP concerns, dependencies, response status codes
schemas.py     Pydantic request and response DTOs
service.py     Business rules, transactions, audit calls
repository.py  Database reads and writes
model.py       ORM table mapping
```

Module boundaries:

- Auth owns users, tokens, password flows.
- Classes owns class CRUD and capacity rules.
- Inquiries owns inquiry lifecycle.
- Students owns student profile, status, class assignment, soft delete.
- Admissions owns admission lifecycle.
- Teachers owns teacher profile, assignment, attendance, salary workflows.

## 20. API Endpoint Documentation

The following endpoints must all return the standard response envelope.

## 21. Request and Response Body for Every Endpoint

### Register User

**Method:** POST  
**URL:** `/api/v1/auth/register`  
**Description:** Register a new user account.  
**Allowed Roles:** SUPER_ADMIN, ADMIN  
**Authentication Required:** Yes

**Request Params:** None  
**Query Params:** None  
**Request Body:**

```json
{
  "first_name": "John",
  "last_name": "Admin",
  "email": "john.admin@example.com",
  "phone": "+911234567890",
  "password": "StrongPassword@123",
  "role_codes": ["ADMIN"]
}
```

**Success Response:**

```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": 1,
    "email": "john.admin@example.com",
    "roles": ["ADMIN"],
    "status": "active"
  },
  "errors": null
}
```

**Error Response:**

```json
{
  "success": false,
  "message": "User already exists",
  "data": null,
  "errors": [{"code": "RESOURCE_CONFLICT", "field": "email", "message": "Email already exists"}]
}
```

**Validation Rules:**

- Email must be unique and valid.
- Password must meet complexity rules.
- Role codes must exist and be active.

**Database Tables Used:**

- users
- roles
- user_roles
- audit_logs

**Business Logic:**

- Validate uniqueness.
- Hash password.
- Create user and role mappings.
- Write audit log.

**Edge Cases:**

- Duplicate email or phone.
- Invalid role code.
- Weak password.

### Login User

**Method:** POST  
**URL:** `/api/v1/auth/login`  
**Description:** Authenticate user and issue access and refresh tokens.  
**Allowed Roles:** All active users  
**Authentication Required:** No

**Request Params:** None  
**Query Params:** None  
**Request Body:**

```json
{
  "email": "john.admin@example.com",
  "password": "StrongPassword@123"
}
```

**Success Response:**

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "jwt-access-token",
    "refresh_token": "jwt-refresh-token",
    "token_type": "bearer",
    "expires_in": 900
  },
  "errors": null
}
```

**Error Response:**

```json
{
  "success": false,
  "message": "Invalid credentials",
  "data": null,
  "errors": [{"code": "AUTH_INVALID_CREDENTIALS", "message": "Invalid email or password"}]
}
```

**Validation Rules:**

- Email is required.
- Password is required.

**Database Tables Used:**

- users
- roles
- permissions
- refresh_tokens
- audit_logs

**Business Logic:**

- Validate user credentials.
- Reject inactive or locked users.
- Generate access token and refresh token.
- Store hashed refresh token.

**Edge Cases:**

- Locked account.
- Deleted user.
- Repeated failed attempts should trigger rate limiting.

### Refresh Token

**Method:** POST  
**URL:** `/api/v1/auth/refresh-token`  
**Description:** Issue a new access token using a valid refresh token.  
**Allowed Roles:** All active users  
**Authentication Required:** No

**Request Params:** None  
**Query Params:** None  
**Request Body:**

```json
{
  "refresh_token": "jwt-refresh-token"
}
```

**Success Response:**

```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "new-jwt-access-token",
    "token_type": "bearer",
    "expires_in": 900
  },
  "errors": null
}
```

**Error Response:**

```json
{
  "success": false,
  "message": "Invalid refresh token",
  "data": null,
  "errors": [{"code": "AUTH_TOKEN_INVALID", "message": "Refresh token is invalid or revoked"}]
}
```

**Validation Rules:**

- Refresh token is required.
- Token type must be refresh.

**Database Tables Used:**

- users
- refresh_tokens

**Business Logic:**

- Validate signature and expiry.
- Validate token hash exists and is not revoked.
- Generate a new access token.

**Edge Cases:**

- Revoked token.
- Expired token.
- User no longer active.

### Get Current User

**Method:** GET  
**URL:** `/api/v1/auth/me`  
**Description:** Get authenticated user profile.  
**Allowed Roles:** All active users  
**Authentication Required:** Yes

**Request Params:** None  
**Query Params:** None  
**Request Body:**

```json
{}
```

**Success Response:**

```json
{
  "success": true,
  "message": "User fetched successfully",
  "data": {
    "id": 1,
    "first_name": "John",
    "last_name": "Admin",
    "email": "john.admin@example.com",
    "roles": ["ADMIN"],
    "permissions": ["students.create"]
  },
  "errors": null
}
```

**Error Response:**

```json
{
  "success": false,
  "message": "Authentication required",
  "data": null,
  "errors": [{"code": "AUTH_TOKEN_INVALID", "message": "Valid access token is required"}]
}
```

**Validation Rules:**

- Access token must be valid.

**Database Tables Used:**

- users
- roles
- permissions

**Business Logic:**

- Decode token.
- Fetch user with roles and permissions.
- Return profile.

**Edge Cases:**

- Token user no longer exists.
- User is inactive.

### Change Password

**Method:** POST  
**URL:** `/api/v1/auth/change-password`  
**Description:** Change current user's password.  
**Allowed Roles:** All active users  
**Authentication Required:** Yes

**Request Params:** None  
**Query Params:** None  
**Request Body:**

```json
{
  "current_password": "OldPassword@123",
  "new_password": "NewPassword@123"
}
```

**Success Response:**

```json
{
  "success": true,
  "message": "Password changed successfully",
  "data": null,
  "errors": null
}
```

**Error Response:**

```json
{
  "success": false,
  "message": "Current password is incorrect",
  "data": null,
  "errors": [{"code": "VALIDATION_ERROR", "field": "current_password", "message": "Current password is incorrect"}]
}
```

**Validation Rules:**

- Current password is required.
- New password must meet complexity rules.
- New password cannot equal current password.

**Database Tables Used:**

- users
- refresh_tokens
- audit_logs

**Business Logic:**

- Verify current password.
- Hash and store new password.
- Revoke existing refresh tokens.
- Write audit log.

**Edge Cases:**

- Weak new password.
- User account locked.

### Logout User

**Method:** POST  
**URL:** `/api/v1/auth/logout`  
**Description:** Revoke current refresh token or active session.  
**Allowed Roles:** All active users  
**Authentication Required:** Yes

**Request Params:** None  
**Query Params:** None  
**Request Body:**

```json
{
  "refresh_token": "jwt-refresh-token"
}
```

**Success Response:**

```json
{
  "success": true,
  "message": "Logout successful",
  "data": null,
  "errors": null
}
```

**Error Response:**

```json
{
  "success": false,
  "message": "Token not found",
  "data": null,
  "errors": [{"code": "RESOURCE_NOT_FOUND", "message": "Refresh token was not found"}]
}
```

**Validation Rules:**

- Refresh token is required when token storage is session-based.

**Database Tables Used:**

- refresh_tokens
- audit_logs

**Business Logic:**

- Hash provided refresh token.
- Mark token revoked.
- Write audit log.

**Edge Cases:**

- Already revoked token.
- Logout after password change.

### Verify Token

**Method:** GET  
**URL:** `/api/v1/auth/verify-token`  
**Description:** Verify the current access token.  
**Allowed Roles:** All active users  
**Authentication Required:** Yes

**Request Params:** None  
**Query Params:** None  
**Request Body:**

```json
{}
```

**Success Response:**

```json
{
  "success": true,
  "message": "Token is valid",
  "data": {
    "valid": true,
    "user_id": 1
  },
  "errors": null
}
```

**Error Response:**

```json
{
  "success": false,
  "message": "Token expired",
  "data": null,
  "errors": [{"code": "AUTH_TOKEN_EXPIRED", "message": "Access token has expired"}]
}
```

**Validation Rules:**

- Access token must be present and valid.

**Database Tables Used:**

- users

**Business Logic:**

- Decode token.
- Check token type.
- Confirm user is active.

**Edge Cases:**

- Expired token.
- Token signed with old key.

### Create Class

**Method:** POST  
**URL:** `/api/v1/classes/`  
**Description:** Create a class for an academic year.  
**Allowed Roles:** SUPER_ADMIN, ADMIN  
**Authentication Required:** Yes

**Request Params:** None  
**Query Params:** None  
**Request Body:**

```json
{
  "name": "Grade 1",
  "section": "A",
  "academic_year": "2026-2027",
  "capacity": 40
}
```

**Success Response:**

```json
{
  "success": true,
  "message": "Class created successfully",
  "data": {
    "id": 1,
    "name": "Grade 1",
    "section": "A",
    "academic_year": "2026-2027",
    "capacity": 40,
    "status": "active"
  },
  "errors": null
}
```

**Error Response:**

```json
{
  "success": false,
  "message": "Class already exists",
  "data": null,
  "errors": [{"code": "RESOURCE_CONFLICT", "message": "Class already exists for this section and academic year"}]
}
```

**Validation Rules:**

- Name is required.
- Capacity must be greater than zero.
- Academic year format must be valid.

**Database Tables Used:**

- classes
- audit_logs

**Business Logic:**

- Validate duplicate class.
- Create class.
- Write audit log.

**Edge Cases:**

- Duplicate class section.
- Invalid capacity.

### List Classes

**Method:** GET  
**URL:** `/api/v1/classes/`  
**Description:** List classes with pagination and filters.  
**Allowed Roles:** SUPER_ADMIN, ADMIN, PRINCIPAL, TEACHER, ADMISSION_OFFICER  
**Authentication Required:** Yes

**Request Params:** None  
**Query Params:** `page`, `limit`, `academic_year`, `status`, `sort_by`, `sort_order`  
**Request Body:**

```json
{}
```

**Success Response:**

```json
{
  "success": true,
  "message": "Classes fetched successfully",
  "data": [
    {
      "id": 1,
      "name": "Grade 1",
      "section": "A",
      "academic_year": "2026-2027",
      "capacity": 40,
      "status": "active"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_records": 1,
    "total_pages": 1
  },
  "errors": null
}
```

**Error Response:**

```json
{
  "success": false,
  "message": "Invalid query parameter",
  "data": null,
  "errors": [{"code": "VALIDATION_ERROR", "field": "limit", "message": "Limit must be between 1 and 100"}]
}
```

**Validation Rules:**

- Page must be greater than zero.
- Limit must be between 1 and 100.

**Database Tables Used:**

- classes

**Business Logic:**

- Apply filters.
- Exclude soft-deleted records.
- Return paginated results.

**Edge Cases:**

- Empty result set.
- Unsupported sort field.

### Get Class by ID

**Method:** GET  
**URL:** `/api/v1/classes/{class_id}`  
**Description:** Get class details.  
**Allowed Roles:** SUPER_ADMIN, ADMIN, PRINCIPAL, TEACHER, ADMISSION_OFFICER  
**Authentication Required:** Yes

**Request Params:** `class_id`  
**Query Params:** None  
**Request Body:**

```json
{}
```

**Success Response:**

```json
{
  "success": true,
  "message": "Class fetched successfully",
  "data": {
    "id": 1,
    "name": "Grade 1",
    "section": "A",
    "academic_year": "2026-2027",
    "capacity": 40,
    "status": "active"
  },
  "errors": null
}
```

**Error Response:**

```json
{
  "success": false,
  "message": "Class not found",
  "data": null,
  "errors": [{"code": "RESOURCE_NOT_FOUND", "message": "Class not found"}]
}
```

**Validation Rules:**

- Class ID must be a positive integer.

**Database Tables Used:**

- classes

**Business Logic:**

- Fetch non-deleted class by ID.
- Return details.

**Edge Cases:**

- Soft-deleted class requested.

### Update Class

**Method:** PUT  
**URL:** `/api/v1/classes/{class_id}`  
**Description:** Update class details.  
**Allowed Roles:** SUPER_ADMIN, ADMIN  
**Authentication Required:** Yes

**Request Params:** `class_id`  
**Query Params:** None  
**Request Body:**

```json
{
  "name": "Grade 1",
  "section": "B",
  "capacity": 45,
  "status": "active"
}
```

**Success Response:**

```json
{
  "success": true,
  "message": "Class updated successfully",
  "data": {
    "id": 1,
    "name": "Grade 1",
    "section": "B",
    "capacity": 45,
    "status": "active"
  },
  "errors": null
}
```

**Error Response:**

```json
{
  "success": false,
  "message": "Class capacity cannot be lower than enrolled students",
  "data": null,
  "errors": [{"code": "BUSINESS_RULE_VIOLATION", "message": "Capacity is below current student count"}]
}
```

**Validation Rules:**

- Capacity must be greater than zero.
- Status must be valid.

**Database Tables Used:**

- classes
- students
- audit_logs

**Business Logic:**

- Fetch class.
- Validate capacity against active student count.
- Update fields.
- Write audit log.

**Edge Cases:**

- Duplicate section.
- Capacity below current enrollment.

### Delete Class

**Method:** DELETE  
**URL:** `/api/v1/classes/{class_id}`  
**Description:** Soft delete a class if not actively used.  
**Allowed Roles:** SUPER_ADMIN, ADMIN  
**Authentication Required:** Yes

**Request Params:** `class_id`  
**Query Params:** None  
**Request Body:**

```json
{}
```

**Success Response:**

```json
{
  "success": true,
  "message": "Class deleted successfully",
  "data": null,
  "errors": null
}
```

**Error Response:**

```json
{
  "success": false,
  "message": "Class has active students",
  "data": null,
  "errors": [{"code": "BUSINESS_RULE_VIOLATION", "message": "Cannot delete class with active students"}]
}
```

**Validation Rules:**

- Class ID must exist.

**Database Tables Used:**

- classes
- students
- audit_logs

**Business Logic:**

- Check active student references.
- Set deleted fields.
- Write audit log.

**Edge Cases:**

- Class already deleted.
- Class assigned to teachers.

## Endpoint Pattern for Remaining Business Modules

The same exact documentation format applies to the remaining endpoints below. The request bodies, responses, validations, tables, logic, and edge cases are defined module-wise to avoid duplication while keeping implementation contracts clear.

### Inquiry Endpoints

| Endpoint | Roles | Request Body | Success Data | Tables | Main Rules |
|---|---|---|---|---|---|
| `POST /api/v1/inquiries` | Public or ADMISSION_OFFICER | `student_name`, `parent_name`, `phone`, `email`, `interested_class_id`, `message` | Inquiry object with `status=new` | inquiries, classes, audit_logs | Phone required; class must exist |
| `GET /api/v1/inquiries` | ADMIN, PRINCIPAL, ADMISSION_OFFICER | None | Paginated inquiries | inquiries, classes | Filter by status, class, date |
| `GET /api/v1/inquiries/{inquiry_id}` | ADMIN, PRINCIPAL, ADMISSION_OFFICER | None | Inquiry details | inquiries, classes | ID must exist |
| `PUT /api/v1/inquiries/{inquiry_id}` | ADMIN, ADMISSION_OFFICER | Editable inquiry fields | Updated inquiry | inquiries, audit_logs | Cannot edit approved inquiry except notes |
| `POST /api/v1/inquiries/{inquiry_id}/approve` | ADMIN, ADMISSION_OFFICER | `notes` | Approved inquiry | inquiries, students, audit_logs | Cannot approve rejected inquiry |
| `POST /api/v1/inquiries/{inquiry_id}/reject` | ADMIN, ADMISSION_OFFICER | `rejection_reason` | Rejected inquiry | inquiries, audit_logs | Reason required |

Standard inquiry create body:

```json
{
  "student_name": "Aarav Sharma",
  "parent_name": "Rohit Sharma",
  "phone": "+911234567890",
  "email": "parent@example.com",
  "interested_class_id": 1,
  "message": "Looking for admission details"
}
```

Standard inquiry response:

```json
{
  "id": 1,
  "student_name": "Aarav Sharma",
  "parent_name": "Rohit Sharma",
  "phone": "+911234567890",
  "email": "parent@example.com",
  "interested_class_id": 1,
  "status": "new"
}
```

Approval logic:

- Lock inquiry row.
- Ensure status is not approved or rejected.
- Validate interested class exists and is active.
- Mark inquiry approved.
- Optionally create prospective student.
- Write audit log.

Rejection logic:

- Require rejection reason.
- Lock inquiry row.
- Ensure status is not approved.
- Mark inquiry rejected.
- Store reason and audit log.

### Student Endpoints

| Endpoint | Roles | Request Body | Success Data | Tables | Main Rules |
|---|---|---|---|---|---|
| `POST /api/v1/students` | ADMIN, ADMISSION_OFFICER | Student profile fields | Student object | students, classes, audit_logs | Admission number unique |
| `GET /api/v1/students` | ADMIN, PRINCIPAL, TEACHER, ADMISSION_OFFICER | None | Paginated students | students, classes | Filter by class, status, search |
| `GET /api/v1/students/{student_id}` | ADMIN, PRINCIPAL, TEACHER, ADMISSION_OFFICER | None | Student details | students, classes, admissions | Exclude deleted |
| `PUT /api/v1/students/{student_id}` | ADMIN, ADMISSION_OFFICER | Editable profile fields | Updated student | students, audit_logs | Cannot update deleted student |
| `DELETE /api/v1/students/{student_id}` | ADMIN | None | Null | students, audit_logs | Soft delete only |
| `PUT /api/v1/students/{student_id}/status` | ADMIN, PRINCIPAL | `status`, `reason` | Updated status | students, audit_logs | Valid status transition required |
| `PUT /api/v1/students/{student_id}/class` | ADMIN, ADMISSION_OFFICER | `class_id`, `academic_year` | Updated class | students, classes, audit_logs | Class capacity must allow |

Student create body:

```json
{
  "admission_no": "ADM-2026-0001",
  "first_name": "Aarav",
  "last_name": "Sharma",
  "date_of_birth": "2018-04-10",
  "gender": "male",
  "email": "student@example.com",
  "phone": "+911234567890",
  "current_class_id": 1
}
```

Student response:

```json
{
  "id": 1,
  "admission_no": "ADM-2026-0001",
  "first_name": "Aarav",
  "last_name": "Sharma",
  "date_of_birth": "2018-04-10",
  "gender": "male",
  "current_class_id": 1,
  "status": "active"
}
```

Student lifecycle:

```text
prospective -> active -> graduated
prospective -> rejected
active -> inactive
active -> transferred
```

Soft delete behavior:

- Set `deleted_at`, `deleted_by`, and `is_active=false`.
- Do not physically delete student records.
- Exclude deleted records from normal list and detail queries.

### Student Admission Endpoints

| Endpoint | Roles | Request Body | Success Data | Tables | Main Rules |
|---|---|---|---|---|---|
| `GET /api/v1/students/admissions/all` | ADMIN, PRINCIPAL, ADMISSION_OFFICER | None | Paginated admissions | student_admissions, students, classes | Filter by status/year |
| `POST /api/v1/students/{student_id}/admission` | ADMIN, ADMISSION_OFFICER | `class_id`, `academic_year`, `notes` | Admission object | student_admissions, students, classes, audit_logs | One admission per year |
| `GET /api/v1/students/{student_id}/admission` | ADMIN, PRINCIPAL, ADMISSION_OFFICER | None | Student admission | student_admissions | Student must exist |
| `PUT /api/v1/students/admission/{admission_id}` | ADMIN, ADMISSION_OFFICER | Editable admission fields | Updated admission | student_admissions, audit_logs | Cannot edit approved admission except notes |
| `POST /api/v1/students/admission/{admission_id}/approve` | ADMIN, PRINCIPAL | `notes` | Approved admission | student_admissions, students, classes, audit_logs | Check capacity |
| `POST /api/v1/students/admission/{admission_id}/reject` | ADMIN, PRINCIPAL | `rejection_reason` | Rejected admission | student_admissions, audit_logs | Reason required |

Admission create body:

```json
{
  "class_id": 1,
  "academic_year": "2026-2027",
  "notes": "Documents verified"
}
```

Admission response:

```json
{
  "id": 1,
  "student_id": 1,
  "class_id": 1,
  "academic_year": "2026-2027",
  "status": "submitted",
  "rejection_reason": null
}
```

Admission status flow:

```text
draft -> submitted -> approved
draft -> submitted -> rejected
rejected -> submitted
```

Approval rules:

- Admission must be submitted.
- Student must not be deleted.
- Class must be active.
- Class capacity must not be exceeded.
- Approval must update student status and class assignment in the same transaction.

### Teacher Endpoints

| Endpoint | Roles | Request Body | Success Data | Tables | Main Rules |
|---|---|---|---|---|---|
| `POST /api/v1/teachers` | ADMIN | Teacher profile | Teacher object | teachers, users, audit_logs | Employee number unique |
| `GET /api/v1/teachers` | ADMIN, PRINCIPAL | None | Paginated teachers | teachers | Filter by status/search |
| `GET /api/v1/teachers/{teacher_id}` | ADMIN, PRINCIPAL | None | Teacher details | teachers | Teacher must exist |
| `PUT /api/v1/teachers/{teacher_id}` | ADMIN | Editable profile | Updated teacher | teachers, audit_logs | Cannot update resigned teacher without override |
| `POST /api/v1/teachers/{teacher_id}/subject` | ADMIN, PRINCIPAL | `subject_id` | Assignment | teachers, subjects, teacher_subjects | Prevent duplicate |
| `GET /api/v1/teachers/{teacher_id}/subject` | ADMIN, PRINCIPAL, TEACHER | None | Assigned subjects | teacher_subjects, subjects | Teacher must exist |
| `POST /api/v1/teachers/{teacher_id}/class` | ADMIN, PRINCIPAL | `class_id` | Assignment | teachers, classes, teacher_classes | Prevent duplicate |
| `GET /api/v1/teachers/{teacher_id}/class` | ADMIN, PRINCIPAL, TEACHER | None | Assigned classes | teacher_classes, classes | Teacher must exist |
| `POST /api/v1/teachers/{teacher_id}/attendance` | ADMIN, PRINCIPAL | `attendance_date`, `status`, `remarks` | Attendance record | teacher_attendance, audit_logs | Unique per date |
| `GET /api/v1/teachers/{teacher_id}/attendance` | ADMIN, PRINCIPAL, TEACHER | None | Attendance list | teacher_attendance | Filter by date range |
| `GET /api/v1/teachers/{teacher_id}/salary` | ADMIN, ACCOUNTANT | None | Salary setup | teacher_salary | Salary may not exist |
| `POST /api/v1/teachers/{teacher_id}/salary/payments` | ADMIN, ACCOUNTANT | Payment details | Payment record | teacher_salary, teacher_salary_payments, audit_logs | Prevent duplicate month |

Teacher create body:

```json
{
  "employee_no": "TCH-001",
  "first_name": "Neha",
  "last_name": "Mehta",
  "email": "neha.mehta@example.com",
  "phone": "+919876543210",
  "joining_date": "2026-06-01"
}
```

Teacher response:

```json
{
  "id": 1,
  "employee_no": "TCH-001",
  "first_name": "Neha",
  "last_name": "Mehta",
  "email": "neha.mehta@example.com",
  "phone": "+919876543210",
  "joining_date": "2026-06-01",
  "status": "active"
}
```

Subject assignment body:

```json
{
  "subject_id": 1
}
```

Class assignment body:

```json
{
  "class_id": 1
}
```

Attendance body:

```json
{
  "attendance_date": "2026-05-24",
  "status": "present",
  "remarks": "On time"
}
```

Salary payment body:

```json
{
  "payment_month": "2026-05",
  "gross_amount": 50000.00,
  "deduction_amount": 2500.00,
  "net_amount": 47500.00,
  "status": "paid",
  "paid_at": "2026-05-24T10:00:00Z"
}
```

Teacher salary workflow:

- Create teacher.
- Assign subjects.
- Assign classes.
- Configure salary record.
- Record attendance.
- Create salary payment after validating duplicate month and active salary setup.

## 22. Database Table Mapping for Every Module

| Module | Tables |
|---|---|
| Auth | users, roles, permissions, user_roles, refresh_tokens, audit_logs |
| Classes | classes, students, teacher_classes, audit_logs |
| Inquiries | inquiries, classes, students, audit_logs |
| Students | students, classes, student_admissions, audit_logs |
| Admissions | student_admissions, students, classes, audit_logs |
| Teachers | teachers, subjects, teacher_subjects, teacher_classes, teacher_attendance, teacher_salary, teacher_salary_payments, audit_logs |

## 23. Service Layer Responsibilities

Services must:

- Enforce business rules.
- Own transaction boundaries.
- Call repositories for persistence.
- Call audit service for tracked changes.
- Avoid direct HTTP request and response concerns.
- Return domain data to routes.

Examples:

- `AuthService.login`
- `ClassService.create_class`
- `InquiryService.approve_inquiry`
- `StudentService.assign_class`
- `AdmissionService.approve_admission`
- `TeacherService.create_salary_payment`

## 24. Repository Layer Responsibilities

Repositories must:

- Encapsulate database queries.
- Provide reusable query methods.
- Avoid business decisions.
- Avoid commits.
- Return ORM models or mapped data.

Examples:

- `get_by_id`
- `get_by_email`
- `list_paginated`
- `create`
- `update`
- `soft_delete`
- `exists_by_unique_fields`

## 25. Schema / DTO Standards

Use separate schemas:

- `CreateRequest`
- `UpdateRequest`
- `Response`
- `ListResponse`
- `FilterParams`

Example:

```text
StudentCreateRequest
StudentUpdateRequest
StudentResponse
StudentListResponse
StudentFilterParams
```

Rules:

- Request schemas validate input only.
- Response schemas expose safe output only.
- Never expose `password_hash` or token hashes.
- Use enums for statuses.

## 26. Naming Conventions

| Layer | Convention | Example |
|---|---|---|
| Routes | plural resource names | `/students` |
| Route function | verb_resource | `create_student` |
| Service class | PascalCase + Service | `StudentService` |
| Repository class | PascalCase + Repository | `StudentRepository` |
| ORM model | Singular PascalCase | `StudentAdmission` |
| DB table | snake_case plural | `student_admissions` |
| Schema | PascalCase purpose suffix | `StudentCreateRequest` |
| Status enum | PascalCase | `StudentStatus` |
| Permission code | module.action | `students.create` |

## 27. Deployment Readiness Checklist

- `.env.example` is complete.
- Production secrets are configured outside source control.
- Alembic migrations are tested.
- Database backup and restore process exists.
- CORS is restricted.
- HTTPS is enforced.
- Password hashing is strong.
- Refresh tokens are hashed and revocable.
- Rate limits are enabled for authentication endpoints.
- Structured logs include request IDs.
- Sensitive values are redacted from logs.
- Health check endpoint is available.
- CI runs linting, type checks, tests, and migrations.
- Docker image runs as non-root user.
- Database connection pool settings are production tuned.
- Error monitoring is configured.
- API docs are protected or disabled in production if required.
- Audit logs are retained according to policy.
- Authorization tests cover each protected endpoint.
- Workflow tests cover inquiry, admission, student, teacher salary, and token flows.

