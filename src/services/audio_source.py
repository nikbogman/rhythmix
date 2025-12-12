from enum import Enum


class AudioSource(Enum):
    SOUNDCLOUD = "soundcloud"
    SPOTIFY = "spotify"
    UNKNOWN = "unknown"


def detect_audio_source(url: str) -> AudioSource:
    u = url.lower()

    if "soundcloud.com" in u:
        return AudioSource.SOUNDCLOUD

    if "open.spotify.com" in u or "spotify.com" in u:
        return AudioSource.SPOTIFY

    return AudioSource.UNKNOWN
