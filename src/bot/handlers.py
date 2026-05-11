from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.auth import is_admin
from src.core.config import get_settings


router = Router(name="secpilot_bot")


@router.message(Command("start"))
async def start_command(message: Message) -> None:
    settings = get_settings()
    if not is_admin(message, settings):
        await message.answer("Access denied.")
        return
    await message.answer("SecPilot Defense online. Defensive and authorized use only.")


@router.message(Command("status"))
async def status_command(message: Message) -> None:
    settings = get_settings()
    if not is_admin(message, settings):
        await message.answer("Access denied.")
        return
    await message.answer("Status: API configured, bot running, worker queue enabled.")
