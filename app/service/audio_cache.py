import uuid
from typing import Optional


# TODO: Handle redis errors
class AudioCache:
    def __init__(self, redis_client):
        self.redis = redis_client

    def set(self, data: bytes) -> str:
        key = str(uuid.uuid4())
        self.redis.set(key, data)
        return key

    def get(self, key: str) -> Optional[bytes]:
        return self.redis.get(key)

    def delete(self, key: str) -> bool:
        return bool(self.redis.delete(key))
