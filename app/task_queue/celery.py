from celery import Celery, signals

from app.service.service_container import DependencyResolver

app = Celery("proj", broker="amqp://", backend="rpc://", include=["task_queue.tasks"])


@signals.worker_process_init.connect
def on_init(**kwargs):
    DependencyResolver.setup()


@signals.worker_shutdown.connect
def on_shutdown(**kwargs):
    DependencyResolver.cleanup()
