from fastapi import APIRouter, UploadFile, File, HTTPException

from celery.result import AsyncResult
from app.celery.tasks import celery_app, analyze_audio_task

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/audio")
async def upload_audio(file: UploadFile = File(...)):
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is {MAX_FILE_SIZE / 1024 / 1024} MB",
        )

    task = analyze_audio_task.delay(contents)
    return {"task_id": task.id}


@router.get("/audio/{task_id}")
async def get_audio(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    if result.state == "PENDING":
        return {"status": "pending"}
    elif result.state == "FAILURE":
        return {"status": "failure", "error": str(result.info)}
    else:
        return {"status": "success", "data": result.result}
