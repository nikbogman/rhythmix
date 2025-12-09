from celery import Celery

from app.service.audio_download import download_audio_segment
from app.service.audio_analysis import analyze_audio

app = Celery("tasks", broker="pyamqp://guest@localhost//")


@app.task
def download_audio_task(url: str, duration_sec: int = 60) -> bytes:
    return download_audio_segment(url, duration_sec)


@app.task
def analyze_audio_task(audio_bytes: bytes):
    return analyze_audio(audio_bytes)
