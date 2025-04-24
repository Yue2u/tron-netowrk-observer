from redis.asyncio import from_url as aioredis_from_url
from redis.asyncio.client import Redis

from settings.redis import get_redis_settings

redis = aioredis_from_url(
    get_redis_settings().REDIS_URL, decode_responses=False
)


# Has to be overriden in fastapi lifespan
def get_redis() -> Redis:
    raise NotImplementedError()
