from src.config import SOUNDCLOUD_MIMETYPE, SOUNDCLOUD_PROTOCOLS
from src.services.soundcloud.api import SoundCloudAPI

from dataclasses import dataclass


@dataclass
class SoundCloudTrack:
    id: int
    urn: str
    title: str
    duration: int
    artist: str
    artist_display: str
    release_date: str
    stream_url: str
    artwork_url: str
    download_url: str
    genre: str
    waveform_url: str


def _select_transcoding(transcodings: list) -> str | None:
    for t in transcodings:
        fmt = t.get("format", {})
        if (
            fmt.get("protocol") in SOUNDCLOUD_PROTOCOLS
            and fmt.get("mime_type") == SOUNDCLOUD_MIMETYPE
        ):
            return t.get("url")
    return None


class SoundCloudService:
    def __init__(self, api: SoundCloudAPI):
        self.api = api

    async def get_track(self, url: str):
        track = await self.api.resolve_track(url)

        stream_url = _select_transcoding(track["media"]["transcodings"])
        if not stream_url:
            raise ValueError("No suitable stream url found.")

        download_url = await self.api.get_download_url(stream_url)
        if not download_url:
            raise ValueError("No suitable progressive transcoding found.")

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
            # artist=track_artist,
            artist_display=artist_display,
            download_url=download_url,
            stream_url=stream_url,
        )
