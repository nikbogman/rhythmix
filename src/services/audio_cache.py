import uuid

import redis.asyncio as aioredis

from src.config import AUDIO_CACHE_TTL


class AudioCache:
    def __init__(self, redis_client: aioredis.Redis):
        self.redis_client = redis_client

    def _generate_key(self) -> str:
        return str(uuid.uuid4())

    # TODO: add ttl
    async def store(self, data: bytes) -> str:
        key = self._generate_key()
        await self.redis_client.set(key, data, ex=AUDIO_CACHE_TTL)
        return key

    async def retreive(self, key: str) -> bytes | None:
        return await self.redis_client.get(key)

    async def remove(self, key: str) -> bool:
        result = await self.redis_client.delete(key)
        return bool(result)
