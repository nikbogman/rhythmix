from dataclasses import dataclass
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from app.dependencies import get_sc
from app.service.rate_limitter import limiter
from app.service.soundcloud_client import SoundCloudClient

router = APIRouter("/soundcloud")


protocols = ["progressive", "hls"]
mime_type = "audio/mpeg"


@router.post("/{artist}/{track_name}")
@limiter.limit("20/minute")
async def analyze_track(
    artist: str,
    track_name: str,
    request: Request,
    response: Response,
    sc: SoundCloudClient = Depends(get_sc),
):
    track_path = f"{artist}/{track_name}"

    track_url = f"https://soundcloud.com/{track_path}"
    track = await sc.resolve_track(track_url)

    stream_url = None
    for t in track["media"]["transcodings"]:
        fmt = t.get("format", {})
        if fmt.get("protocol") in protocols and fmt.get("mime_type", "") == mime_type:
            stream_url = t.get("url")
            break

    if not stream_url:
        raise HTTPException(status_code=500, detail="No suitable stream url found.")

    download_url = await sc.get_download_url(stream_url)
    if not download_url:
        raise HTTPException(
            status_code=500, detail="No suitable progressive transcoding found."
        )

    artist_display = track.get("publisher_metadata").get("artist")
    if not artist_display:
        artist_display = track.get("user").get("username")

    # chain dowload, analyze, save

    return {}
