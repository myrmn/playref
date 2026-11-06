"""Rate limiting and caching with Redis and in-memory fallback."""

import time
from collections import defaultdict

import redis.asyncio as aioredis

from backend.app.config import settings
from backend.app.logger import logger

_memory_rate_limit: dict[str, list[float]] = defaultdict(list)
_redis_client = None
_redis_attempted = False


async def get_redis():
    global _redis_client, _redis_attempted
    if _redis_attempted:
        return _redis_client

    _redis_attempted = True
    if settings.redis_url:
        try:
            r = aioredis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=1.0)
            await r.ping()
            logger.info(f"Connected to Redis at {settings.redis_url}")
            _redis_client = r
            return _redis_client
        except Exception:
            logger.info("Redis not available; using in-memory rate limiting")
    return None


class RateLimiter:
    """Rate limiter with Redis support and in-memory fallback."""

    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute

    async def is_allowed(self, identifier: str) -> bool:
        """Check whether the request from identifier (IP/session) is permitted."""
        redis_conn = await get_redis()
        now = time.time()

        if redis_conn:
            try:
                key = f"rate_limit:{identifier}"
                count = await redis_conn.incr(key)
                if count == 1:
                    await redis_conn.expire(key, 60)
                return count <= self.rpm
            except Exception:
                pass

        # In-memory sliding window fallback
        timestamps = _memory_rate_limit[identifier]
        # Keep only timestamps within the last 60 seconds
        valid = [t for t in timestamps if now - t < 60.0]
        valid.append(now)
        _memory_rate_limit[identifier] = valid
        return len(valid) <= self.rpm


rate_limiter = RateLimiter(requests_per_minute=60)
