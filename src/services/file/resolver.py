from typing import BinaryIO
from src.services.storage import Storage

MAX_FILE_SIZE = 1024 * 1024 * 5  # 5mb
ALLOWED_AUDIO_MIME_TYPES = [
    "audio/mpeg",  # MP3
    "audio/wav",  # WAV
    "audio/ogg",  # OGG
    "audio/flac",  # FLAC
    "audio/aac",  # AAC
    "audio/mp4",  # MP4 audio
    "audio/webm",  # WebM audio
]


class FileResolver:
    def __init__(self, storage: Storage):
        self._storage = storage

    async def resolve_download_url(
        self, content: BinaryIO, type: str, name: str
    ):
        if type not in ALLOWED_AUDIO_MIME_TYPES:
            raise ValueError("Invalid audio file type")

        if name.strip() == "":
            raise ValueError("File must have a valid name.")

        if name.isascii():
            raise ValueError("File name contains invalid characters.")

        url = self._storage.save(key=name, data=content)
        return url
