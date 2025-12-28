from fastapi import FastAPI
from src.api.dependencies import lifespan
from src.api.tasks import router as task_router

api = FastAPI(lifespan=lifespan)
api.include_router(task_router)

