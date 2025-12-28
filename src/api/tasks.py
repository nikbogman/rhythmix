from typing import Annotated, Optional
from fastapi import Depends, APIRouter, File, Form, HTTPException, UploadFile
from src.services.file.resolver import FileResolver
from src.services.soundcloud.resolver import SoundCloudResolver
from src.api.dependencies import get_soundcloud_resolver, get_file_resolver
from src.worker.tasks import extract_audio_features
from src.worker import celery_app
from celery.result import AsyncResult

router = APIRouter(prefix="/tasks")


@router.post("/")
async def create_task(
    soundcloud_resolver: Annotated[
        SoundCloudResolver, Depends(get_soundcloud_resolver)
    ],
    file_resolver: Annotated[FileResolver, Depends(get_file_resolver)],
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
):
    if not file and not url:
        raise HTTPException(
            status_code=400, detail="Either file or URL must be provided."
        )
    if file and url:
        raise HTTPException(status_code=400, detail="Provide only one: file or URL.")

    if file:
        download_url = file_resolver.resolve_download_url(
            content=file.file, type=file.content_type, name=file.filename
        )
        source = "s3"
    if url:
        if "soundcloud.com" not in url:
            raise HTTPException(
                status_code=400, detail="Unsupported URL. Only SoundCloud is supported."
            )

        download_url = soundcloud_resolver.resolve_download_url(url)
        source = "soundcloud"

    payload = dict(download_url, source)
    task = extract_audio_features.delay(payload)
    return {"task_id": task.id}


@router.get("/{task_id}")
async def get_task(task_id: str):
    result = AsyncResult(id=task_id, app=celery_app)


    if result.state == "PENDING":
        if result.result is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
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
