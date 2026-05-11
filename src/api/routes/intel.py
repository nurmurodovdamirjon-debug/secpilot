"""Defensive-only passive intelligence API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import structlog

from src.api.dependencies import require_api_key
from src.api.errors import ApiError
from src.core.config import Settings, get_settings
from src.db.session import get_db_session
from src.schemas.dns import DnsAuditResult
from src.schemas.monitoring import MonitoringStatus
from src.schemas.ssl import SslAuditResult
from src.schemas.subdomains import SubdomainDiscoveryResult
from src.services.defensive_intel import audit_intel_action, get_authorized_domain_asset
from src.services.audit_log import write_audit_event
from src.services.dns_audit import collect_dns_audit
from src.services.monitoring import (
    get_or_create_monitoring_state,
    monitoring_status_from_state,
    set_monitoring_enabled,
    with_monitoring_scheduler_status,
)
from src.services.rate_limit import RateLimitExceededError, rate_limiter
from src.services.ssl_audit import collect_ssl_audit
from src.services.subdomains import collect_passive_subdomains


router = APIRouter(prefix="/api/v1", tags=["defensive-intel"])
logger = structlog.get_logger(__name__)


class AssetActionRequest(BaseModel):
    asset_id: UUID = Field(description="Authorized active domain/url asset ID.")


@router.get("/dns/{asset_id}", response_model=DnsAuditResult)
def dns_audit_endpoint(
    asset_id: UUID,
    db: Session = Depends(get_db_session),
    actor: tuple[str, str] = Depends(require_api_key),
    settings: Settings = Depends(get_settings),
) -> DnsAuditResult:
    return _run_dns_audit(db=db, asset_id=asset_id, actor=actor, settings=settings)


@router.post("/dns/audit", response_model=DnsAuditResult)
def dns_audit_contract_endpoint(
    request: AssetActionRequest,
    db: Session = Depends(get_db_session),
    actor: tuple[str, str] = Depends(require_api_key),
    settings: Settings = Depends(get_settings),
) -> DnsAuditResult:
    return _run_dns_audit(db=db, asset_id=request.asset_id, actor=actor, settings=settings)


def _run_dns_audit(
    *,
    db: Session,
    asset_id: UUID,
    actor: tuple[str, str],
    settings: Settings,
) -> DnsAuditResult:
    _check_rate_limit(actor, "dns", settings)
    asset, domain = _get_authorized_asset_for_action(db, asset_id, actor, "dns.audit")
    logger.info("dns_audit_started", asset_id=str(asset_id), domain=domain)
    result = collect_dns_audit(domain, settings.INTEL_TIMEOUT_SECONDS)
    audit_intel_action(db, actor_type=actor[0], actor_id=actor[1], action="dns.audit", asset=asset, result="allowed")
    logger.info("dns_audit_finished", asset_id=str(asset_id), domain=domain)
    return result


@router.get("/ssl/{asset_id}", response_model=SslAuditResult)
def ssl_audit_endpoint(
    asset_id: UUID,
    db: Session = Depends(get_db_session),
    actor: tuple[str, str] = Depends(require_api_key),
    settings: Settings = Depends(get_settings),
) -> SslAuditResult:
    return _run_ssl_audit(db=db, asset_id=asset_id, actor=actor, settings=settings)


@router.post("/ssl/audit", response_model=SslAuditResult)
def ssl_audit_contract_endpoint(
    request: AssetActionRequest,
    db: Session = Depends(get_db_session),
    actor: tuple[str, str] = Depends(require_api_key),
    settings: Settings = Depends(get_settings),
) -> SslAuditResult:
    return _run_ssl_audit(db=db, asset_id=request.asset_id, actor=actor, settings=settings)


def _run_ssl_audit(
    *,
    db: Session,
    asset_id: UUID,
    actor: tuple[str, str],
    settings: Settings,
) -> SslAuditResult:
    _check_rate_limit(actor, "ssl", settings)
    asset, domain = _get_authorized_asset_for_action(db, asset_id, actor, "ssl.audit")
    logger.info("ssl_audit_started", asset_id=str(asset_id), domain=domain)
    result = collect_ssl_audit(domain, settings.INTEL_TIMEOUT_SECONDS)
    audit_intel_action(db, actor_type=actor[0], actor_id=actor[1], action="ssl.audit", asset=asset, result="allowed")
    logger.info("ssl_audit_finished", asset_id=str(asset_id), domain=domain)
    return result


@router.get("/subdomains/{asset_id}", response_model=SubdomainDiscoveryResult)
def subdomain_discovery_endpoint(
    asset_id: UUID,
    db: Session = Depends(get_db_session),
    actor: tuple[str, str] = Depends(require_api_key),
    settings: Settings = Depends(get_settings),
) -> SubdomainDiscoveryResult:
    return _run_subdomain_discovery(db=db, asset_id=asset_id, actor=actor, settings=settings)


@router.post("/subdomains/passive", response_model=SubdomainDiscoveryResult)
def subdomain_discovery_contract_endpoint(
    request: AssetActionRequest,
    db: Session = Depends(get_db_session),
    actor: tuple[str, str] = Depends(require_api_key),
    settings: Settings = Depends(get_settings),
) -> SubdomainDiscoveryResult:
    return _run_subdomain_discovery(db=db, asset_id=request.asset_id, actor=actor, settings=settings)


def _run_subdomain_discovery(
    *,
    db: Session,
    asset_id: UUID,
    actor: tuple[str, str],
    settings: Settings,
) -> SubdomainDiscoveryResult:
    _check_rate_limit(actor, "subdomains", settings)
    asset, domain = _get_authorized_asset_for_action(db, asset_id, actor, "subdomains.passive_discovery")
    logger.info("subdomain_discovery_started", asset_id=str(asset_id), domain=domain)
    result = collect_passive_subdomains(domain, settings.INTEL_TIMEOUT_SECONDS)
    audit_intel_action(
        db,
        actor_type=actor[0],
        actor_id=actor[1],
        action="subdomains.passive_discovery",
        asset=asset,
        result="allowed",
    )
    logger.info("subdomain_discovery_finished", asset_id=str(asset_id), domain=domain)
    return result


@router.get("/monitoring/{asset_id}", response_model=MonitoringStatus)
def monitoring_status_endpoint(
    asset_id: UUID,
    db: Session = Depends(get_db_session),
    actor: tuple[str, str] = Depends(require_api_key),
    settings: Settings = Depends(get_settings),
) -> MonitoringStatus:
    return _run_monitoring_status(db=db, asset_id=asset_id, actor=actor, settings=settings)


@router.post("/monitoring/status", response_model=MonitoringStatus)
def monitoring_status_contract_endpoint(
    request: AssetActionRequest,
    db: Session = Depends(get_db_session),
    actor: tuple[str, str] = Depends(require_api_key),
    settings: Settings = Depends(get_settings),
) -> MonitoringStatus:
    return _run_monitoring_status(db=db, asset_id=request.asset_id, actor=actor, settings=settings)


def _run_monitoring_status(
    *,
    db: Session,
    asset_id: UUID,
    actor: tuple[str, str],
    settings: Settings,
) -> MonitoringStatus:
    asset, _domain = _get_authorized_asset_for_action(db, asset_id, actor, "monitoring.status")
    logger.info("monitoring_status_requested", asset_id=str(asset_id))
    status = monitoring_status_from_state(get_or_create_monitoring_state(db, asset))
    return with_monitoring_scheduler_status(status, settings)


@router.post("/monitoring/{asset_id}/enable", response_model=MonitoringStatus)
def enable_monitoring_endpoint(
    asset_id: UUID,
    db: Session = Depends(get_db_session),
    actor: tuple[str, str] = Depends(require_api_key),
    settings: Settings = Depends(get_settings),
) -> MonitoringStatus:
    asset, _ = _get_authorized_asset_for_action(db, asset_id, actor, "monitoring.enable")
    status = set_monitoring_enabled(db, asset=asset, enabled=True, actor_type=actor[0], actor_id=actor[1])
    return with_monitoring_scheduler_status(status, settings)


@router.post("/monitoring/{asset_id}/disable", response_model=MonitoringStatus)
def disable_monitoring_endpoint(
    asset_id: UUID,
    db: Session = Depends(get_db_session),
    actor: tuple[str, str] = Depends(require_api_key),
    settings: Settings = Depends(get_settings),
) -> MonitoringStatus:
    asset, _ = _get_authorized_asset_for_action(db, asset_id, actor, "monitoring.disable")
    status = set_monitoring_enabled(db, asset=asset, enabled=False, actor_type=actor[0], actor_id=actor[1])
    return with_monitoring_scheduler_status(status, settings)


def _check_rate_limit(actor: tuple[str, str], action: str, settings: Settings) -> None:
    try:
        rate_limiter.check(
            f"{actor[0]}:{actor[1]}:{action}",
            limit=settings.INTEL_RATE_LIMIT_PER_MINUTE,
        )
    except RateLimitExceededError as exc:
        raise ApiError(status_code=429, code="rate_limit_exceeded", message="Too many requests.") from exc


def _get_authorized_asset_for_action(
    db: Session,
    asset_id: UUID,
    actor: tuple[str, str],
    action: str,
):
    try:
        return get_authorized_domain_asset(db, asset_id)
    except ApiError as exc:
        write_audit_event(
            db,
            actor_type=actor[0],
            actor_id=actor[1],
            action=action,
            result="denied",
            object_type="asset",
            object_id=str(asset_id),
            meta={"reason": exc.code},
        )
        raise
