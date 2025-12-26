from celery import Celery

from src.config import get_settings, REDIS_SSL
from src.services.audio_analysis import analyse_audio
from src.services.audio_download import download_audio_from_url

settings = get_settings()

celery_app = Celery(
    "task_queue",
    broker=settings.redis_url,
    backend=settings.redis_url,
    broker_use_ssl={"ssl_cert_reqs": REDIS_SSL},
    redis_backend_use_ssl={"ssl_cert_reqs": REDIS_SSL},
)


@celery_app.task
def extract_audio_features(url: str):
    audio = download_audio_from_url(url)

    features = analyse_audio(audio)

    return features
