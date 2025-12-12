import httpx

from src.config import SOUNDCLOUD_API_URL


class SoundCloudAPI:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client

    async def get_track(self, track_urn: str):
        response = await self.http_client.get(
            url=f"{SOUNDCLOUD_API_URL}/tracks/{track_urn}",
        )
        return response.json()

    async def resolve_track(self, track_url: str):
        # TODO: handle no track found
        response = await self.http_client.get(
            url=f"{SOUNDCLOUD_API_URL}/resolve",
            params={"url": track_url},
        )
        return response.json()

    async def get_download_url(self, stream_url: str):
        response = await self.http_client.get(
            url=stream_url,
        )
        return response.json().get("url")
