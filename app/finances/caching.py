import json
from redis.asyncio import Redis
from app.finances.schemas import ResponseExpense


class CacheClient:
    def __init__(self, redis: Redis, ttl_seconds: int = 300):
        self.redis = redis
        self.ttl = ttl_seconds
        self.prefix = "expense"

    def _make_key(self, id_: int) -> str:
        return f"{self.prefix}:{id_}"

    async def get_many_exp(self, ids: list[int]) -> list[ResponseExpense]:
        keys = [self._make_key(id_) for id_ in ids]

        raw_values = await self.redis.mget(keys=keys)

        results = []
        for raw in raw_values:
            if raw:
                data = json.loads(raw)
                results.append(ResponseExpense(**data))

        return results

    async def set_many(self, expenses: list[ResponseExpense]) -> None:
        pipe = self.redis.pipeline()
        for expense in expenses:
            key = self._make_key(expense.id)
            value = expense.model_dump_json()
            pipe.set(key, value, ex=self.ttl)

        await pipe.execute()

    async def invalidate(self, ids: list[int]) -> None:
        keys = [self._make_key(id_) for id_ in ids]

        if keys:
            await self.redis.delete(*keys)


redis = Redis(host="redis_app", port=6379,
              decode_responses=True)
cache_client: CacheClient | None = None


async def get_cache() -> CacheClient:
    global redis, cache_client
    if cache_client is None:
        cache_client = CacheClient(redis=redis)

    return cache_client
