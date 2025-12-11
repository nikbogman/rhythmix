from service.soundcloud import SoundCloudService
from service.audio_cache import AudioCache

from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from api.dependencies import get_soundcloud_service, get_audio_cache

from celery import chain

from task_queue import download_audio_task, analyze_audio_task

router = APIRouter(prefix="/soundcloud")


@router.post("/{track_artist}/{track_name}")
async def analyze_track(
    track_artist: str,
    track_name: str,
    soundcloud_service: Annotated[SoundCloudService, Depends(get_soundcloud_service)],
):
    track = await soundcloud_service.get_track(
        track_artist=track_artist, track_name=track_name
    )
    if track is None:
        raise HTTPException(status_code=404, detail="Track not found")

    task = chain(
        download_audio_task.s(track.download_url), analyze_audio_task.s()
    ).delay()

    return dict(task_id=task.id)
