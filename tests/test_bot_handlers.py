from types import SimpleNamespace

import pytest

from src.bot.api_client import BotAsset
from src.bot.handlers import add_asset_command, add_asset_value, check_asset_value, delete_asset_command, help_command, start_command
from src.bot.states import AddAssetStates
from src.core.config import Settings


class FakeMessage:
    def __init__(self, user_id: int, text: str = "") -> None:
        self.from_user = SimpleNamespace(id=user_id)
        self.text = text
        self.answers: list[tuple[str, object | None]] = []

    async def answer(self, text: str, reply_markup: object | None = None) -> None:
        self.answers.append((text, reply_markup))


class FakeState:
    def __init__(self, data: dict[str, object] | None = None) -> None:
        self.data = data or {}
        self.state: object | None = None
        self.cleared = False

    async def set_state(self, state: object) -> None:
        self.state = state

    async def update_data(self, **kwargs: object) -> None:
        self.data.update(kwargs)

    async def get_data(self) -> dict[str, object]:
        return self.data

    async def clear(self) -> None:
        self.cleared = True


class FakeApiClient:
    def __init__(self) -> None:
        self.created: tuple[str, str] | None = None
        self.deleted: str | None = None
        self.closed = False
        self.assets = [
            BotAsset(
                id="12345678-aaaa-bbbb-cccc-123456789abc",
                asset_type="domain",
                value="example.com",
                normalized_value="example.com",
                label=None,
                status="active",
            )
        ]

    async def list_assets(self) -> list[BotAsset]:
        return self.assets

    async def create_asset(self, *, asset_type: str, value: str) -> BotAsset:
        self.created = (asset_type, value)
        return BotAsset(
            id="asset-1",
            asset_type=asset_type,
            value=value,
            normalized_value=value.lower(),
            label=None,
            status="active",
        )

    async def delete_asset(self, asset_id: str) -> None:
        self.deleted = asset_id

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_start_command_answers_in_uzbek_with_menu(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.bot.handlers.get_settings", lambda: Settings(BOT_ADMIN_IDS="123"))
    message = FakeMessage(user_id=123)

    await start_command(message)

    text, reply_markup = message.answers[0]
    assert "Assalomu alaykum" in text
    assert "SecPilot Defense" in text
    assert reply_markup is not None


@pytest.mark.asyncio
async def test_start_command_denies_non_admin_in_uzbek(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.bot.handlers.get_settings", lambda: Settings(BOT_ADMIN_IDS="123"))
    message = FakeMessage(user_id=999)

    await start_command(message)

    assert message.answers[0][0] == "Kirish rad etildi. Bu bot faqat ruxsat berilgan adminlar uchun."


@pytest.mark.asyncio
async def test_help_command_lists_commands_and_defensive_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.bot.handlers.get_settings", lambda: Settings(BOT_ADMIN_IDS="123"))
    message = FakeMessage(user_id=123)

    await help_command(message)

    text = message.answers[0][0]
    assert "/assets" in text
    assert "/add_asset" in text
    assert "Defensive-only" in text


@pytest.mark.asyncio
async def test_add_asset_command_starts_fsm_and_value_creates_asset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.bot.handlers.get_settings", lambda: Settings(BOT_ADMIN_IDS="123"))
    api_client = FakeApiClient()
    monkeypatch.setattr("src.bot.handlers.build_api_client", lambda _: api_client)
    state = FakeState({"asset_type": "domain"})

    await add_asset_command(FakeMessage(user_id=123), state)  # type: ignore[arg-type]
    assert state.state == AddAssetStates.waiting_for_type

    message = FakeMessage(user_id=123, text="Example.COM")
    await add_asset_value(message, state)  # type: ignore[arg-type]

    assert api_client.created == ("domain", "Example.COM")
    assert state.cleared is True
    assert "✅ Asset whitelistga qo‘shildi" in message.answers[0][0]


@pytest.mark.asyncio
async def test_check_asset_value_uses_api_assets_without_scanning(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.bot.handlers.get_settings", lambda: Settings(BOT_ADMIN_IDS="123"))
    monkeypatch.setattr("src.bot.handlers.build_api_client", lambda _: FakeApiClient())
    state = FakeState()
    message = FakeMessage(user_id=123, text="example.com")

    await check_asset_value(message, state)  # type: ignore[arg-type]

    assert message.answers[0][0] == "✅ Ruxsat berilgan asset"
    assert state.cleared is True


@pytest.mark.asyncio
async def test_delete_asset_command_lists_inline_asset_buttons(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.bot.handlers.get_settings", lambda: Settings(BOT_ADMIN_IDS="123"))
    monkeypatch.setattr("src.bot.handlers.build_api_client", lambda _: FakeApiClient())
    message = FakeMessage(user_id=123)

    await delete_asset_command(message)

    text, reply_markup = message.answers[0]
    assert text == "O‘chirish uchun assetni tanlang:"
    assert reply_markup.inline_keyboard[0][0].callback_data.startswith("delete_asset:")
