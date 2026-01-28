import redis.asyncio as redis
from app.core.config import settings

class RedisCache:
    def __init__(self):
        self.client = redis.from_url(
            settings.redis_url, 
            decode_responses=True # Returns strings instead of bytes
        )

    async def set_metadata(self, key: str, value: dict, ttl: int = None):
        await self.client.hset(key, mapping=value)
        if ttl:
            await self.client.expire(key, ttl)

    async def get_metadata(self, key: str):
        return await self.client.hgetall(key)

redis_cache = RedisCache()