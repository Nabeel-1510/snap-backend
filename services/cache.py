import json
import redis.asyncio as aioredis
from config import settings

_redis = aioredis.from_url(settings.redis_url, decode_responses=True)


async def get_cached(key: str):
    data = await _redis.get(key)
    if data:
        return json.loads(data)
    return None


async def set_cached(key: str, value, ttl: int = 300):
    await _redis.set(key, json.dumps(value, default=str), ex=ttl)


async def delete_cached(key: str):
    await _redis.delete(key)
