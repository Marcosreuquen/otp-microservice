from typing import AsyncGenerator
from redis.asyncio import Redis
from config import settings

# Singleton Redis client for the app
redis_client: Redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis() -> Redis:
    """FastAPI dependency that returns the global Redis client."""
    return redis_client


async def close_redis() -> None:
    try:
        await redis_client.close()
    except Exception:
        pass
