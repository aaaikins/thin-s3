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

    async def set_leased_metadata(self, file_id: str, value: dict, ttl: int):
        """
        Creates two keys:
        1. upload:{file_id} -> The actual data (No TTL)
        2. lease:{file_id}  -> The trigger (Has TTL)
        """
        data_key = f"upload:{file_id}"
        lease_key = f"lease:{file_id}"
        
        # Store the heavy metadata
        await self.client.hset(data_key, mapping=value)
        # Store the trigger key with the expiration
        await self.client.set(lease_key, "active", ex=ttl)

redis_cache = RedisCache()