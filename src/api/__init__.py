from contextlib import asynccontextmanager
from typing import Annotated

from celery.result import AsyncResult
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.api.dependencies import (
    DependancyContainer,
    get_soundcloud_service,
    get_audio_storage,
)
from src.config import MAX_FILE_SIZE, get_settings
from src.services.audio_source import AudioSource, detect_audio_source
from src.services.audio_storage import AudioStorage
from src.services.soundcloud import SoundCloudService
from src.task_queue import celery_app, extract_audio_features


# def verify_api_key(x_api_key: str = Header(...)):
#     if x_api_key != API_KEY:
#         raise HTTPException(status_code=403, detail="Forbidden")


@asynccontextmanager
async def lifespan(api: FastAPI):
    settings = get_settings()
    deps = DependancyContainer()

    await deps.setup(settings)
    api.state.deps = deps

    yield

    await deps.cleanup()


api = FastAPI(lifespan=lifespan)
api.mount("/static", StaticFiles(directory="static"), name="static")


@api.get("/")
async def get_root():
    return RedirectResponse(url="/static/index.html")


@api.post("/upload")
async def create_task_from_upload(
    audio_storage: Annotated[AudioStorage, Depends(get_audio_storage)],
    file: UploadFile = File(...),
):
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is {MAX_FILE_SIZE / 1024 / 1024} MB",
        )

    audio_id = audio_storage.upload(
        filename=file.filename or "upload",
        content_type=file.content_type,
        content=contents,
    )

    preview_url = audio_storage.generate_preview_url(audio_id)

    task = extract_audio_features.delay(url=preview_url)
    return dict(task_id=task.id)


@api.post("/url")
async def create_task_from_url(
    soundcloud_service: Annotated[SoundCloudService, Depends(get_soundcloud_service)],
    url: str,
):
    source = detect_audio_source(url)
    if source is AudioSource.UNKNOWN:
        raise HTTPException(
            status_code=400,
            detail="Unsupported URL. Only Spotify and SoundCloud are supported.",
        )

    elif source is AudioSource.SOUNDCLOUD:
        track = await soundcloud_service.get_track(url)
        if track is None:
            raise HTTPException(status_code=404, detail="Soundcloud track not found")

        download_url = track.download_url

    else:
        download_url = url

    task = extract_audio_features.delay(url=download_url)
    return dict(task_id=task.id)


@api.get("/task/{task_id}")
async def get_task_result(task_id: str):
    result = AsyncResult(id=task_id, app=celery_app)

    if result.state == "PENDING":
        return {"status": "pending"}
    elif result.state == "FAILURE":
        return {"status": "failure", "error": str(result.info)}
    elif result.ready():
        try:
            data = result.get(timeout=0)
            return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "failure", "error": str(e)}
    else:
        return {"status": result.state}
