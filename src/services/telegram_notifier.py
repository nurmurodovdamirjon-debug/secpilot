"""Telegram notification helper for monitoring alerts."""

import httpx
import structlog

from src.core.config import Settings


logger = structlog.get_logger(__name__)


def send_admin_alerts(settings: Settings, text: str, *, timeout: float = 5.0) -> None:
    if not settings.BOT_TOKEN:
        return
    for admin_id in settings.bot_admin_id_set:
        try:
            httpx.post(
                f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage",
                json={"chat_id": admin_id, "text": text},
                timeout=timeout,
            )
        except Exception as exc:
            logger.warning("telegram_alert_failed", admin_id=admin_id, error=str(exc))
