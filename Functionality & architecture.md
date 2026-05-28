# School Management System (SMS) – Functional Requirement & System Design Document

## Project Overview

The purpose of this system is to build a complete and scalable **School Management System** using:

* Python
* FastAPI
* SQLAlchemy
* MySQL/PostgreSQL
* JWT Authentication
* Alembic Migration

The system will manage:

* Student Inquiry
* Admission Process
* Interview/Test Process
* Student Enrollment
* Teacher & Staff Hiring
* Academic Management
* Result Management
* Authentication & Authorization
* Logs & Monitoring

---

# 1. Core Modules

## Student Modules

1. Public Student Inquiry
2. Inquiry Status Tracking
3. Inquiry Modification
4. Inquiry Review Process
5. Interview/Test Scheduling
6. Admission Form Submission
7. Document Verification
8. Student Enrollment
9. Roll Number Allocation
10. Academic Result Management

---

## School Management Modules

1. Teacher Management
2. Staff Management
3. Class Management
4. Subject Management
5. Academic Session Management
6. Student Attendance
7. Result Management
8. Notification Management

---

## Career Module

1. Teacher Job Inquiry
2. Staff Hiring
3. Interview Process
4. Document Verification
5. Employee Onboarding

---

# 2. Main Workflow

---

# Student Inquiry Flow

```text
Student Inquiry Form
        ↓
Inquiry Created
        ↓
Inquiry ID Generated
        ↓
Status = PENDING
        ↓
School Reviews Inquiry
        ↓
UNDER_REVIEW
        ↓
PROCESSING
        ↓
Interview/Test Scheduled
        ↓
PASS / FAIL
        ↓
Admission Form Submission
        ↓
Document Verification
        ↓
ADMISSION_SUCCESS
        ↓
Student ID + Roll Number Generated
```

---

# 3. Student Inquiry Module

## Public API

### POST `/api/v1/public/student/inquiry`

This API will be publicly available.

## Required Fields

| Field                  | Type    | Mandatory |
| ---------------------- | ------- | --------- |
| first_name             | String  | Yes       |
| middle_name            | String  | No        |
| last_name              | String  | Yes       |
| gender                 | Enum    | Yes       |
| father_name            | String  | Yes       |
| dob                    | Date    | Yes       |
| student_mobile         | String  | No        |
| parent_mobile          | String  | Yes       |
| email                  | String  | Yes       |
| address                | Text    | Yes       |
| last_school            | String  | Yes       |
| current_class          | String  | Yes       |
| admission_for_class    | String  | Yes       |
| last_school_percentage | Decimal | No        |

---

## Auto Generated Fields

| Field         | Description       |
| ------------- | ----------------- |
| inquiry_id    | Unique Inquiry ID |
| created_at    | Created DateTime  |
| updated_at    | Updated DateTime  |
| serial_number | Auto Increment    |

---

# Inquiry Status Values

| Status                |
| --------------------- |
| PENDING               |
| UNDER_REVIEW          |
| PROCESSING            |
| INTERVIEW_SCHEDULED   |
| INTERVIEW_PASS        |
| INTERVIEW_FAIL        |
| DOCUMENT_PENDING      |
| DOCUMENT_VERIFICATION |
| ADMISSION_SUCCESS     |
| REJECTED              |

---

# 4. Inquiry Status Check API

## GET `/api/v1/public/student/inquiry/status/{inquiry_id}`

Public API.

Student can check:

* Inquiry Status
* Interview Schedule
* Admission Status
* Rejection Reason

---

# 5. Inquiry Modify API

## PUT `/api/v1/public/student/inquiry/update`

## Required Validation

Student must provide:

* inquiry_id
* email
* parent_mobile

Only then update is allowed.

---

# 6. School Management Review Process

Authorized users only.

## Admin Actions

| Action         | Status       |
| -------------- | ------------ |
| Review Started | UNDER_REVIEW |
| Eligible       | PROCESSING   |
| Rejected       | REJECTED     |

---

# 7. Interview/Test Module

## Interview Details

| Field                  |
| ---------------------- |
| interview_id           |
| inquiry_id             |
| schedule_date          |
| schedule_time          |
| location               |
| mode (ONLINE/OFFLINE)  |
| interviewer_teacher_id |
| remarks                |
| result                 |

---

# Interview Status

| Status    |
| --------- |
| SCHEDULED |
| PASSED    |
| FAILED    |
| ABSENT    |

---

# 8. Admission Module

After interview pass.

## Admission API

### POST `/api/v1/student/admission`

---

## Required Documents

| Document              |
| --------------------- |
| Progress Report Card  |
| Transfer Certificate  |
| Migration Certificate |
| Character Certificate |
| Student Aadhar        |
| Parent Aadhar         |

---

## Additional Details

| Field                    |
| ------------------------ |
| permanent_address        |
| temporary_address        |
| nationality              |
| disability               |
| blood_group              |
| reason_for_school_change |

---

# Document Verification Status

| Status   |
| -------- |
| PENDING  |
| VERIFIED |
| REJECTED |

---

# 9. Student Enrollment

Once admission is successful:

System generates:

| Field        |
| ------------ |
| admission_id |
| student_id   |
| roll_number  |
| class_id     |
| section_id   |

---

# 10. Academic Structure

---

# Class Table

| Field            |
| ---------------- |
| class_id         |
| class_name       |
| section          |
| class_teacher_id |

---

# Subject Table

| Field        |
| ------------ |
| subject_id   |
| subject_name |
| class_id     |

---

# Result Table

| Field      |
| ---------- |
| result_id  |
| student_id |
| subject_id |
| marks      |
| grade      |
| remarks    |

---

# 11. Teacher Management

## Teacher Table

| Field         |
| ------------- |
| teacher_id    |
| first_name    |
| last_name     |
| mobile        |
| email         |
| qualification |
| experience    |
| joining_date  |

---

# 12. Career Module

Publicly available hiring system.

---

# Hiring Flow

```text
Candidate Applies
        ↓
Application Submitted
        ↓
HR Review
        ↓
Interview Scheduled
        ↓
Document Verification
        ↓
Selected / Rejected
        ↓
Employee ID Generated
```

---

# Career APIs

| API                |
| ------------------ |
| Apply Job          |
| Check Status       |
| Update Application |
| Upload Documents   |

---

# 13. Database Design

---

# Main Tables

| Table Name             |
| ---------------------- |
| student_inquiry        |
| inquiry_status_history |
| interview_schedule     |
| admission              |
| admission_documents    |
| student                |
| classes                |
| sections               |
| subjects               |
| student_results        |
| teachers               |
| academic_sessions      |
| attendance             |
| employee_inquiry       |
| employee_interview     |
| users                  |
| roles                  |
| permissions            |
| audit_logs             |

---

# 14. Important Relationships

---

# Student Relationships

```text
student_inquiry
    ↓
interview_schedule
    ↓
admission
    ↓
student
    ↓
student_results
```

---

# Foreign Key Relationships

| Parent Table    | Child Table        | Relationship |
| --------------- | ------------------ | ------------ |
| student_inquiry | interview_schedule | One to One   |
| student_inquiry | admission          | One to One   |
| admission       | student            | One to One   |
| classes         | students           | One to Many  |
| teachers        | classes            | One to Many  |
| students        | results            | One to Many  |
| subjects        | results            | One to Many  |

---

# 15. Authentication & Authorization

## Authentication APIs

| API             |
| --------------- |
| Login           |
| Refresh Token   |
| Logout          |
| Forgot Password |
| Reset Password  |

---

# Roles

| Role         |
| ------------ |
| SUPER_ADMIN  |
| ADMIN        |
| PRINCIPAL    |
| TEACHER      |
| ACCOUNTANT   |
| RECEPTIONIST |
| HR           |

---

# JWT Authentication

Use:

* Access Token
* Refresh Token
* Role Based Access

---

# 16. Required Backend APIs

---

# Public APIs

| API             |
| --------------- |
| Student Inquiry |
| Inquiry Status  |
| Inquiry Update  |
| Career Apply    |
| Career Status   |

---

# Protected APIs

| API                |
| ------------------ |
| Review Inquiry     |
| Schedule Interview |
| Verify Documents   |
| Create Student     |
| Manage Classes     |
| Manage Results     |
| Manage Teachers    |
| Manage Subjects    |

---

# 17. Audit & Logging System

## Audit Log Table

Track:

* User Activity
* Login Activity
* Status Change
* Data Modification
* API Request Logs

---

# 18. Exception Handling

Global exception handler required.

## Exceptions

| Exception                 |
| ------------------------- |
| Validation Error          |
| Authentication Error      |
| Authorization Error       |
| Database Error            |
| File Upload Error         |
| Custom Business Exception |

---

# 19. File Upload System

Allowed document uploads:

* PDF
* JPG
* PNG

---

# Upload Storage

| Option        |
| ------------- |
| Local Storage |
| AWS S3        |
| Azure Blob    |

---

# 20. Recommended Folder Structure

```text
school_management_system/
│
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── public/
│   │   │   ├── auth/
│   │   │   ├── student/
│   │   │   ├── teacher/
│   │   │   ├── admission/
│   │   │   ├── inquiry/
│   │   │   ├── results/
│   │   │   ├── classes/
│   │   │   ├── career/
│   │   │   └── health/
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── constants.py
│   │   └── dependencies.py
│   │
│   ├── models/
│   │   ├── student.py
│   │   ├── inquiry.py
│   │   ├── admission.py
│   │   ├── teacher.py
│   │   ├── result.py
│   │   ├── class.py
│   │   ├── subject.py
│   │   ├── employee.py
│   │   └── auth.py
│   │
│   ├── schemas/
│   │   ├── inquiry.py
│   │   ├── admission.py
│   │   ├── student.py
│   │   ├── teacher.py
│   │   └── auth.py
│   │
│   ├── services/
│   │   ├── inquiry_service.py
│   │   ├── admission_service.py
│   │   ├── auth_service.py
│   │   └── result_service.py
│   │
│   ├── repositories/
│   │   ├── inquiry_repo.py
│   │   ├── student_repo.py
│   │   └── admission_repo.py
│   │
│   ├── utils/
│   │   ├── helpers.py
│   │   ├── validators.py
│   │   ├── response.py
│   │   └── exceptions.py
│   │
│   ├── middleware/
│   │   ├── auth_middleware.py
│   │   └── logging_middleware.py
│   │
│   ├── uploads/
│   │
│   └── main.py
│
├── alembic/
├── tests/
│   ├── test_auth.py
│   ├── test_inquiry.py
│   ├── test_student.py
│   └── test_admission.py
│
├── .env
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── README.md
└── pytest.ini
```

---

# 21. Mandatory APIs

| API                 |
| ------------------- |
| Health Check API    |
| Authentication API  |
| Role Management API |
| Permission API      |
| Audit Log API       |
| File Upload API     |
| Notification API    |

---

# 22. Health Check API

## GET `/health`

Response:

```json
{
  "status": "UP",
  "database": "CONNECTED",
  "server_time": "2026-05-26T10:30:00"
}
```

---

# 23. Recommended Technologies

| Component      | Technology       |
| -------------- | ---------------- |
| Backend        | Python + FastAPI |
| ORM            | SQLAlchemy       |
| Database       | PostgreSQL/MySQL |
| Migration      | Alembic          |
| Authentication | JWT              |
| Validation     | Pydantic         |
| Testing        | Pytest           |
| Deployment     | Docker           |
| Reverse Proxy  | Nginx            |

---

# 24. Future Enhancements

1. Fee Management
2. Bus Tracking
3. Mobile App
4. Parent Portal
5. Student Portal
6. Online Exam
7. Library Management
8. AI Attendance
9. SMS/Email Notification
10. Report Generation

---

# 25. Recommended Development Phases

## Phase 1

* Project Setup
* Authentication
* Inquiry Module
* Database Setup

---

## Phase 2

* Interview Module
* Admission Module
* Student Enrollment

---

## Phase 3

* Teacher Management
* Result Management
* Attendance

---

## Phase 4

* Career Module
* Notifications
* Reports
* Audit Logs

---

# 26. Suggested Important IDs

| Entity       | Format Example |
| ------------ | -------------- |
| Inquiry ID   | INQ20260001    |
| Admission ID | ADM20260001    |
| Student ID   | STU20260001    |
| Employee ID  | EMP20260001    |
| Roll Number  | 101            |

---

# 27. Enterprise-Level Best Practices

1. Soft Delete
2. Audit Columns
3. UUID Support
4. Pagination
5. Rate Limiting
6. API Versioning
7. Redis Caching
8. Background Jobs
9. Email Notifications
10. Structured Logging
11. Swagger Documentation
12. Centralized Exception Handling
13. Environment Based Configurations
