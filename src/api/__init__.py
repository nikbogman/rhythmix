from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.api.lifespan import lifespan
from src.api.routes.soundcloud import router as soundcloud_router
from src.api.routes.audio import router as audio_router

api = FastAPI(lifespan=lifespan)

api.mount("/static", StaticFiles(directory="static"), name="static")

api.include_router(audio_router)
api.include_router(soundcloud_router)


@api.get("/")
async def get_root():
    return RedirectResponse(url="/static/index.html")
