from typing import Any, Dict

import httpx
from app.service.http import HttpClient
from app.service.soundcloud import SoundCloudClientIdProvider


class SoundCloudClient:
    def __init__(self, http: HttpClient, id_provider: SoundCloudClientIdProvider):
        self.http = http
        self.id_provider = id_provider

    async def request(
        self,
        url: str,
        *,
        params: Dict[str, Any],
        retries: int,
        backoff: int,
    ):
        client_id = await self.id_provider.get()

        try:
            return await self.http.get(
                url,
                params={**(params or {}), "client_id": client_id},
                retries=retries,
                backoff=backoff,
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 403):
                await self.id_provider.invalidate()
                client_id = await self.id_provider.refresh()

                return await self.http.get(
                    url,
                    params={**(params or {}), "client_id": client_id},
                    retries=retries,
                    backoff=backoff,
                )
            else:
                raise
