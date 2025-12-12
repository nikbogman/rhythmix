import ssl
from contextlib import AsyncExitStack
from typing import Optional

from redis import asyncio as aioredis

from src.config import Settings
from src.services.audio_cache import AudioCache


class Dependencies:
    exit_stack: AsyncExitStack

    audio_cache: Optional[AudioCache] = None
    _redis_client: Optional[aioredis.Redis] = None

    async def _init_redis(self, redis_url: str) -> aioredis.Redis:
        redis_client = aioredis.from_url(url=redis_url, ssl_cert_reqs=ssl.CERT_NONE)
        await redis_client.ping()
        return await self.exit_stack.enter_async_context(redis_client)

    def __init__(self):
        self.exit_stack = AsyncExitStack()

    async def setup(self, settings: Settings):
        await self.exit_stack.__aenter__()

        self._redis_client = await self._init_redis(settings.redis_url)
        self.audio_cache = AudioCache(self._redis_client)

    async def cleanup(self):
        await self.exit_stack.aclose()
