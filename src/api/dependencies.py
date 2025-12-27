from contextlib import AsyncExitStack
from typing import Optional

from fastapi import Request
import httpx

from src.config import Settings
from src.services.soundcloud import SoundCloudService
from api.app.services.soundcloud.api import SoundCloudAPI
from src.services.soundcloud.client_id_auth import SoundCloudClientIdAuth
from src.services.soundcloud.client_id_provider import SoundCloudClientIdProvider
import boto3
from mypy_boto3_s3.service_resource import Bucket
from src.services.audio_storage import AudioStorage


class DependancyContainer:
    _exit_stack: AsyncExitStack

    soundcloud_service: Optional[SoundCloudService] = None

    _provider_http_client: Optional[httpx.AsyncClient] = None
    _soundcloud_http_client: Optional[httpx.AsyncClient] = None

    def __init__(self):
        self._exit_stack = AsyncExitStack()

    async def _init_provider_http_client(self, retries: int = 3) -> httpx.AsyncClient:
        return await self._exit_stack.enter_async_context(
            httpx.AsyncClient(transport=httpx.AsyncHTTPTransport(retries=retries))
        )

    async def _init_resolver_http_client(self, auth: httpx.Auth) -> httpx.AsyncClient:
        return await self._exit_stack.enter_async_context(
            client=httpx.AsyncClient(auth=auth)
        )

    async def setup(self, settings: Settings):
        await self._exit_stack.__aenter__()

        self._provider_http_client = await self._init_provider_http_client()
        provider = SoundCloudClientIdProvider(self._provider_http_client)
        auth = SoundCloudClientIdAuth(provider)

        self._soundcloud_http_client = await self._init_soundcloud_http_client(auth)
        self.soundcloud_service = SoundCloudService(self.soundcloud_api)

    async def cleanup(self):
        await self._exit_stack.aclose()


def get_audio_storage(request: Request) -> AudioStorage:
    return request.app.state.deps.audio_storage


def get_soundcloud_service(request: Request) -> SoundCloudService:
    return request.app.state.deps.soundcloud_service



