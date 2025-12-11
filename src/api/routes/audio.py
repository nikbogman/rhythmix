from typing import Annotated

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from src.api.dependencies import get_audio_cache
from src.config import get_settings
from src.service.audio_cache import AudioCache

from celery import chain
from celery.result import AsyncResult
from src.task_queue import analyze_audio_task, celery_app

router = APIRouter(prefix="/audio")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/")
async def upload_audio(
    audio_cache: Annotated[AudioCache, Depends(get_audio_cache)],
    file: UploadFile = File(...),
):
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is {MAX_FILE_SIZE / 1024 / 1024} MB",
        )

    cache_key = await audio_cache.store(data=contents)
    task = analyze_audio_task.delay(cache_key)

    # then delete from cache after processing

    return dict(task_id=task.id)


@router.get("/{task_id}")
async def get_audio(task_id: str):
    settings = get_settings()
    result = AsyncResult(id=task_id, app=celery_app)

    if result.state == "PENDING":
        return {"status": "pending"}
    elif result.state == "FAILURE":
        return {"status": "failure", "error": str(result.info)}
    elif result.ready():  # SUCCESS or RETRY
        try:
            # Use .get() with timeout=0 to avoid blocking if result already available
            data = result.get(timeout=0)
            return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "failure", "error": str(e)}
    else:
        return {"status": result.state}
