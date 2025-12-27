from typing import Optional
import httpx

SOUNDCLOUD_API_URL = "https://api-v2.soundcloud.com"
SOUNDCLOUD_PROTOCOLS = ["progressive", "hls"]
SOUNDCLOUD_MIMETYPE = "audio/mpeg"


class SoundCloudResolver:
    def __init__(self, http_client: httpx.AsyncClient):
        self._http_client = http_client

    async def _resolve_track(self, track_url: str) -> dict:
        response = await self._http_client.get(
            f"{SOUNDCLOUD_API_URL.rstrip('/')}/resolve", params={"url": track_url}
        )
        response.raise_for_status()
        return response.json()

    async def _get_download_url(self, stream_url: str) -> Optional[str]:
        response = await self._http_client.get(stream_url)
        response.raise_for_status()
        return response.json().get("url")

    def _select_transcoding(self, transcodings: list) -> Optional[str]:
        for transcoding in transcodings:
            fmt = transcoding.get("format", {})
            if (
                fmt.get("protocol") in SOUNDCLOUD_PROTOCOLS
                and fmt.get("mime_type") == SOUNDCLOUD_MIMETYPE
            ):
                return transcoding.get("url")
        return None

    async def resolve_download_url(self, track_url: str) -> str:
        track = await self._resolve_track(track_url)

        transcodings = track.get("media", {}).get("transcodings", [])
        stream_url = self._select_transcoding(transcodings)

        if not stream_url:
            raise ValueError("No suitable stream URL found for this track.")

        download_url = await self._get_download_url(stream_url)
        if not download_url:
            raise ValueError("No download URL found for the stream.")

        return download_url
