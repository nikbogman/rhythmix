import ffmpeg


def download_audio_segment(url: str, duration_sec: int = 60) -> bytes:
    out, _ = (
        ffmpeg.input(url, t=duration_sec)
        .output("pipe:", format="f32le", acodec="pcm_f32le", ac=1, ar=44100)
        .run(capture_stdout=True, capture_stderr=True)
    )
    return out
