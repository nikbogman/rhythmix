from fastapi import APIRouter, UploadFile, File, HTTPException

from celery.result import AsyncResult
from app.api.dependencies import AudioCacheDependancy
from app.service.audio_cache import AudioCache
from app.tasks import celery_app, analyze_audio_task

router = APIRouter(prefix="/audio")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/audio")
async def upload_audio(
    file: UploadFile = File(...), audio_cache: AudioCache = AudioCacheDependancy
):
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is {MAX_FILE_SIZE / 1024 / 1024} MB",
        )

    cache_key = audio_cache.set(contents)
    # pass cache_key to celery task for processing
    # then delete from cache after processing

    task = analyze_audio_task.delay(contents)
    return dict(task_id=task.id, cache_key=cache_key)


@router.get("/audio/{task_id}")
async def get_audio(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    if result.state == "PENDING":
        return {"status": "pending"}
    elif result.state == "FAILURE":
        return {"status": "failure", "error": str(result.info)}
    else:
        return {"status": "success", "data": result.result}
