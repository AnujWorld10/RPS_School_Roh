"""Add an atomic uniqueness key for active applicant inquiries.

Revision ID: 008_inquiry_duplicate_key
Revises: 007_refresh_tokens
"""

import json
from collections.abc import Sequence
from datetime import date
from hashlib import sha256

import sqlalchemy as sa

from alembic import op

revision: str = "008_inquiry_duplicate_key"
down_revision: str | None = "007_refresh_tokens"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _identity_key(
    first_name: str,
    last_name: str,
    father_name: str,
    date_of_birth: date,
) -> str:
    identity = [
        " ".join(value.split()).casefold()
        for value in (first_name, last_name, father_name)
    ]
    identity.append(date_of_birth.isoformat())
    canonical = json.dumps(identity, ensure_ascii=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("student_inquiries"):
        return

    columns = {column["name"] for column in inspector.get_columns("student_inquiries")}
    if "duplicate_key" not in columns:
        op.add_column(
            "student_inquiries",
            sa.Column("duplicate_key", sa.String(length=64), nullable=True),
        )

    inquiries = sa.table(
        "student_inquiries",
        sa.column("id", sa.Integer),
        sa.column("first_name", sa.String),
        sa.column("last_name", sa.String),
        sa.column("father_name", sa.String),
        sa.column("date_of_birth", sa.Date),
        sa.column("status", sa.String),
        sa.column("duplicate_key", sa.String),
    )
    rows = bind.execute(
        sa.select(
            inquiries.c.id,
            inquiries.c.first_name,
            inquiries.c.last_name,
            inquiries.c.father_name,
            inquiries.c.date_of_birth,
            inquiries.c.status,
            inquiries.c.duplicate_key,
        ).order_by(inquiries.c.id)
    )
    seen_keys: set[str] = set()
    for row in rows:
        if row.status in {"REJECTED", "INTERVIEW_FAIL"}:
            if row.duplicate_key is not None:
                bind.execute(
                    inquiries.update()
                    .where(inquiries.c.id == row.id)
                    .values(duplicate_key=None)
                )
            continue
        if row.duplicate_key is not None:
            seen_keys.add(row.duplicate_key)
            continue
        if row.date_of_birth is None:
            continue
        key = _identity_key(
            row.first_name or "",
            row.last_name or "",
            row.father_name or "",
            row.date_of_birth,
        )
        if key in seen_keys:
            continue
        bind.execute(
            inquiries.update()
            .where(inquiries.c.id == row.id)
            .values(duplicate_key=key)
        )
        seen_keys.add(key)

    indexes = {index["name"] for index in inspector.get_indexes("student_inquiries")}
    if "uq_student_inquiry_duplicate_key" not in indexes:
        op.create_index(
            "uq_student_inquiry_duplicate_key",
            "student_inquiries",
            ["duplicate_key"],
            unique=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("student_inquiries"):
        return

    indexes = {index["name"] for index in inspector.get_indexes("student_inquiries")}
    if "uq_student_inquiry_duplicate_key" in indexes:
        op.drop_index("uq_student_inquiry_duplicate_key", table_name="student_inquiries")

    columns = {column["name"] for column in inspector.get_columns("student_inquiries")}
    if "duplicate_key" in columns:
        op.drop_column("student_inquiries", "duplicate_key")
