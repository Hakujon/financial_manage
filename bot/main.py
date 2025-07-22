import asyncio
import httpx
from redis.asyncio import Redis

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram import F
from aiogram_dialog import setup_dialogs

from bot.router import router
from bot.dialog_router import router as dialog_router
from bot.config import settings
from bot.reply_keyboard import head_keyboard

BOT_TOKEN: str = settings.BOT_TOKEN  # type: ignore

redis = Redis(host="localhost", port=6379)

storage = RedisStorage(redis=redis,
                       key_builder=DefaultKeyBuilder(with_destiny=True))
dp = Dispatcher(storage=storage)
bot = Bot(token=BOT_TOKEN)


@dp.message(CommandStart())
@dp.message(F.text.startswith("hello"))
async def sending_ping(message: Message) -> None:
    async with httpx.AsyncClient() as client:
        answer = await client.get("http://localhost:8000/ping")
        data = answer.json().get("message", "No response")
    await message.answer(text=f"Your API is talking {data}",
                         reply_markup=head_keyboard)


dp.include_router(router=dialog_router)
dp.include_router(router=router)
setup_dialogs(dp)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
