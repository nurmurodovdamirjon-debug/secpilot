from src.core.config import Settings


def test_admin_ids_are_parsed_from_csv() -> None:
    settings = Settings(BOT_ADMIN_IDS="123, 456")

    assert settings.bot_admin_id_set == {123, 456}


def test_safety_defaults_require_manual_high_risk_actions() -> None:
    settings = Settings()

    assert settings.AUTO_BLOCK_ENABLED is False
    assert settings.POLICY_FAIL_CLOSED is True
