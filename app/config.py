from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Awesome API"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0


settings = Settings()
