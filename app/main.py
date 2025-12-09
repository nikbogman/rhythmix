from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager

from .service.soundcloud_client import SoundCloudClient
from .service.audio_analysis import *

from app.service.rate_limitter import (
    limiter,
    _rate_limit_exceeded_handler,
    RateLimitExceeded,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    sc = SoundCloudClient()
    app.state.sc = sc
    await sc.get_client_id()
    yield
    await sc.close()


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def get_root():
    return RedirectResponse(url="/static/index.html")
