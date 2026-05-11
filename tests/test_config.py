import pytest

from src.core.config import Settings


def test_admin_ids_are_parsed_from_csv() -> None:
    settings = Settings(BOT_ADMIN_IDS="123, 456")

    assert settings.bot_admin_id_set == {123, 456}


def test_safety_defaults_require_manual_high_risk_actions() -> None:
    settings = Settings()

    assert settings.AUTO_BLOCK_ENABLED is False
    assert settings.POLICY_FAIL_CLOSED is True
    assert settings.API_BASE_URL == "http://api:8000"
    assert settings.API_CONNECT_TIMEOUT_SECONDS == 5
    assert settings.API_READ_TIMEOUT_SECONDS == 30


def test_production_rejects_container_unsafe_localhost_api_url() -> None:
    with pytest.raises(ValueError, match="API_BASE_URL"):
        Settings(
            APP_ENV="production",
            API_SECRET_KEY="api-secret",
            JWT_SECRET_KEY="jwt-secret",
            BOT_TOKEN="bot-token",
            BOT_ADMIN_IDS="123",
            API_BASE_URL="http://localhost:8000",
        )
