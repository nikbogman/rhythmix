from service.soundcloud import SoundCloudService
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from config import get_settings
from service.soundcloud.client_id_auth import SoundCloudClientIdAuth
from service.soundcloud.client_id_provider import SoundCloudClientIdProvider
from service.soundcloud.api import SoundCloudAPI
from service.audio_cache import AudioCache
from redis import asyncio as aioredis

from contextlib import AsyncExitStack
import httpx


@asynccontextmanager
async def lifespan(api: FastAPI):
    async with AsyncExitStack() as stack:
        settings = get_settings()
        redis_client = aioredis.Redis(
            host=settings.redis_host, port=settings.redis_port, db=settings.redis_db
        )
        # ping redis
        await stack.enter_async_context(redis_client)

        provider_client = httpx.AsyncClient(
            transport=httpx.AsyncHTTPTransport(retries=3)
        )
        await stack.enter_async_context(provider_client)

        client_id_provider = SoundCloudClientIdProvider(http_client=provider_client)

        sc_client = httpx.AsyncClient(
            auth=SoundCloudClientIdAuth(client_id_provider=client_id_provider)
        )
        await stack.enter_async_context(sc_client)

        api.state.soundcloud_service = SoundCloudService(
            api=SoundCloudAPI(http_client=sc_client)
        )
        api.state.audio_cache = AudioCache(redis_client=redis_client)

        yield
