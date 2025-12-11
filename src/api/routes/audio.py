from typing import Annotated

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from api.dependencies import get_audio_cache
from service.audio_cache import AudioCache

from celery import chain
from celery.result import AsyncResult
from task_queue import analyze_audio_task

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
    result = AsyncResult(
        task_id,
    )
    if result.state == "PENDING":
        return {"status": "pending"}
    elif result.state == "FAILURE":
        return {"status": "failure", "error": str(result.info)}
    else:
        return {"status": "success", "data": result.result}
