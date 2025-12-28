from celery import Celery
from src.dependencies import get_settings
import ssl

settings = get_settings()

celery_app = Celery(
    "task_queue",
    broker=settings.redis_url,
    backend=settings.redis_url,
    broker_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE},
    redis_backend_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE},
)
