from src.bot.keyboards import MENU_BUTTONS, asset_type_keyboard, main_menu_keyboard


def test_main_menu_keyboard_contains_expected_uzbek_buttons() -> None:
    keyboard = main_menu_keyboard()
    labels = [button.text for row in keyboard.keyboard for button in row]

    assert labels == MENU_BUTTONS
    assert "📊 Status" in labels
    assert "➕ Asset qo‘shish" in labels
    assert "ℹ️ Yordam" in labels


def test_asset_type_keyboard_uses_safe_asset_types() -> None:
    keyboard = asset_type_keyboard()
    callback_data = [button.callback_data for row in keyboard.inline_keyboard for button in row]

    assert callback_data == ["asset_type:domain", "asset_type:ip", "asset_type:cidr", "asset_type:url"]
