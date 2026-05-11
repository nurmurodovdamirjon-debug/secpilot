"""Audit log persistence for security-relevant events."""

from typing import Any

import structlog
from sqlalchemy.orm import Session

from src.db.models import AuditLog


logger = structlog.get_logger(__name__)


def write_audit_event(
    db: Session | None = None,
    *,
    actor_type: str,
    actor_id: str,
    action: str,
    result: str,
    object_type: str | None = None,
    object_id: str | None = None,
    meta: dict[str, Any] | None = None,
) -> AuditLog | None:
    """Persist an audit event when a DB session is available, and always log it."""
    logger.info(
        "audit_event",
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        object_type=object_type,
        object_id=object_id,
        result=result,
    )
    if db is None:
        return None

    audit_log = AuditLog(
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        object_type=object_type,
        object_id=object_id,
        result=result,
        meta_jsonb=meta or {},
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log
