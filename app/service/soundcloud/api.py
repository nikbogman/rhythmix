from app.service.soundcloud import SoundCloudClient

API_URL = "https://api-v2.soundcloud.com"


class SoundCloudAPI:
    def __init__(self, client: SoundCloudClient):
        self.client = client

    async def get_track(self, track_urn: str):
        response = await self.client.request(
            url=f"{API_URL}/tracks/{track_urn}",
            retries=5,
            backoff=150,
        )
        return response.json()

    async def resolve_track(self, track_url: str):
        response = await self.client.request(
            url=f"{API_URL}/resolve",
            params={"url": track_url},
            retries=5,
            backoff=200,
        )
        return response.json()

    async def get_download_url(self, stream_url: str):
        response = await self.client.request(
            url=stream_url,
            retries=5,
            backoff=200,
        )
        return response.json().get("url")
