from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles


from app.api.lifespan import lifespan

from app.api.rate_limiter import Limiter, rate_limit_exceeded_handler, RateLimitExceeded


api = FastAPI(lifespan=lifespan)
api.state.limiter = Limiter
api.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


api.mount("/static", StaticFiles(directory="static"), name="static")


@api.get("/")
async def get_root():
    return RedirectResponse(url="/static/index.html")
