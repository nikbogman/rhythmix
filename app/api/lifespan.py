from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from app.service.service_container import ServiceContainer


@asynccontextmanager
async def lifespan(api: FastAPI):
    svc = ServiceContainer({})
    api.state.services = svc

    yield

    del svc
