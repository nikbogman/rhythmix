from app.service.soundcloud import SoundCloudClient
from app.service.soundcloud.track import SoundCloudTrack

API_URL = "https://api-v2.soundcloud.com"
protocols = ["progressive", "hls"]
mime_type = "audio/mpeg"


class SoundCloudAPI:
    def __init__(self, client: SoundCloudClient):
        self.client = client

    def get_url() -> str:
        return API_URL

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
