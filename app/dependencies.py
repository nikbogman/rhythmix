import redis
from functools import cache
from app.config import Settings


@cache
def get_redis_client(config: Settings) -> redis.Redis:
    return redis.Redis(
        host=config.redis_host, port=config.redis_port, db=config.redis_db
    )
