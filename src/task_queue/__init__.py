import asyncio
from celery import Celery, signals
from redis import asyncio as aioredis

from config import get_settings

from service.audio_cache import AudioCache
from service.audio_analysis import analyse_audio
from service.audio_download import download_audio_async

celery_app = Celery(
    "task_queue",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

redis_client: aioredis.Redis
audio_cache: AudioCache


@signals.worker_process_init.connect
def init_celery_worker(**kwargs):
    global redis_client, audio_cache
    settings = get_settings()
    redis_client = aioredis.Redis(
        host=settings.redis_host, port=settings.redis_port, db=settings.redis_db
    )
    audio_cache = AudioCache(redis_client)


@signals.worker_process_shutdown.connect
def shutdown_celery_worker(**kwargs):
    global redis_client
    if redis_client:
        redis_client.close()


@celery_app.task
async def download_audio_task(url: str) -> str:
    audio = await download_audio_async(url)
    cache_key = await audio_cache.store(audio)
    return cache_key


@celery_app.task
async def remove_cache(cache_key: str): ...


@celery_app.task
async def analyze_audio_task(cache_key: str):
    audio = await audio_cache.retreive(cache_key)
    if audio is None:
        raise ValueError("Audio data not found in cache")

    return await asyncio.to_thread(analyse_audio, audio)
