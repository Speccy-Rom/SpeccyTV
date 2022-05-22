from typing import Optional

from aioredis import Redis

redis: Optional[Redis] = None


async def get_redis() -> Redis:
    return redis
