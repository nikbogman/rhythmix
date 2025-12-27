from fastapi import UploadFile
from api.app.services.file.storage import BlobStorage

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
    def __init__(self, blob_storage: BlobStorage):
        self._blob_storage = blob_storage

    async def resolve_download_url(self, file: UploadFile):
        if file.content_type not in ALLOWED_AUDIO_MIME_TYPES:
            raise ValueError("Invalid audio file type")

        if not file.filename or file.filename.strip() == "":
            raise ValueError("File must have a valid name.")

        if not file.filename.isascii():
            raise ValueError("File name contains invalid characters.")

        contents = await file.read(MAX_FILE_SIZE)

        blob_key = self._blob_storage.upload(
            filename=file.filename,
            content_type=file.content_type,
            content=contents,
        )

        preview_url = self._blob_storage.generate_preview_url(blob_key)
        return preview_url
