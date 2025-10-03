from unittest.mock import AsyncMock, MagicMock
import asyncio


def test_redis_incr_and_setex():
    fake_redis = MagicMock()
    fake_redis.incr = AsyncMock(return_value=1)
    fake_redis.expire = AsyncMock(return_value=True)
    fake_redis.setex = AsyncMock(return_value=True)

    async def _use_redis():
        r = fake_redis
        val = await r.incr("rate:key")
        assert val == 1
        await r.expire("rate:key", 60)
        await r.setex("otp:key", 120, "123456")

    asyncio.run(_use_redis())

    fake_redis.incr.assert_called_once()
    fake_redis.setex.assert_called_once()
