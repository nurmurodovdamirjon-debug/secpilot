from src.bot.api_client import BotAsset, HealthResult
from src.bot.services import format_asset_list, format_status_message, is_asset_whitelisted


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
