from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    jwt_secret_key: str
    jwt_algorithm: str = 'HS256'
    jwt_expire_minutes: int = 30
    cors_origins: list[str] = ['http://localhost:9901']


@lru_cache
def get_settings() -> Settings:
    """
    Return the base settings for the app
    :return: settings
    """
    return Settings()
