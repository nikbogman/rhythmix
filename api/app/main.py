from typing import Annotated, Optional
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from api.app.services.file.resolver import FileResolver
from api.app.services.soundcloud.resolver import SoundCloudResolver
from app.dependencies import get_file_resolver, get_soundcloud_resolver, get_sqs_client, lifespan

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


@app.post("/task")
async def create_task(
    soundcloud_resolver: Annotated[
        SoundCloudResolver, Depends(get_soundcloud_resolver)
    ],
    file_resolver: Annotated[
        FileResolver, Depends(get_file_resolver)
    ],
    sqs_client: Annotated[
        FileResolver, Depends(get_sqs_client)
    ],
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
):
    if not file and not url:
        raise HTTPException(
            status_code=400, detail="Either a file or a URL must be provided."
        )

    if file:
        download_url = await file_resolver.resolve_download_url(file)                

    if url:
        # validate url
        download_url = await soundcloud_resolver.resolve_download_url(url)

    print(download_url)

    return {"message": "Hello Bigger Applications!"}


@app.get("/task/{task_id}")
async def get_task(task_id: str):
    # get task status
    return {"message": "Hello Bigger Applications!"}


@app.patch("/task/{task_id}")
async def patch_task(task_id: str, status: str):
    # update task status in db
    return {"message": "Hello Bigger Applications!"}
