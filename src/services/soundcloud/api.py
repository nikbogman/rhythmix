from typing import Optional
import httpx


class SoundCloudAPI:
    def __init__(self, http_client: httpx.AsyncClient):
        self._http_client = http_client

    async def get_track(self, track_urn: str) -> dict:
        response = await self._http_client.get(f"/tracks/{track_urn}")
        response.raise_for_status()
        return response.json()

    async def resolve_track(self, track_url: str) -> dict:
        response = await self._http_client.get("/resolve", params={"url": track_url})
        response.raise_for_status()
        return response.json()

    async def get_download_url(self, stream_url: str) -> Optional[str]:
        response = await self._http_client.get(stream_url)
        response.raise_for_status()
        return response.json().get("url")
