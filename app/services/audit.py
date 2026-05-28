from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.audit import AuditRepository


class AuditService:
    def __init__(self, session: Session) -> None:
        self.repo = AuditRepository(session)

    def log(
        self,
        *,
        action: str,
        entity_type: str,
        entity_id: int | None = None,
        actor_user_id: int | None = None,
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
        request: Request | None = None,
    ) -> AuditLog:
        request_id = "system"
        ip_address = None
        user_agent = None
        if request is not None:
            request_id = getattr(request.state, "request_id", "unknown")
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
        return self.repo.create(
            AuditLog(
                actor_user_id=actor_user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                old_values=old_values,
                new_values=new_values,
                request_id=request_id,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )
