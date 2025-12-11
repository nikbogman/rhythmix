from app.service.audio_sources.audio_source import RemoteAudioSource
from app.service.soundcloud.api import SoundCloudAPI

PROTOCOLS = ["progressive", "hls"]
MIME_TYPE = "audio/mpeg"


class SoundCloudAudioSource(RemoteAudioSource):
    def __init__(self, api: SoundCloudAPI, track: any):
        self.api = api
        self.track = track

    async def get_bytes(self) -> bytes:

        download_url = await self.api.get_download_url(stream_url)
        if not download_url:
            raise ValueError(
                status_code=500, detail="No suitable progressive transcoding found."
            )

        return await super().get_bytes()
        # download
