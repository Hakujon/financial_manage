import json
from typing import Annotated
from redis.asyncio import Redis
from fastapi import Depends
from src.finances.schemas import ResponseExpense
from src.exceptions.exceptions import CacheExcpeption


class CacheClient:
    def __init__(self, redis: Redis, ttl_seconds: int | None = None):
        self.redis = redis
        self.ttl = ttl_seconds if ttl_seconds else None
        self.prefix = "expense"

    def _make_key(self, id_: int) -> str:
        return f"{self.prefix}:{id_}"

    async def get_many_expenses(self, ids: list[int]) -> list[ResponseExpense]:
        keys = [self._make_key(id_) for id_ in ids]
        try:
            raw_values = await self.redis.mget(keys=keys)
        except Exception as e:
            raise CacheExcpeption(f"Cache exception: {e}") from e
        results = []
        for raw in raw_values:
            if raw:
                expense_dict = json.loads(raw)
                print(type(expense_dict))
                results.append(ResponseExpense(**expense_dict))

        return results

    async def set_many_expenses(self, expenses: list[ResponseExpense]) -> None:
        try:
            pipe = self.redis.pipeline()
            for expense in expenses:
                key = self._make_key(expense.id)
                value = expense.model_dump_json()
                pipe.set(key, value, ex=self.ttl)

            await pipe.execute()
        except Exception as e:
            raise CacheExcpeption(f"Cache exception: {e}") from e

    async def invalidate(self, ids: list[int]) -> None:
        keys = [self._make_key(id_) for id_ in ids]
        try:
            if keys:
                await self.redis.delete(*keys)
        except Exception as e:
            raise CacheExcpeption(f"Cache exception: {e}") from e


redis = Redis(host="redis_app", port=6379,
              decode_responses=True)
cache_client: CacheClient | None = None


async def get_cache() -> CacheClient:
    global redis, cache_client
    if cache_client is None:
        cache_client = CacheClient(redis=redis)

    return cache_client

CACHE = Annotated[CacheClient, Depends(get_cache)]
