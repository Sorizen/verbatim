from celery import Celery

from app.config import settings
from app.constants import CELERY_APP_NAME

celery_app = Celery(CELERY_APP_NAME, broker=settings.REDIS_URL, include=['app.worker.tasks'])
celery_app.conf.update(
    task_ignore_result=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)
