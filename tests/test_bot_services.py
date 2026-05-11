from src.bot.api_client import BotApiError, BotAsset, HealthResult
from src.bot.services import (
    format_api_error,
    format_asset_list,
    format_dns_report,
    format_monitoring_report,
    format_ssl_report,
    format_status_message,
    format_subdomain_report,
    is_asset_whitelisted,
)


def test_format_asset_list_handles_empty_state_in_uzbek() -> None:
    assert format_asset_list([]) == "Hozircha asset qo‘shilmagan."


def test_format_asset_list_includes_short_id_type_value_and_status() -> None:
    message = format_asset_list(
        [
            BotAsset(
                id="12345678-aaaa-bbbb-cccc-123456789abc",
                asset_type="domain",
                value="example.com",
                normalized_value="example.com",
                label="Main",
                status="active",
            )
        ]
    )

    assert "12345678" in message
    assert "domain" in message
    assert "example.com" in message
    assert "active" in message


def test_is_asset_whitelisted_matches_exact_and_cidr_assets() -> None:
    assets = [
        BotAsset(
            id="1",
            asset_type="domain",
            value="example.com",
            normalized_value="example.com",
            label=None,
            status="active",
        ),
        BotAsset(
            id="2",
            asset_type="cidr",
            value="192.0.2.0/24",
            normalized_value="192.0.2.0/24",
            label=None,
            status="active",
        ),
    ]

    assert is_asset_whitelisted(assets, "Example.COM") is True
    assert is_asset_whitelisted(assets, "192.0.2.42") is True
    assert is_asset_whitelisted(assets, "unknown.example") is False


def test_format_status_message_includes_bot_api_and_dependencies() -> None:
    message = format_status_message(
        bot_online=True,
        environment="development",
        live=HealthResult(ok=True, payload={"status": "ok"}),
        ready=HealthResult(
            ok=True,
            payload={"status": "ready", "dependencies": {"database": True, "redis": True}},
        ),
    )

    assert "Bot: online" in message
    assert "API: ishlayapti" in message
    assert "DB: ishlayapti" in message
    assert "Redis: ishlayapti" in message
    assert "Muhit: development" in message


def test_format_status_message_reads_not_ready_dependency_detail() -> None:
    message = format_status_message(
        bot_online=True,
        environment="production",
        live=HealthResult(ok=True, payload={"status": "ok"}),
        ready=HealthResult(
            ok=False,
            payload={"detail": {"status": "not_ready", "dependencies": {"database": False, "redis": True}}},
        ),
    )

    assert "DB: xatolik" in message
    assert "Redis: ishlayapti" in message


def test_format_dns_ssl_subdomain_and_monitoring_reports() -> None:
    dns_message = format_dns_report(
        {
            "domain": "example.com",
            "a_records": ["1.1.1.1"],
            "mx_records": ["mail.example.com"],
            "spf": True,
            "dmarc": False,
            "asn": "AS13335",
            "provider": "Cloudflare",
        }
    )
    ssl_message = format_ssl_report(
        {
            "domain": "example.com",
            "issuer": "Let's Encrypt",
            "days_remaining": 52,
            "tls_version": "TLSv1.3",
            "hsts": True,
        }
    )
    subdomain_message = format_subdomain_report(
        {"domain": "example.com", "subdomains": [{"name": "www.example.com", "first_seen": None}]}
    )
    monitoring_message = format_monitoring_report(
        {"enabled": True, "last_status": "ok", "last_check_at": None, "last_detail": None}
    )

    assert "DNS Audit" in dns_message
    assert "SPF: bor" in dns_message
    assert "SSL/TLS Audit" in ssl_message
    assert "52 kun" in ssl_message
    assert "www.example.com" in subdomain_message
    assert "Monitoring: yoqilgan" in monitoring_message


def test_format_api_error_reports_database_schema_not_ready() -> None:
    message = format_api_error(
        BotApiError(
            code="database_schema_not_ready",
            message="Required database schema is not ready.",
            status_code=503,
        )
    )

    assert "migration/schema" in message
    assert "Admin" in message
