"""Telegram keyboards for SecPilot Defense."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


MENU_STATUS = "📊 Status"
MENU_ASSETS = "📁 Assetlar"
MENU_ADD_ASSET = "➕ Asset qo‘shish"
MENU_CHECK_ASSET = "🔎 Asset tekshirish"
MENU_DNS_AUDIT = "🌐 DNS Audit"
MENU_SSL_AUDIT = "🔐 SSL Audit"
MENU_SUBDOMAINS = "🔎 Subdomainlar"
MENU_MONITORING = "📡 Monitoring"
MENU_DELETE_ASSET = "🗑 Asset o‘chirish"
MENU_REPORTS = "📄 Hisobot"
MENU_SETTINGS = "⚙️ Sozlamalar"
MENU_HELP = "ℹ️ Yordam"

MENU_BUTTONS = [
    MENU_STATUS,
    MENU_ASSETS,
    MENU_ADD_ASSET,
    MENU_CHECK_ASSET,
    MENU_DNS_AUDIT,
    MENU_SSL_AUDIT,
    MENU_SUBDOMAINS,
    MENU_MONITORING,
    MENU_DELETE_ASSET,
    MENU_REPORTS,
    MENU_SETTINGS,
    MENU_HELP,
]


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MENU_STATUS), KeyboardButton(text=MENU_ASSETS)],
            [KeyboardButton(text=MENU_ADD_ASSET), KeyboardButton(text=MENU_CHECK_ASSET)],
            [KeyboardButton(text=MENU_DNS_AUDIT), KeyboardButton(text=MENU_SSL_AUDIT)],
            [KeyboardButton(text=MENU_SUBDOMAINS), KeyboardButton(text=MENU_MONITORING)],
            [KeyboardButton(text=MENU_DELETE_ASSET), KeyboardButton(text=MENU_REPORTS)],
            [KeyboardButton(text=MENU_SETTINGS), KeyboardButton(text=MENU_HELP)],
        ],
        resize_keyboard=True,
        input_field_placeholder="SecPilot buyrug‘ini tanlang",
    )


def asset_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Domain", callback_data="asset_type:domain"),
                InlineKeyboardButton(text="IP", callback_data="asset_type:ip"),
            ],
            [
                InlineKeyboardButton(text="CIDR", callback_data="asset_type:cidr"),
                InlineKeyboardButton(text="URL", callback_data="asset_type:url"),
            ],
        ]
    )


def asset_delete_keyboard(assets: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    return asset_action_keyboard("delete_asset", assets)


def asset_action_keyboard(action: str, assets: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{asset_id[:8]} · {value}", callback_data=f"{action}:{asset_id}")]
            for asset_id, value in assets
        ]
    )


def confirm_delete_keyboard(asset_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Ha, o‘chirish", callback_data=f"confirm_delete:{asset_id}"),
                InlineKeyboardButton(text="Bekor qilish", callback_data="cancel_delete"),
            ]
        ]
    )


def monitoring_action_keyboard(asset_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Yoqish", callback_data=f"monitoring_enable:{asset_id}"),
                InlineKeyboardButton(text="O‘chirish", callback_data=f"monitoring_disable:{asset_id}"),
            ]
        ]
    )
