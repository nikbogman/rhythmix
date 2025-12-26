import uuid
from typing import List
from mypy_boto3_s3.service_resource import Bucket


class AudioStorage:
    _bucket: Bucket

    def __init__(
        self,
        bucket: Bucket,
        base_path: str = "audio",
    ):
        self._bucket = bucket
        self._base_path = base_path

    def _generate_object_key(self, filename: str) -> str:
        unique_id = uuid.uuid4()
        return f"{self._base_path}/{unique_id}-{filename}"

    def upload(self, filename: str, content: bytes, content_type: str) -> str:
        key = self._generate_object_key(filename)
        self._bucket.put_object(Key=key, Body=content, ContentType=content_type)
        return key

    def delete(self, audio_id: str) -> None:
        self._bucket.Object(audio_id).delete()

    def delete_if_exists(self, audio_id: str) -> bool:
        obj = self._bucket.Object(audio_id)
        try:
            obj.load()
        except self._bucket.meta.client.exceptions.NoSuchKey:
            return False
        obj.delete()
        return True

    def bulk_delete(self, audio_ids: List[str]) -> int:
        objects = [{"Key": key} for key in audio_ids]
        if not objects:
            return 0
        self._bucket.delete_objects(Delete={"Objects": objects, "Quiet": True})
        return len(objects)

    def generate_preview_url(self, audio_id: str, expires_in_seconds: int = 300) -> str:
        return self._bucket.meta.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self._bucket.name, "Key": audio_id},
            ExpiresIn=expires_in_seconds,
        )
