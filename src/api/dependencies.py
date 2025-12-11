from fastapi import Request

from src.service.audio_cache import AudioCache
from src.service.soundcloud import SoundCloudService


def get_soundcloud_service(request: Request) -> SoundCloudService:
    return request.app.state.soundcloud_service


def get_audio_cache(request: Request) -> AudioCache:
    return request.app.state.audio_cache
