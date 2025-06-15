from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl, field_validator
from contextlib import asynccontextmanager

from .soundcloud_client import SoundCloudClient
from .audio_analysis import *

sc = SoundCloudClient()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await sc.get_client_id()
    # load env
    # init boto3
    # init ratelimitter

    yield

    await sc.close()


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


class TrackRequest(BaseModel):
    url: HttpUrl

    @field_validator("url")
    @classmethod
    def must_be_soundcloud(cls, v: HttpUrl):
        if "soundcloud.com" not in v.host:
            raise ValueError("Only SoundCloud URLs are supported")
        return v


@app.get("/")
async def get_root():
    return RedirectResponse(url="/static/index.html")


@app.post("/")
async def post_root(request: TrackRequest):
    resolved_track = await sc.resolve_track(track_url=request.url)
    track_id = resolved_track.get("id")
    download_url = await sc.get_download_url(track_id)

    audio = download_audio_segment(download_url)
    data = analyze_audio(audio)
    return data
