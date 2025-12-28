from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request
import httpx

from src.dependencies import get_storage
from src.services.file.resolver import FileResolver
from src.services.soundcloud.client import SoundCloudClient
from src.services.soundcloud.resolver import SoundCloudResolver
from src.services.storage import Storage


@asynccontextmanager
def lifespan(api: FastAPI):
    with httpx.Client() as http_client:
        api.state.http_client = http_client
        yield


def get_http_client(request: Request) -> httpx.Client:
    return request.app.state.http_client


def get_soundcloud_resolver(
    http_client: Annotated[httpx.Client, Depends(get_http_client)],
):
    client = SoundCloudClient(http_client)
    resolver = SoundCloudResolver(client)
    return resolver


def get_file_resolver(storage: Annotated[Storage, Depends(get_storage)]):
    return FileResolver(storage)
