import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from src.dialogs.router import router as dialogs_router
from src.handlers.main_handler import router as start_router
from src.core.config import settings
from src.redis_storage import redis_storage
from aiogram_dialog import setup_dialogs


BOT_TOKEN = settings.BOT_TOKEN

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=redis_storage)
async def main() -> None:
    setup_dialogs(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    dp.include_router(start_router)
    dp.include_router(dialogs_router)
    asyncio.run(main())
