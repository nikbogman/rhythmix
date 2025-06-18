from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager

from .soundcloud_client import SoundCloudClient
from .audio_analysis import *
from .storage import *

from datetime import datetime

sc = SoundCloudClient()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await sc.get_client_id()
    yield
    await sc.close()


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def get_root():
    return RedirectResponse(url="/static/index.html")


@app.get("/track/{artist}/{track_name}")
def get_track(artist: str, track_name: str):
    track_path = f"{artist}/{track_name}"
    s3_key = f"{track_path}.json"

    try:
        return get_object(key=s3_key)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Track not found")


@app.post("/track/{artist}/{track_name}")
async def analyze_track(artist: str, track_name: str):
    track_path = f"{artist}/{track_name}"
    track_url = f"https://soundcloud.com/{track_path}"
    s3_key = f"{track_path}.json"

    try:
        existing = get_object(key=s3_key)
        return existing
    except FileNotFoundError:
        pass

    track = await sc.resolve_track(track_url)
    track_id = track.get("id")

    stream_url = None

    protocol = "progressive"
    mime_type = "audio/mpeg"

    for t in track["media"]["transcodings"]:
        if t.get("format", {}).get("protocol") == protocol and mime_type in t.get(
            "format", {}
        ).get("mime_type", ""):
            stream_url = t.get("url")

    if not stream_url:
        raise HTTPException(status_code=500, detail="No suitable stream url found.")

    download_url = await sc.get_download_url(stream_url)

    audio = download_audio_segment(download_url)
    audio_data = analyze_audio(audio)

    data = {
        "id": track_id,
        "slug": track_name,
        "artist_slug": artist,
        "artwork_url": track["artwork_url"],
        "full_duration": track["full_duration"],
        "title": track["title"],
        "genre": track["genre"],
        "artist_display": track["publisher_metadata"]["artist"],
        "created_at": str(datetime.now()),
    } | audio_data

    upload_object(key=s3_key, data=data)
    return data
