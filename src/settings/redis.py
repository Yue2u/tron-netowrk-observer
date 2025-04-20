from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    REDIS_URL: str


def get_redis_settings() -> RedisSettings:
    return RedisSettings()