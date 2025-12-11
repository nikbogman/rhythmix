import ssl
from src.service.soundcloud import SoundCloudService
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from src.config import get_settings
from src.service.soundcloud.client_id_auth import SoundCloudClientIdAuth
from src.service.soundcloud.client_id_provider import SoundCloudClientIdProvider
from src.service.soundcloud.api import SoundCloudAPI
from src.service.audio_cache import AudioCache
from redis import asyncio as aioredis

from contextlib import AsyncExitStack
import httpx


@asynccontextmanager
async def lifespan(api: FastAPI):
    async with AsyncExitStack() as stack:
        settings = get_settings()
        redis_client = aioredis.from_url(
            url=settings.redis_url, ssl_cert_reqs=ssl.CERT_NONE
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
