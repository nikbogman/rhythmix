from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from api.lifespan import lifespan

api = FastAPI(lifespan=lifespan)

api.mount("/static", StaticFiles(directory="static"), name="static")


@api.get("/")
async def get_root():
    return RedirectResponse(url="/static/index.html")
