import ffmpeg
import asyncio

DURATION_SEC_DEFAULT = 30


def download_audio(url: str) -> bytes:
    out, _ = (
        ffmpeg.input(url, t=DURATION_SEC_DEFAULT)
        .output("pipe:", format="f32le", acodec="pcm_f32le", ac=1, ar=44100)
        .run(capture_stdout=True, capture_stderr=True)
    )
    return out


async def download_audio_async(url: str) -> bytes:
    return await asyncio.to_thread(download_audio, url)
