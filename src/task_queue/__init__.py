import asyncio
import ssl
from celery import Celery, signals
from redis import asyncio as aioredis

from src.config import get_settings

from src.service.audio_cache import AudioCache
from src.service.audio_analysis import analyse_audio
from src.service.audio_download import download_audio

settings = get_settings()

celery_app = Celery(
    "task_queue",
    broker=settings.redis_url,
    backend=settings.redis_url,
    broker_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE},  # or CERT_REQUIRED
    redis_backend_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE},
)

redis_client: aioredis.Redis
audio_cache: AudioCache


@signals.worker_process_init.connect
def init_celery_worker(**kwargs):
    global redis_client, audio_cache
    settings = get_settings()
    redis_client = aioredis.from_url(
        url=settings.redis_url, ssl_cert_reqs=ssl.CERT_NONE
    )

    audio_cache = AudioCache(redis_client)


@signals.worker_process_shutdown.connect
def shutdown_celery_worker(**kwargs):
    global redis_client
    if redis_client:
        asyncio.run(redis_client.close())


@celery_app.task
def download_audio_task(url: str) -> str:
    audio = download_audio(url)
    cache_key = asyncio.run(audio_cache.store(audio))
    return cache_key


@celery_app.task
def analyze_audio_task(cache_key: str):
    audio = asyncio.run(audio_cache.retreive(cache_key))
    if audio is None:
        raise ValueError("Audio data not found in cache")

    return analyse_audio(audio)
