from src.services.soundcloud.client import SoundCloudClient

SOUNDCLOUD_API_URL = "https://api-v2.soundcloud.com"
SOUNDCLOUD_PROTOCOLS = ["progressive", "hls"]
SOUNDCLOUD_MIMETYPE = "audio/mpeg"


class SoundCloudResolver:
    def __init__(self, client: SoundCloudClient):
        self._client = client

    def _select_transcoding(self, transcodings: list) -> str | None:
        for transcoding in transcodings:
            fmt = transcoding.get("format", {})
            if (
                fmt.get("protocol") in SOUNDCLOUD_PROTOCOLS
                and fmt.get("mime_type") == SOUNDCLOUD_MIMETYPE
            ):
                return transcoding.get("url")
        return None

    def resolve_download_url(self, track_url: str) -> str:
        track = self._client.get(
            f"{SOUNDCLOUD_API_URL}/resolve", params={"url": track_url}
        ).json()

        transcodings = track.get("media", {}).get("transcodings", [])
        stream_url = self._select_transcoding(transcodings)

        if not stream_url:
            raise ValueError("No suitable stream URL found for this track.")

        url = self._client.get(stream_url).json().get("url")
        if not url:
            raise ValueError("No download URL found for the stream.")

        return url
