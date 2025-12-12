from typing import Optional

import httpx

from src.config import Settings
from src.services.dependencies import Dependencies
from src.services.soundcloud import SoundCloudService
from src.services.soundcloud.client_id_auth import SoundCloudClientIdAuth
from src.services.soundcloud.client_id_provider import SoundCloudClientIdProvider


class APIDependencies(Dependencies):
    soundcloud_service: Optional[SoundCloudService] = None

    _provider_http_client: Optional[httpx.AsyncClient] = None
    _soundcloud_http_client: Optional[httpx.AsyncClient] = None

    async def _init_provider_http_client(self) -> httpx.AsyncClient:
        return await self.exit_stack.enter_async_context(
            httpx.AsyncClient(transport=httpx.AsyncHTTPTransport(retries=3))
        )

    async def _init_soundcloud_http_client(self, auth: httpx.Auth) -> httpx.AsyncClient:
        return await self.exit_stack.enter_async_context(
            client=httpx.AsyncClient(auth=auth)
        )

    async def setup(self, settings: Settings):
        await super().setup(settings)

        self._provider_http_client = await self._init_provider_http_client()
        provider = SoundCloudClientIdProvider(self._provider_http_client)
        auth = SoundCloudClientIdAuth(provider)

        self._soundcloud_http_client = await self._init_soundcloud_http_client(auth)
        self.soundcloud_service = SoundCloudService(self._soundcloud_http_client)
