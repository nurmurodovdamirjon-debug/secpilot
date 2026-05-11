from src.schemas.dns import DnsAuditResult
from src.schemas.subdomains import SubdomainDiscoveryResult
from src.services.defensive_intel import extract_domain_from_asset
from src.services.dns_audit import _detect_dmarc, _detect_spf
from src.services.monitoring import evaluate_monitoring_alert
from src.services.subdomains import _parse_crtsh_rows


def test_extract_domain_from_domain_and_url_assets() -> None:
    assert extract_domain_from_asset("domain", "Example.COM") == "example.com"
    assert extract_domain_from_asset("url", "https://Example.COM/admin") == "example.com"


def test_spf_and_dmarc_detection() -> None:
    assert _detect_spf(['"v=spf1 include:_spf.example.com -all"']) is True
    assert _detect_spf(["hello"]) is False
    assert _detect_dmarc(['"v=DMARC1; p=reject"']) is True


def test_crtsh_parser_deduplicates_subdomains() -> None:
    result = _parse_crtsh_rows(
        "example.com",
        [
            {"name_value": "www.example.com\napi.example.com", "entry_timestamp": "2026-05-11T00:00:00"},
            {"name_value": "*.api.example.com", "entry_timestamp": None},
        ],
    )

    assert result == SubdomainDiscoveryResult(
        domain="example.com",
        subdomains=[
            {"name": "api.example.com", "first_seen": "2026-05-11T00:00:00"},
            {"name": "www.example.com", "first_seen": "2026-05-11T00:00:00"},
        ],
        sources=["crt.sh"],
    )


def test_dns_schema_defaults_are_safe() -> None:
    result = DnsAuditResult(domain="example.com")

    assert result.a_records == []
    assert result.spf is False
    assert result.dmarc is False


def test_monitoring_alert_detects_ssl_dns_and_availability_changes() -> None:
    status, reasons = evaluate_monitoring_alert(
        previous_detail={"dns_a_records": ["1.1.1.1"]},
        current_detail={"dns_a_records": ["1.1.1.2"], "ssl_days_remaining": 7, "available": False},
    )

    assert status == "warning"
    assert reasons == ["ssl_expiring_soon", "dns_changed", "asset_unavailable"]
