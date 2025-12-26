from enum import Enum


class AudioSource(Enum):
    SOUNDCLOUD = "soundcloud"
    SPOTIFY = "spotify"
    S3 = "s3"
    UNKNOWN = "unknown"


def detect_audio_source(url: str) -> AudioSource:
    u = url.lower()

    if "soundcloud.com" in u:
        return AudioSource.SOUNDCLOUD

    if "open.spotify.com" in u or "spotify.com" in u:
        return AudioSource.SPOTIFY

    if "s3.amazonaws.com" in u or u.startswith("s3://"):
        return AudioSource.S3

    return AudioSource.UNKNOWN
