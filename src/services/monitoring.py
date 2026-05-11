"""Monitoring state and safe background checks."""

from datetime import UTC, datetime
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.config import Settings
from src.db.models import Asset, MonitoringState
from src.schemas.monitoring import MonitoringStatus
from src.services.audit_log import write_audit_event
from src.services.defensive_intel import extract_domain_from_asset
from src.services.dns_audit import collect_dns_audit
from src.services.ssl_audit import collect_ssl_audit


def get_or_create_monitoring_state(db: Session, asset: Asset) -> MonitoringState:
    state = db.scalar(select(MonitoringState).where(MonitoringState.asset_id == asset.id))
    if state is not None:
        return state
    state = MonitoringState(asset_id=asset.id, enabled=False)
    db.add(state)
    db.commit()
    db.refresh(state)
    return state


def set_monitoring_enabled(
    db: Session,
    *,
    asset: Asset,
    enabled: bool,
    actor_type: str,
    actor_id: str,
) -> MonitoringStatus:
    state = get_or_create_monitoring_state(db, asset)
    state.enabled = enabled
    db.commit()
    db.refresh(state)
    write_audit_event(
        db,
        actor_type=actor_type,
        actor_id=actor_id,
        action="monitoring.enable" if enabled else "monitoring.disable",
        result="allowed",
        object_type="asset",
        object_id=str(asset.id),
        meta={"enabled": enabled},
    )
    return monitoring_status_from_state(state)


def monitoring_status_from_state(state: MonitoringState) -> MonitoringStatus:
    return MonitoringStatus(
        asset_id=state.asset_id,
        enabled=state.enabled,
        last_check_at=state.last_check_at,
        last_status=state.last_status,
        last_detail=state.last_detail,
    )


def monitoring_scheduler_status(settings: Settings) -> dict[str, object]:
    return {
        "backend": settings.QUEUE_BACKEND,
        "task": "secpilot.monitoring.run_enabled_checks",
        "interval_seconds": settings.MONITORING_INTERVAL_SECONDS,
        "enabled": settings.QUEUE_BACKEND == "celery",
    }


def with_monitoring_scheduler_status(status: MonitoringStatus, settings: Settings) -> MonitoringStatus:
    return status.model_copy(update={"scheduler": monitoring_scheduler_status(settings)})


def record_monitoring_check(
    db: Session,
    *,
    asset_id: UUID,
    status: str,
    detail: dict[str, object],
) -> MonitoringStatus:
    state = db.scalar(select(MonitoringState).where(MonitoringState.asset_id == asset_id))
    if state is None:
        state = MonitoringState(asset_id=asset_id, enabled=False)
        db.add(state)
    state.last_check_at = datetime.now(UTC)
    state.last_status = status
    state.last_detail = detail
    db.commit()
    db.refresh(state)
    return monitoring_status_from_state(state)


def run_monitoring_check_for_asset(db: Session, *, asset: Asset, timeout: float) -> MonitoringStatus:
    domain = extract_domain_from_asset(asset.asset_type, asset.normalized_value)
    state = get_or_create_monitoring_state(db, asset)
    dns_result = collect_dns_audit(domain, timeout)
    ssl_result = collect_ssl_audit(domain, timeout)
    current_detail: dict[str, object] = {
        "domain": domain,
        "dns_a_records": dns_result.a_records,
        "ssl_days_remaining": ssl_result.days_remaining,
        "available": _check_asset_availability(domain, timeout),
    }
    status, reasons = evaluate_monitoring_alert(previous_detail=state.last_detail, current_detail=current_detail)
    current_detail["reasons"] = reasons
    result = record_monitoring_check(db, asset_id=asset.id, status=status, detail=current_detail)
    if status == "warning":
        write_audit_event(
            db,
            actor_type="worker",
            actor_id="monitoring",
            action="monitoring.alert",
            result="warning",
            object_type="asset",
            object_id=str(asset.id),
            meta=current_detail,
        )
    return result


def evaluate_monitoring_alert(
    *,
    previous_detail: dict[str, object] | None,
    current_detail: dict[str, object],
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    days_remaining = current_detail.get("ssl_days_remaining")
    if isinstance(days_remaining, int) and days_remaining <= 14:
        reasons.append("ssl_expiring_soon")
    if previous_detail:
        previous_records = previous_detail.get("dns_a_records")
        current_records = current_detail.get("dns_a_records")
        if previous_records is not None and previous_records != current_records:
            reasons.append("dns_changed")
    if current_detail.get("available") is False:
        reasons.append("asset_unavailable")
    return ("warning" if reasons else "ok"), reasons


def _check_asset_availability(domain: str, timeout: float) -> bool:
    try:
        response = httpx.get(f"https://{domain}", timeout=timeout, follow_redirects=False)
        return response.status_code < 500
    except Exception:
        return False
