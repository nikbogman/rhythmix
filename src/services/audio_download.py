import ffmpeg

from src.config import DEFAULT_DOWNLOAD_DURATION


def download_audio(url: str) -> bytes:
    out, _ = (
        ffmpeg.input(url, t=DEFAULT_DOWNLOAD_DURATION)
        .output("pipe:", format="f32le", acodec="pcm_f32le", ac=1, ar=44100)
        .run(capture_stdout=True, capture_stderr=True)
    )
    return out
