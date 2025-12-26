import ffmpeg


def download_audio_from_url(url: str, duration: int) -> bytes:
    out, _ = (
        ffmpeg.input(url, t=duration)
        .output("pipe:", format="f32le", acodec="pcm_f32le", ac=1, ar=44100)
        .run(capture_stdout=True, capture_stderr=True)
    )
    return out
