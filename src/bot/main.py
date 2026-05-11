import asyncio

from aiogram import Bot, Dispatcher

from src.bot.handlers import router
from src.core.config import get_settings
from src.core.logging import configure_logging


async def main() -> None:
    settings = get_settings()
    configure_logging(settings)
    bot = Bot(token=settings.BOT_TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
