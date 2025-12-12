import asyncio

from celery import Celery, signals

from src.config import REDIS_SSL, get_settings
from src.services.audio_analysis import analyse_audio
from src.services.audio_download import download_audio
from src.services.dependencies import Dependencies

settings = get_settings()
dependencies: Dependencies

celery_app = Celery(
    "task_queue",
    broker=settings.redis_url,
    backend=settings.redis_url,
    broker_use_ssl={"ssl_cert_reqs": REDIS_SSL},
    redis_backend_use_ssl={"ssl_cert_reqs": REDIS_SSL},
)


@signals.worker_process_init.connect
def init_celery_worker(**kwargs):
    global dependencies
    settings = get_settings()
    dependencies = Dependencies()
    asyncio.run(dependencies.setup(settings))


@signals.worker_process_shutdown.connect
def shutdown_celery_worker(**kwargs):
    global dependencies
    if dependencies:
        asyncio.run(dependencies.cleanup())


@celery_app.task
def download_audio_task(url: str) -> str:
    audio = download_audio(url)
    cache_key = asyncio.run(dependencies.audio_cache.store(audio))
    return cache_key


@celery_app.task
def analyze_audio_task(cache_key: str):
    audio = asyncio.run(dependencies.audio_cache.retreive(cache_key))
    if audio is None:
        raise ValueError("Audio data not found in cache")

    return analyse_audio(audio)
