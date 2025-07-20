from fastapi import APIRouter
from app.celery import sample_task

tasks_router = APIRouter()

@tasks_router.get("/celery")
async def check_celery_health():
    res = sample_task.delay()
    print(res)
    if res:
        return {"status": "ok", "message": "Celery is up and running"}
    else:
        return {"status": "error", "message": "Celery is not running"}