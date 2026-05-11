from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api.main import app
from src.core.config import Settings, get_settings
from src.db.models import Asset, AuditLog
from src.db.session import get_db_session
from src.schemas.dns import DnsAuditResult
from src.schemas.monitoring import MonitoringStatus
from src.schemas.ssl import SslAuditResult
from src.schemas.subdomains import SubdomainDiscoveryResult


def _settings() -> Settings:
    return Settings(API_SECRET_KEY="test-api-key")


def _headers() -> dict[str, str]:
    return {"X-API-Key": "test-api-key"}


def _add_asset(db_session: Session, asset_type: str = "domain", status: str = "active") -> Asset:
    asset = Asset(
        asset_type=asset_type,
        value="example.com" if asset_type == "domain" else "https://example.com",
        normalized_value="example.com" if asset_type == "domain" else "https://example.com",
        status=status,
    )
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    return asset


def test_dns_audit_requires_active_whitelisted_domain_asset(
    db_session: Session,
    monkeypatch,
) -> None:
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_settings] = _settings
    asset = _add_asset(db_session)

    def fake_collect(domain: str, timeout: float) -> DnsAuditResult:
        assert domain == "example.com"
        assert timeout > 0
        return DnsAuditResult(domain=domain, a_records=["1.1.1.1"], spf=True, dmarc=True, asn="AS13335")

    monkeypatch.setattr("src.api.routes.intel.collect_dns_audit", fake_collect)
    response = TestClient(app).get(f"/api/v1/dns/{asset.id}", headers=_headers())

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["domain"] == "example.com"
    assert response.json()["a_records"] == ["1.1.1.1"]
    assert db_session.query(AuditLog).filter(AuditLog.action == "dns.audit").count() == 1


def test_dns_audit_contract_endpoint_accepts_asset_request(
    db_session: Session,
    monkeypatch,
) -> None:
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_settings] = _settings
    asset = _add_asset(db_session)

    def fake_collect(domain: str, timeout: float) -> DnsAuditResult:
        return DnsAuditResult(domain=domain, a_records=["1.1.1.1"], spf=True, dmarc=True)

    monkeypatch.setattr("src.api.routes.intel.collect_dns_audit", fake_collect)
    response = TestClient(app).post(
        "/api/v1/dns/audit",
        headers=_headers(),
        json={"asset_id": str(asset.id)},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["domain"] == "example.com"


def test_dns_audit_rejects_non_domain_assets(db_session: Session) -> None:
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_settings] = _settings
    asset = _add_asset(db_session, asset_type="ip")

    response = TestClient(app).get(f"/api/v1/dns/{asset.id}", headers=_headers())

    app.dependency_overrides.clear()
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "asset_type_not_allowed"


def test_ssl_audit_returns_certificate_summary(db_session: Session, monkeypatch) -> None:
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_settings] = _settings
    asset = _add_asset(db_session)

    def fake_collect(domain: str, timeout: float) -> SslAuditResult:
        return SslAuditResult(
            domain=domain,
            issuer="Let's Encrypt",
            expires_at="2026-07-02T00:00:00+00:00",
            days_remaining=52,
            tls_version="TLSv1.3",
            https_available=True,
            hsts=True,
        )

    monkeypatch.setattr("src.api.routes.intel.collect_ssl_audit", fake_collect)
    response = TestClient(app).get(f"/api/v1/ssl/{asset.id}", headers=_headers())

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["issuer"] == "Let's Encrypt"


def test_subdomain_discovery_uses_passive_service_only(db_session: Session, monkeypatch) -> None:
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_settings] = _settings
    asset = _add_asset(db_session)

    def fake_collect(domain: str, timeout: float) -> SubdomainDiscoveryResult:
        return SubdomainDiscoveryResult(domain=domain, subdomains=[{"name": "www.example.com", "first_seen": None}])

    monkeypatch.setattr("src.api.routes.intel.collect_passive_subdomains", fake_collect)
    response = TestClient(app).get(f"/api/v1/subdomains/{asset.id}", headers=_headers())

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["subdomains"][0]["name"] == "www.example.com"


def test_monitoring_enable_disable_and_status(db_session: Session) -> None:
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_settings] = _settings
    asset = _add_asset(db_session)
    client = TestClient(app)

    enable_response = client.post(f"/api/v1/monitoring/{asset.id}/enable", headers=_headers())
    status_response = client.get(f"/api/v1/monitoring/{asset.id}", headers=_headers())
    disable_response = client.post(f"/api/v1/monitoring/{asset.id}/disable", headers=_headers())

    app.dependency_overrides.clear()
    assert enable_response.status_code == 200
    assert MonitoringStatus(**status_response.json()).enabled is True
    assert "scheduler" in status_response.json()
    assert disable_response.status_code == 200
    assert disable_response.json()["enabled"] is False


def test_monitoring_status_contract_endpoint_returns_scheduler_status(db_session: Session) -> None:
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_settings] = _settings
    asset = _add_asset(db_session)

    response = TestClient(app).post(
        "/api/v1/monitoring/status",
        headers=_headers(),
        json={"asset_id": str(asset.id)},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["asset_id"] == str(asset.id)
    assert response.json()["scheduler"]["backend"] == "celery"


def test_intel_endpoints_reject_unknown_asset(db_session: Session) -> None:
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_settings] = _settings

    response = TestClient(app).get(f"/api/v1/dns/{uuid4()}", headers=_headers())

    app.dependency_overrides.clear()
    assert response.status_code == 404
