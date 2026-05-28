import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.permissions import DEFAULT_PERMISSIONS, DEFAULT_ROLES, ROLE_PERMISSION_MAP
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.class_model import Class
from app.models.enums import ClassStatus, UserStatus
from app.models.permission import Permission, RolePermission
from app.models.role import Role, UserRole
from app.models.user import User

DEFAULT_CLASSES: list[tuple[str, str | None, str, int]] = [
    ("1st Grade", "A", "2025-26", 40),
    ("2nd Grade", "A", "2025-26", 40),
    ("3rd Grade", "A", "2025-26", 40),
    ("4th Grade", "A", "2025-26", 40),
    ("5th Grade", "A", "2025-26", 40),
    ("6th Grade", "A", "2025-26", 40),
    ("7th Grade", "A", "2025-26", 40),
    ("8th Grade", "A", "2025-26", 40),
    ("9th Grade", "A", "2025-26", 40),
    ("10th Grade", "A", "2025-26", 40),
]

logger = logging.getLogger("app.seed")


def seed_database(session: Session | None = None) -> None:
    """
    Seed default roles, permissions, and super admin user.

    Args:
        session: Optional session (for tests). Uses ``SessionLocal`` when omitted.
    """
    owns_session = session is None
    if owns_session:
        session = SessionLocal()
    try:
        _seed_roles_and_permissions(session)
        _seed_super_admin(session)
        _seed_classes(session)
        session.commit()
    except Exception:
        session.rollback()
        logger.exception("database seed failed")
    finally:
        if owns_session:
            session.close()


def _seed_roles_and_permissions(session: Session) -> None:
    role_map: dict[str, Role] = {}
    for code, name, description in DEFAULT_ROLES:
        role = session.scalar(select(Role).where(Role.code == code))
        if not role:
            role = Role(code=code, name=name, description=description, is_active=True)
            session.add(role)
            session.flush()
        role_map[code] = role

    permission_map: dict[str, Permission] = {}
    for code, module, action in DEFAULT_PERMISSIONS:
        permission = session.scalar(select(Permission).where(Permission.code == code))
        if not permission:
            permission = Permission(code=code, module=module, action=action)
            session.add(permission)
            session.flush()
        permission_map[code] = permission

    for role_code, permission_codes in ROLE_PERMISSION_MAP.items():
        role = role_map[role_code]
        for permission_code in permission_codes:
            permission = permission_map[permission_code]
            exists = session.scalar(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == permission.id,
                )
            )
            if not exists:
                session.add(RolePermission(role_id=role.id, permission_id=permission.id))


def _seed_super_admin(session: Session) -> None:
    # Use a TLD accepted by strict validators; AppEmail also allows *.local for dev.
    email = "superadmin@school.com"
    user = session.scalar(select(User).where(User.email == email))
    if user:
        return
    role = session.scalar(select(Role).where(Role.code == "SUPER_ADMIN"))
    if not role:
        return
    user = User(
        first_name="Super",
        last_name="Admin",
        email=email,
        phone=None,
        password_hash=hash_password("SuperAdmin@123"),
        status=UserStatus.ACTIVE.value,
    )
    session.add(user)
    session.flush()
    session.add(UserRole(user_id=user.id, role_id=role.id))
    logger.info("seeded default super admin user: %s", email)


def _seed_classes(session: Session) -> None:
    """Seed catalog classes for public inquiry ``admission_for_class_id`` FK."""
    for name, section, academic_year, capacity in DEFAULT_CLASSES:
        exists = session.scalar(
            select(Class.id).where(
                Class.name == name,
                Class.section == section,
                Class.academic_year == academic_year,
                Class.deleted_at.is_(None),
            )
        )
        if exists:
            continue
        session.add(
            Class(
                name=name,
                section=section,
                academic_year=academic_year,
                capacity=capacity,
                status=ClassStatus.ACTIVE.value,
                is_active=True,
            )
        )
    logger.info("seeded default school classes (grades 1–10)")
