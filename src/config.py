from functools import cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    redis_url: str

    model_config = SettingsConfigDict(env_file=".env")


@cache
def get_settings():
    return Settings()
