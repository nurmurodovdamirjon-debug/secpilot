from aiogram.types import Message

from src.core.config import Settings
from src.services.audit_log import write_audit_event


def is_admin(message: Message, settings: Settings) -> bool:
    user_id = message.from_user.id if message.from_user else None
    return is_admin_user_id(user_id, settings)


def is_admin_user_id(user_id: int | None, settings: Settings) -> bool:
    allowed = user_id in settings.bot_admin_id_set
    if not allowed and user_id is not None:
        write_audit_event(
            actor_type="telegram_user",
            actor_id=str(user_id),
            action="bot_access_denied",
            result="denied",
        )
    return allowed
