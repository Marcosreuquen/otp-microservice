from fastapi import APIRouter
from fastapi import status, Response
import time
import asyncio
from sqlalchemy import text, select
from redis.asyncio import Redis

from config import settings
from app.models.db import db
from app.lib.cache import redis_client
from app.utils.logger import Logger
from app.schemas.schemas import HealthResponse



router = APIRouter(prefix="/health", tags=["health"])


async def _check_redis() -> dict:
    start = time.perf_counter()
    try:
        # Try a ping - redis_client is an async Redis instance
        pong = await redis_client.ping()
        ok = bool(pong)
    except Exception as e:
        Logger.warning(f"Redis health check failed: {e}")
        # If the primary REDIS_URL fails, optionally try an explicit fallback URL
        ok = False
        fallback = getattr(settings, "REDIS_FALLBACK", "")
        if fallback:
            try:
                tmp = Redis.from_url(fallback, decode_responses=True)
                try:
                    pong = await tmp.ping()
                    ok = bool(pong)
                finally:
                    try:
                        await tmp.close()
                    except Exception:
                        pass
            except Exception:
                ok = False
    latency = (time.perf_counter() - start) * 1000.0
    return {"ok": ok, "latency_ms": round(latency, 2)}


def _check_db_sync() -> dict:
    start = time.perf_counter()
    try:
        # Use a very small work: open a connection and execute a lightweight query
        with db.session() as session:
            # use select(1) to avoid SQLAlchemy textual SQL warnings
            session.exec(select(1))
        ok = True
    except Exception as e:
        Logger.warning(f"DB health check failed: {e}")
        ok = False
    latency = (time.perf_counter() - start) * 1000.0
    return {"ok": ok, "latency_ms": round(latency, 2)}


@router.get("/", status_code=status.HTTP_200_OK, response_model=HealthResponse)
async def health(response: Response):
    # Run checks concurrently
    redis_task = asyncio.create_task(_check_redis())
    # Run database check in a thread because it uses sync DB session
    db_task = asyncio.to_thread(_check_db_sync)

    # gather
    res_redis, res_db = await asyncio.gather(redis_task, db_task)

    overall_ok = res_redis.get("ok") and res_db.get("ok")
    status_code = status.HTTP_200_OK if overall_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    response.status_code = status_code

    return {
        "ok": overall_ok,
        "services": {
            "redis": res_redis,
            "db": res_db,
        },
    }
