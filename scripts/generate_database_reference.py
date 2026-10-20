"""Generate a database-column reference from the configured live database."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, create_engine, inspect

import app.models  # noqa: F401
from app.core.config import get_settings
from app.db.base import Base

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "database-schema-reference.md"

TABLE_DESCRIPTIONS = {
    "admission_documents": "Uploaded files and review state for an admission.",
    "alembic_version": "Alembic's internal record of the applied migration revision.",
    "audit_logs": "Audit trail for security-sensitive or business-changing actions.",
    "classes": "Class/grade offerings for an academic year.",
    "inquiry_admissions": "Formal admission applications linked to inquiries.",
    "inquiry_status_history": "Append-only history of inquiry status transitions.",
    "interview_schedules": "Scheduled interviews/tests and their results.",
    "permissions": "Permission codes granted to roles.",
    "refresh_tokens": "Hashed refresh-token records and revocation state.",
    "role_permissions": "Many-to-many links between roles and permissions.",
    "roles": "Named application roles.",
    "student_admissions": "Legacy student-based admission records retained for compatibility.",
    "student_inquiries": "Public admission inquiries and current workflow state.",
    "students": "Enrolled student records.",
    "subjects": "Subject catalog.",
    "teacher_attendance": "Teacher attendance by date.",
    "teacher_classes": "Many-to-many teacher/class assignments.",
    "teacher_salary": "Current salary terms for each teacher.",
    "teacher_salary_payments": "Monthly teacher salary payment records.",
    "teacher_subjects": "Many-to-many teacher/subject assignments.",
    "teachers": "Teacher employment profile.",
    "user_roles": "Many-to-many user/role assignments.",
    "users": "Accounts used for staff authentication and authorization.",
}

FIELD_DESCRIPTIONS = {
    "academic_year": "Academic year/session label associated with the record.",
    "action": "Audit action or permission action name.",
    "actor_user_id": "User account that performed the audited action, when available.",
    "admission_code": "Human-readable admission application identifier.",
    "admission_for_class": "Applicant-provided class/grade name requested for admission.",
    "admission_for_class_id": "Optional catalog class requested by the inquiry.",
    "admission_id": "Admission application that owns this uploaded document.",
    "admission_no": "Optional school admission number or legacy identifier.",
    "allowance": "Additional recurring salary allowance.",
    "approved_at": "Time the admission was approved, when approved.",
    "approved_by": "User who approved the admission, when applicable.",
    "attendance_date": "Calendar date covered by the attendance record.",
    "base_salary": "Recurring base salary amount.",
    "blood_group": "Applicant blood group, when provided.",
    "capacity": "Maximum number of students for the class.",
    "change_reason": "Optional reason recorded for an inquiry status transition.",
    "changed_by": "User who changed the inquiry status; null for system/public actions.",
    "class_id": "Class catalog record associated with this enrollment/application/assignment.",
    "code": "Stable code used to identify a role, permission, or subject.",
    "created_at": "Time the row was created.",
    "current_class": "Applicant-provided current class/grade text.",
    "current_class_id": "Legacy class link retained on student records.",
    "date_of_birth": "Student date of birth.",
    "deduction": "Recurring salary deduction.",
    "deduction_amount": "Salary payment deduction for this month.",
    "department": "Legacy department label retained on teacher rows.",
    "deleted_at": "Time the record was soft-deleted, if deleted.",
    "deleted_by": "Identifier of the actor recorded for soft deletion, when populated.",
    "description": "Human-readable description of a role or subject.",
    "disability": "Optional disability/support information provided for admission.",
    "document_type": "Category of document uploaded for an admission.",
    "duplicate_key": (
        "Normalized applicant identity hash used to prevent duplicate active inquiries."
    ),
    "effective_from": "Date the salary terms become effective.",
    "email": "Email address used for contact or account identity, depending on the table.",
    "employee_id": "Legacy employee identifier retained in the live database.",
    "employee_no": "Unique employee number assigned to a teacher.",
    "enrollment_number": "Legacy student enrollment identifier retained in the live database.",
    "entity_id": "Identifier of the affected entity, when available.",
    "entity_type": "Kind of entity affected by an audited action.",
    "expires_at": "Expiry time of the refresh-token record.",
    "father_name": "Father or legal guardian name supplied for the inquiry.",
    "file_name": "Original name of an uploaded document.",
    "file_path": "Storage path recorded for an uploaded document.",
    "first_name": "Given name of the person or student represented by the row.",
    "from_status": "Status before the transition; null for the initial history event.",
    "gender": "Student gender value.",
    "gross_amount": "Salary amount before monthly deductions.",
    "id": "Internal primary key for the row.",
    "inquiry_code": "Human-readable inquiry tracking code.",
    "inquiry_id": "Related student inquiry record.",
    "ip_address": "Client IP address captured for an audited request, when available.",
    "is_active": "Boolean flag indicating whether the record is active.",
    "last_login_at": "Time of the user's most recent successful login.",
    "last_name": "Family name of the person or student represented by the row.",
    "last_school": "Name of the school most recently attended.",
    "last_school_percentage": "Optional percentage/grade recorded from the previous school.",
    "location": "Interview location or meeting details.",
    "middle_name": "Optional student middle name.",
    "mime_type": "MIME type recorded for an uploaded document, when available.",
    "mode": "Interview mode, such as online or offline.",
    "module": "Permission module/category.",
    "name": "Display name of a class, role, or subject, depending on the table.",
    "nationality": "Optional applicant nationality.",
    "net_amount": "Salary take-home amount after deduction.",
    "notes": "Additional staff or admission notes.",
    "permanent_address": "Applicant's permanent residential address, when provided.",
    "old_values": "JSON snapshot of relevant values before an audited change.",
    "new_values": "JSON snapshot of relevant values after an audited change.",
    "parent_mobile": "Parent/guardian contact number used for inquiry verification.",
    "parent_name": "Legacy parent/guardian name retained in the live student table.",
    "parent_phone": "Legacy parent/guardian phone retained in the live student table.",
    "password_hash": "One-way password hash; the plain-text password is not stored.",
    "payment_month": "Salary month represented as YYYY-MM.",
    "paid_at": "Time payment was marked paid, when applicable.",
    "permission_id": "Related permission catalog row.",
    "phone": "Contact phone number, when available.",
    "qualification": "Legacy teacher qualification retained in the live database.",
    "reason_for_school_change": "Applicant-provided reason for changing schools.",
    "remarks": "Optional notes about attendance, scheduling, or interview outcome.",
    "rejection_reason": "Reason recorded when an inquiry, admission, or document is rejected.",
    "request_id": "Request correlation identifier used to connect logs and responses.",
    "result": "Interview outcome or result value, depending on the table.",
    "revoked_at": "Time a refresh token was revoked; null while not revoked.",
    "role_id": "Related role catalog row.",
    "roll_number": "Student position within the class and academic year.",
    "salary_id": "Salary terms record used to calculate this payment.",
    "schedule_date": "Calendar date scheduled for an interview.",
    "schedule_time": "Local time scheduled for an interview.",
    "section": "Class section associated with an offering or admission.",
    "serial_number": "Monotonic application serial used to form an inquiry code.",
    "specialization": "Legacy teacher specialization retained in the live database.",
    "status": "Current workflow, employment, account, attendance, or payment state.",
    "address": "Student residential address retained in the live database.",
    "interviewer_teacher_id": "Optional teacher assigned to conduct the interview.",
    "joining_date": "Teacher employment start date, when recorded.",
    "student_code": "Human-readable identifier assigned when a student is enrolled.",
    "student_id": "Related enrolled student record.",
    "student_mobile": "Optional student contact phone.",
    "subject_id": "Related subject catalog row.",
    "temporary_address": "Optional current address when different from permanent address.",
    "teacher_id": "Related teacher record.",
    "token_hash": "One-way hash of a refresh token; raw token is not stored.",
    "to_status": "Status after the inquiry transition.",
    "updated_at": "Time the row was most recently updated, when recorded.",
    "user_agent": "Client user-agent string captured for an audited request, when available.",
    "user_id": "Related user account.",
    "verified_at": "Time an uploaded document was verified or rejected.",
    "verified_by": "User who verified or rejected the uploaded document.",
    "verification_status": (
        "Review state of an uploaded document: pending, verified, or rejected."
    ),
    "version_num": "Current Alembic migration revision identifier.",
}

APPLICATION_GENERATED = {
    ("student_inquiries", "inquiry_code"): "Application generates the public code on create.",
    ("student_inquiries", "serial_number"): (
        "Application allocates the serial used in inquiry_code."
    ),
    ("student_inquiries", "duplicate_key"): (
        "Application derives a normalized identity hash; null when reapplication is allowed."
    ),
    ("inquiry_admissions", "admission_code"): (
        "Application generates the business code on admission creation."
    ),
    ("students", "student_code"): "Enrollment service generates this business identifier.",
    ("students", "roll_number"): (
        "Enrollment service assigns this within class and academic year."
    ),
    ("teachers", "employee_no"): (
        "Supplied by the teacher-create client; uniqueness is database-enforced."
    ),
}

API_VALIDATION_NOTES = {
    ("student_inquiries", "last_school_percentage"): (
        "API accepts 0–100; DB precision is Numeric(5,2)."
    ),
    ("teacher_salary_payments", "payment_month"): "API expects YYYY-MM; DB stores VARCHAR(7).",
    ("teacher_salary_payments", "net_amount"): (
        "API and DB require gross_amount - deduction_amount."
    ),
    ("teacher_salary_payments", "deduction_amount"): (
        "API and DB require 0 <= deduction <= gross amount."
    ),
}


def sql_type(column: dict[str, Any]) -> str:
    return str(column["type"]).upper()


def generated_by(column: dict[str, Any], table: str) -> str:
    custom = APPLICATION_GENERATED.get((table, column["name"]))
    if custom:
        return custom
    if column.get("autoincrement") is True:
        return "Database-generated auto-increment primary key."
    if column.get("default") is not None:
        return f"Database default: `{column['default']}`."
    model_table = Base.metadata.tables.get(table)
    if model_table is None or column["name"] not in model_table.columns:
        if table == "alembic_version" and column["name"] == "version_num":
            return "Alembic updates this value when migrations run."
        return "Unmapped live-database column; population source is not verifiable from the ORM."
    if column["name"] == "updated_at":
        return "Application ORM update hook; no database default."
    return "Client, service, or migration supplied; see source and API schema."


def description_for(column: dict[str, Any], table: str) -> tuple[str, str]:
    comment = column.get("comment")
    if comment:
        return str(comment), "Database comment"
    description = FIELD_DESCRIPTIONS.get(column["name"])
    if description:
        if column["name"] in {"status", "code", "name", "result", "email"}:
            description += f" Table context: `{table}`."
        return description, "Model/field-name documentation"
    return (
        f"Purpose is not explicitly documented in the database schema; inspect the "
        f"`{table}` model and service before changing this field.",
        "Not declared",
    )


def constraint_for(table_name: str, column_name: str, inspector: Any) -> str:
    markers = []
    pk = inspector.get_pk_constraint(table_name).get("constrained_columns") or []
    if column_name in pk:
        markers.append("PK")
    for fk in inspector.get_foreign_keys(table_name):
        if column_name in (fk.get("constrained_columns") or []):
            referred = f"{fk.get('referred_table')}.{','.join(fk.get('referred_columns') or [])}"
            markers.append(f"FK → `{referred}`")
            if fk.get("options", {}).get("ondelete"):
                markers.append(f"ON DELETE {fk['options']['ondelete']}")
    for unique in inspector.get_unique_constraints(table_name):
        columns = unique.get("column_names") or []
        if column_name in columns:
            other_columns = ", ".join(
                f"`{name}`" for name in columns if name != column_name
            )
            markers.append("UNIQUE" if not other_columns else f"UNIQUE with {other_columns}")
    for index in inspector.get_indexes(table_name):
        if index.get("unique") and column_name in (index.get("column_names") or []):
            columns = index.get("column_names") or []
            if not any("UNIQUE" in marker for marker in markers):
                other_columns = ", ".join(
                    f"`{name}`" for name in columns if name != column_name
                )
                markers.append(
                    "UNIQUE INDEX"
                    if not other_columns
                    else f"UNIQUE INDEX with {other_columns}"
                )
        elif column_name in (index.get("column_names") or []):
            markers.append("INDEX")
    return "; ".join(markers) or "—"


def table_constraints(inspector: Any, table: str) -> list[str]:
    items = []
    for unique in inspector.get_unique_constraints(table):
        columns = ", ".join(f"`{name}`" for name in unique.get("column_names") or [])
        items.append(f"UNIQUE ({columns})")
    for check in inspector.get_check_constraints(table):
        items.append(f"CHECK `{check.get('sqltext', 'expression unavailable')}`")
    for index in inspector.get_indexes(table):
        if not index.get("unique"):
            columns = ", ".join(f"`{name}`" for name in index.get("column_names") or [])
            items.append(f"INDEX `{index['name']}` ({columns})")
    return list(dict.fromkeys(items))


def generate(engine: Engine) -> None:
    inspector = inspect(engine)
    tables = sorted(inspector.get_table_names())
    revision = "unavailable"
    if "alembic_version" in tables:
        with engine.connect() as connection:
            current_revision = connection.exec_driver_sql(
                "SELECT version_num FROM alembic_version"
            ).scalar()
            revision = str(current_revision or "empty")

    live_tables = set(tables) - {"alembic_version"}
    model_tables = set(Base.metadata.tables)
    schema_differences = []
    for table in sorted(live_tables | model_tables):
        live_columns = (
            {column["name"] for column in inspector.get_columns(table)}
            if table in live_tables
            else set()
        )
        model_columns = (
            set(Base.metadata.tables[table].columns.keys())
            if table in model_tables
            else set()
        )
        db_only = sorted(live_columns - model_columns)
        model_only = sorted(model_columns - live_columns)
        if db_only or model_only:
            schema_differences.append((table, db_only, model_only))

    lines = [
        "# Database Schema Reference",
        "",
        f"> Generated from the configured database on {date.today().isoformat()}. "
        f"Applied Alembic revision: `{revision}`. This document lists actual database "
        "columns and constraints observed by SQLAlchemy's read-only schema inspector.",
        "",
        "## How to read this reference",
        "",
        "- `NOT NULL`/`NULL`, primary keys, foreign keys, unique constraints, indexes, "
        "defaults, and checks below are database metadata.",
        "- Application request validation can be stricter than the database. See the "
        "[API reference](api-reference.md) for API-required fields and input rules; those "
        "are not implied by database nullability.",
        "- `Client, service, or migration supplied` means metadata alone cannot determine "
        "which layer supplies the value. The note names application-generated identifiers "
        "where verified; inspect the linked model/service before assuming any other field "
        "is generated.",
        "- Column descriptions are sourced from database comments or explicit field notes. "
        "Where the source has no description, this is stated rather than guessed.",
        "- `AUTO_INCREMENT` identifiers are created by MySQL. Business codes and roll "
        "numbers are generated by application workflows, not by the database.",
        "",
        "## Live schema versus ORM model",
        "",
        "This snapshot is from the configured database. It is not safe to assume every "
        "column matches the current ORM model: migrations preserve some legacy columns. "
        "Review this generated reference after applying migrations and regenerate it with "
        "`python scripts\\generate_database_reference.py`.",
        "",
        "## Live database and ORM model differences",
        "",
        "The following differences were detected between this database snapshot and the "
        "registered SQLAlchemy models. Database-only columns may be retained for legacy "
        "compatibility; model-only columns are not present in this database snapshot. "
        "Do not assume a model-only field can be queried or written against this database "
        "until the required migration is applied. These differences are reported for "
        "visibility, not as an instruction to drop or add columns.",
        "",
    ]
    if schema_differences:
        lines.extend(
            [
                "| Table | Live database only | ORM model only |",
                "|---|---|---|",
            ]
        )
        for table, db_only, model_only in schema_differences:
            lines.append(
                f"| `{table}` | "
                f"{', '.join(f'`{name}`' for name in db_only) or '—'} | "
                f"{', '.join(f'`{name}`' for name in model_only) or '—'} |"
            )
        lines.append("")
    else:
        lines.extend(["No column differences detected.", ""])
    for table in tables:
        table_description = TABLE_DESCRIPTIONS.get(
            table, "Table description is not recorded in source."
        )
        lines.extend([f"## `{table}`", "", table_description, ""])
        columns = inspector.get_columns(table)
        if columns:
            lines.extend([
                "| Column | MySQL type | DB nullability | Default / generation "
                "| PK/FK/unique/index | Database/API rules | Description |",
                "|---|---|---|---|---|---|---|",
            ])
            for column in columns:
                name = column["name"]
                default = column.get("default")
                if default is None:
                    default_text = "—"
                else:
                    default_text = f"`{default}`"
                generation = generated_by(column, table)
                description, source = description_for(column, table)
                api_rule = API_VALIDATION_NOTES.get(
                    (table, name),
                    "No field-specific API rule recorded in this schema catalog.",
                )
                lines.append(
                    f"| `{name}` | `{sql_type(column)}` | "
                    f"{'NOT NULL' if not column['nullable'] else 'NULL'} | "
                    f"{default_text}; {generation} | "
                    f"{constraint_for(table, name, inspector)} | "
                    f"{api_rule} | {description} ({source}) |"
                )
            lines.append("")
        constraints = table_constraints(inspector, table)
        if constraints:
            lines.extend(["**Table constraints and indexes**", ""])
            lines.extend(f"- {constraint}" for constraint in constraints)
            lines.append("")

    OUTPUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({len(tables)} tables)")


def main() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    try:
        generate(engine)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
