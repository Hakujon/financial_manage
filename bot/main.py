import asyncio
import httpx
from redis.asyncio import Redis

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.storage.redis import RedisStorage
from aiogram import F

from bot.router import router
from bot.config import settings

BOT_TOKEN: str = settings.BOT_TOKEN  # type: ignore

redis = Redis(host="localhost", port=6379)

storage = RedisStorage(redis=redis)
dp = Dispatcher(storage=storage)
bot = Bot(token=BOT_TOKEN)


@dp.message(CommandStart())
@dp.message(F.text.startswith("hello"))
async def sending_ping(message: Message) -> None:
    async with httpx.AsyncClient() as client:
        answer = await client.get("http://localhost:8000/ping")
        data = answer.json().get("message", "No response")
    await message.answer(f"Your API is talking {data}")


dp.include_router(router=router)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
