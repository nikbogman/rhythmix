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

    async def get_track_urn(self, track_urn: str):
        response = await self.client.request(
            url=f"{API_URL}/tracks/{track_urn}",
            retries=5,
            backoff=150,
        )
        return response.json()

    async def get_track(self, track_artist: str, track_name: str):
        track = await self.resolve_track(
            f"https://soundcloud.com/{track_artist}/{track_name}"
        )

        stream_url = None

        for t in track["media"]["transcodings"]:
            fmt = t.get("format", {})
            if (
                fmt.get("protocol") in protocols
                and fmt.get("mime_type", "") == mime_type
            ):
                stream_url = t.get("url")
                break

        if not stream_url:
            raise ValueError("No suitable stream url found.")

        download_url = await self.get_download_url(stream_url)

        artist_display = track.get("publisher_metadata").get("artist")
        if not artist_display:
            artist_display = track.get("user").get("username")

        return SoundCloudTrack(
            id=track.get("id"),
            urn=track.get("urn"),
            title=track.get("title"),
            duration=track.get("full_duration"),
            release_date=track.get("release_date"),
            artwork_url=track.get("artwork_url"),
            genre=track.get("genre"),
            waveform_url=track.get("waveform_url"),
            artist=track_artist,
            artist_display=artist_display,
            download_url=download_url,
            stream_url=stream_url,
        )

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
