import asyncio

import ffmpeg
from app.service.audio_sources.audio_source import AudioSource

DURATION_SEC_DEFAULT = 60


class RemoteAudioSource(AudioSource):
    def __init__(self, url: str):
        self.url = url

    async def get_bytes(self) -> bytes:
        return await asyncio.to_thread(self._download_audio)

    def _download_audio(self) -> bytes:
        out, _ = (
            ffmpeg.input(self.url, t=DURATION_SEC_DEFAULT)
            .output("pipe:", format="f32le", acodec="pcm_f32le", ac=1, ar=44100)
            .run(capture_stdout=True, capture_stderr=True)
        )
        return out
