import time
from celery import Celery
from app.settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery = Celery(__name__)
celery.conf.broker_url = CELERY_BROKER_URL
celery.conf.result_backend = CELERY_RESULT_BACKEND

celery.autodiscover_tasks(["app.users_app", "app.chat_app"])

@celery.task(name="sample_task")
def sample_task():
    time.sleep(3)
    print("Long Running Operation Completed")
    return True