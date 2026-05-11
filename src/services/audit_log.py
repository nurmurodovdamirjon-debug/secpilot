import structlog


logger = structlog.get_logger(__name__)


def write_audit_event(
    *,
    actor_type: str,
    actor_id: str,
    action: str,
    result: str,
    object_type: str | None = None,
    object_id: str | None = None,
) -> None:
    """MVP audit sink; DB persistence is wired through AuditLog model next."""
    logger.info(
        "audit_event",
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        object_type=object_type,
        object_id=object_id,
        result=result,
    )
