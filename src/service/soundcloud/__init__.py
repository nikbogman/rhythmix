from service.soundcloud.api import SoundCloudAPI
from service.soundcloud.track import SoundCloudTrack

PROTOCOLS = ["progressive", "hls"]
MIMETYPE = "audio/mpeg"


def _select_transcoding(transcodings: list) -> str | None:
    for t in transcodings:
        fmt = t.get("format", {})
        if fmt.get("protocol") in PROTOCOLS and fmt.get("mime_type") == MIMETYPE:
            return t.get("url")
    return None


class SoundCloudService:
    def __init__(self, api: SoundCloudAPI):
        self.api = api

    async def get_track(self, track_artist: str, track_name: str):
        track = await self.api.resolve_track(
            f"https://soundcloud.com/{track_artist}/{track_name}"
        )

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
            artist=track_artist,
            artist_display=artist_display,
            download_url=download_url,
            stream_url=stream_url,
        )
