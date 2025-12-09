from fastapi import Request
from app.service.soundcloud_client import SoundCloudClient


def get_sc(request: Request) -> SoundCloudClient:
    return request.app.state.sc


def get_s3(request: Request):
    return request.app.state.s3
