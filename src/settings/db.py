from pydantic_settings import BaseSettings


class DBSettings(BaseSettings):
    POSTGRES_URL: str


def get_db_settings() -> DBSettings:
    return DBSettings()