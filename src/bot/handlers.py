"""aiogram handlers for SecPilot Defense Telegram UX."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.api_client import BotApiError, SecPilotApiClient
from src.bot.auth import is_admin, is_admin_user_id
from src.bot.keyboards import (
    MENU_ADD_ASSET,
    MENU_ASSETS,
    MENU_CHECK_ASSET,
    MENU_DELETE_ASSET,
    MENU_HELP,
    MENU_REPORTS,
    MENU_SETTINGS,
    MENU_STATUS,
    asset_delete_keyboard,
    asset_type_keyboard,
    confirm_delete_keyboard,
    main_menu_keyboard,
)
from src.bot.services import format_api_error, format_asset_list, format_status_message, is_asset_whitelisted
from src.bot.states import AddAssetStates, CheckAssetStates
from src.core.config import Settings, get_settings


router = Router(name="secpilot_bot")


def build_api_client(settings: Settings) -> SecPilotApiClient:
    return SecPilotApiClient(base_url=settings.API_BASE_URL, api_key=settings.API_SECRET_KEY)


async def _require_admin(message: Message, settings: Settings) -> bool:
    if is_admin(message, settings):
        return True
    await message.answer("Kirish rad etildi. Bu bot faqat ruxsat berilgan adminlar uchun.")
    return False


async def _require_admin_callback(callback: CallbackQuery, settings: Settings) -> bool:
    user_id = callback.from_user.id if callback.from_user else None
    if is_admin_user_id(user_id, settings):
        return True
    await callback.answer("Kirish rad etildi.", show_alert=True)
    return False


@router.message(Command("start"))
async def start_command(message: Message) -> None:
    settings = get_settings()
    if not await _require_admin(message, settings):
        return
    await message.answer(
        "Assalomu alaykum!\n\n"
        "SecPilot Defense — ruxsat berilgan assetlarni whitelistda yuritish va xavfsizlik "
        "jarayonlarini nazorat qilish uchun Telegram-first himoya yordamchisi.\n\n"
        "Quyidagi tugmalar orqali authorized assetlarni boshqarishingiz mumkin.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
@router.message(F.text == MENU_HELP)
async def help_command(message: Message) -> None:
    settings = get_settings()
    if not await _require_admin(message, settings):
        return
    await message.answer(
        "ℹ️ Yordam\n\n"
        "Komandalar:\n"
        "/start — bosh menyu\n"
        "/status — tizim holati\n"
        "/assets — whitelist assetlar\n"
        "/add_asset — asset qo‘shish\n"
        "/check_asset — asset whitelistda bor-yo‘qligini tekshirish\n"
        "/delete_asset — assetni soft delete qilish\n"
        "/help — yordam\n\n"
        "Eslatma: SecPilot Defensive-only siyosatda ishlaydi. Malware, phishing, exploit, "
        "hack-back, credential theft va unauthorized scanning taqiqlangan.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("status"))
@router.message(F.text == MENU_STATUS)
async def status_command(message: Message) -> None:
    settings = get_settings()
    if not await _require_admin(message, settings):
        return
    client = build_api_client(settings)
    try:
        live = await client.live()
        ready = await client.ready()
    finally:
        await client.close()
    await message.answer(
        format_status_message(bot_online=True, environment=settings.APP_ENV, live=live, ready=ready),
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("assets"))
@router.message(F.text == MENU_ASSETS)
async def assets_command(message: Message) -> None:
    settings = get_settings()
    if not await _require_admin(message, settings):
        return
    client = build_api_client(settings)
    try:
        assets = await client.list_assets()
        await message.answer(format_asset_list(assets), reply_markup=main_menu_keyboard())
    except BotApiError as exc:
        await message.answer(format_api_error(exc), reply_markup=main_menu_keyboard())
    finally:
        await client.close()


@router.message(Command("add_asset"))
@router.message(F.text == MENU_ADD_ASSET)
async def add_asset_command(message: Message, state: FSMContext) -> None:
    settings = get_settings()
    if not await _require_admin(message, settings):
        return
    await state.set_state(AddAssetStates.waiting_for_type)
    await message.answer("Asset turini tanlang: domain, ip, cidr, url", reply_markup=asset_type_keyboard())


@router.callback_query(F.data.startswith("asset_type:"))
async def asset_type_callback(callback: CallbackQuery, state: FSMContext) -> None:
    settings = get_settings()
    if not await _require_admin_callback(callback, settings):
        return
    asset_type = (callback.data or "").split(":", 1)[1]
    await state.update_data(asset_type=asset_type)
    await state.set_state(AddAssetStates.waiting_for_value)
    if callback.message is not None:
        await callback.message.answer(f"Qiymatni yuboring. Masalan: {_example_for_asset_type(asset_type)}")
    await callback.answer()


@router.message(AddAssetStates.waiting_for_value)
async def add_asset_value(message: Message, state: FSMContext) -> None:
    settings = get_settings()
    if not await _require_admin(message, settings):
        return
    state_data = await state.get_data()
    asset_type = str(state_data.get("asset_type", "domain"))
    client = build_api_client(settings)
    try:
        asset = await client.create_asset(asset_type=asset_type, value=(message.text or "").strip())
        await message.answer(
            "✅ Asset whitelistga qo‘shildi\n"
            f"Turi: {asset.asset_type}\n"
            f"Qiymat: {asset.value}\n"
            f"Normal ko‘rinish: {asset.normalized_value}",
            reply_markup=main_menu_keyboard(),
        )
    except BotApiError as exc:
        await message.answer(format_api_error(exc), reply_markup=main_menu_keyboard())
    finally:
        await client.close()
        await state.clear()


@router.message(Command("check_asset"))
@router.message(F.text == MENU_CHECK_ASSET)
async def check_asset_command(message: Message, state: FSMContext) -> None:
    settings = get_settings()
    if not await _require_admin(message, settings):
        return
    await state.set_state(CheckAssetStates.waiting_for_value)
    await message.answer("Tekshirish uchun asset qiymatini yuboring. Masalan: example.com")


@router.message(CheckAssetStates.waiting_for_value)
async def check_asset_value(message: Message, state: FSMContext) -> None:
    settings = get_settings()
    if not await _require_admin(message, settings):
        return
    client = build_api_client(settings)
    try:
        assets = await client.list_assets()
        if is_asset_whitelisted(assets, message.text or ""):
            await message.answer("✅ Ruxsat berilgan asset", reply_markup=main_menu_keyboard())
        else:
            await message.answer("❌ Whitelistda yo‘q", reply_markup=main_menu_keyboard())
    except BotApiError as exc:
        await message.answer(format_api_error(exc), reply_markup=main_menu_keyboard())
    finally:
        await client.close()
        await state.clear()


@router.message(Command("delete_asset"))
@router.message(F.text == MENU_DELETE_ASSET)
async def delete_asset_command(message: Message) -> None:
    settings = get_settings()
    if not await _require_admin(message, settings):
        return
    client = build_api_client(settings)
    try:
        assets = [asset for asset in await client.list_assets() if asset.status == "active"]
        if not assets:
            await message.answer("Hozircha asset qo‘shilmagan.", reply_markup=main_menu_keyboard())
            return
        await message.answer(
            "O‘chirish uchun assetni tanlang:",
            reply_markup=asset_delete_keyboard([(asset.id, asset.value) for asset in assets]),
        )
    except BotApiError as exc:
        await message.answer(format_api_error(exc), reply_markup=main_menu_keyboard())
    finally:
        await client.close()


@router.callback_query(F.data.startswith("delete_asset:"))
async def delete_asset_selected(callback: CallbackQuery) -> None:
    settings = get_settings()
    if not await _require_admin_callback(callback, settings):
        return
    asset_id = (callback.data or "").split(":", 1)[1]
    if callback.message is not None:
        await callback.message.answer("Rostdan o‘chirasizmi?", reply_markup=confirm_delete_keyboard(asset_id))
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete:"))
async def confirm_delete_asset(callback: CallbackQuery) -> None:
    settings = get_settings()
    if not await _require_admin_callback(callback, settings):
        return
    asset_id = (callback.data or "").split(":", 1)[1]
    client = build_api_client(settings)
    try:
        await client.delete_asset(asset_id)
        if callback.message is not None:
            await callback.message.answer("✅ Asset whitelistdan o‘chirildi.", reply_markup=main_menu_keyboard())
    except BotApiError as exc:
        if callback.message is not None:
            await callback.message.answer(format_api_error(exc), reply_markup=main_menu_keyboard())
    finally:
        await client.close()
    await callback.answer()


@router.callback_query(F.data == "cancel_delete")
async def cancel_delete_asset(callback: CallbackQuery) -> None:
    await callback.answer("Bekor qilindi.")
    if callback.message is not None:
        await callback.message.answer("O‘chirish bekor qilindi.", reply_markup=main_menu_keyboard())


@router.message(F.text == MENU_REPORTS)
async def reports_placeholder(message: Message) -> None:
    settings = get_settings()
    if not await _require_admin(message, settings):
        return
    await message.answer("📄 Hisobot moduli keyingi bosqichda qo‘shiladi.", reply_markup=main_menu_keyboard())


@router.message(F.text == MENU_SETTINGS)
async def settings_placeholder(message: Message) -> None:
    settings = get_settings()
    if not await _require_admin(message, settings):
        return
    await message.answer("⚙️ Sozlamalar moduli keyingi bosqichda qo‘shiladi.", reply_markup=main_menu_keyboard())


def _example_for_asset_type(asset_type: str) -> str:
    examples = {
        "domain": "example.com",
        "ip": "192.0.2.10",
        "cidr": "192.0.2.0/24",
        "url": "https://example.com",
    }
    return examples.get(asset_type, "example.com")
