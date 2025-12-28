from functools import cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: Literal["dev", "prod"] = "dev"
    storage_base_path: str = "audio"
    redis_url: str

    s3_bucket_name: str | None = None
    s3_region_name: str | None = None
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        extra="forbid",
    )

    @model_validator(mode="after")
    def validate_prod_requirements(self):
        if self.env == "prod":
            required = [
                self.s3_bucket_name,
                self.s3_region_name,
                self.s3_access_key_id,
                self.s3_secret_access_key,
            ]
            if not all(required):
                raise ValueError("Missing required S3 configuration for production")
        return self

@cache
def get_settings() -> Settings:
    return Settings()
