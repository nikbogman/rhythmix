from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlparse

from celery import Task
from src.dependencies import get_storage
from src.worker import celery_app
import ffmpeg
import essentia.standard as es
import numpy as np

MAX_DURATION = 30


@dataclass
class Payload:
    source: Literal["s3", "soundcloud"]
    download_url: str


def get_s3_key_from_url(presigned_url: str) -> str:
    parsed = urlparse(presigned_url)
    return parsed.path.lstrip("/")


class MyTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        source = kwargs.get("source")
        if not source:
            return

        if source == "soundcloud":
            return  # later maybe upload

        download_url = kwargs.get("download_url")
        if not download_url:
            return

        s3_key = get_s3_key_from_url(download_url)
        storage = get_storage()

        storage.delete(s3_key)
        print(f"Task {task_id} succeeded with result: {retval}")


@celery_app.task
def extract_audio_features(payload: Payload):
    audio_bytes, _ = (
        ffmpeg.input(payload.url, t=MAX_DURATION)
        .output("pipe:", format="f32le", acodec="pcm_f32le", ac=1, ar=44100)
        .run(capture_stdout=True, capture_stderr=True)
    )
    audio = np.frombuffer(audio_bytes, dtype=np.float32)
    key, scale, _ = es.KeyExtractor()(audio)
    bpm, _, _, _, _ = es.RhythmExtractor2013(method="multifeature")(audio)

    return dict(bpm=bpm, key=key, scale=scale)
