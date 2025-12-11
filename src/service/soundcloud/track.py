from dataclasses import dataclass


@dataclass
class SoundCloudTrack:
    id: int
    urn: str
    title: str
    duration: int
    artist: str
    artist_display: str
    release_date: str
    stream_url: str
    artwork_url: str
    download_url: str
    genre: str
    waveform_url: str
