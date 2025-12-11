from fastapi import Request

from service.audio_cache import AudioCache
from service.soundcloud import SoundCloudService


def get_soundcloud_service(request: Request) -> SoundCloudService:
    return request.state.soundcloud_service


def get_audio_cache(request: Request) -> AudioCache:
    return request.state.audio_cache
