"""Background monitoring tasks for authorized SecPilot assets."""

import structlog
from sqlalchemy import select

from src.core.config import get_settings
from src.db.models import Asset, MonitoringState
from src.db.session import SessionLocal
from src.services.monitoring import run_monitoring_check_for_asset
from src.services.telegram_notifier import send_admin_alerts
from src.workers.celery_app import celery_app


logger = structlog.get_logger(__name__)


@celery_app.task(name="secpilot.monitoring.run_enabled_checks")
def run_enabled_monitoring_checks() -> dict[str, int]:
    settings = get_settings()
    checked = 0
    warnings = 0
    with SessionLocal() as db:
        states = db.scalars(select(MonitoringState).where(MonitoringState.enabled.is_(True))).all()
        for state in states:
            asset = db.get(Asset, state.asset_id)
            if asset is None or asset.status != "active" or asset.asset_type not in {"domain", "url"}:
                continue
            logger.info("monitoring_check_started", asset_id=str(asset.id))
            result = run_monitoring_check_for_asset(db, asset=asset, timeout=settings.INTEL_TIMEOUT_SECONDS)
            checked += 1
            if result.last_status == "warning":
                warnings += 1
                send_admin_alerts(settings, f"Monitoring ogohlantirish: {asset.value}")
            logger.info("monitoring_check_finished", asset_id=str(asset.id), status=result.last_status)
    return {"checked": checked, "warnings": warnings}
