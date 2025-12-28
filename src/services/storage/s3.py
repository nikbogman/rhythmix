from typing import BinaryIO
from boto3.resources.factory import Bucket

from src.services.storage import Storage


class S3Storage(Storage):
    def __init__(self, base_path: str, bucket: Bucket):
        super().__init__(base_path)
        self._bucket = bucket

    def save(self, key: str, data: BinaryIO) -> str:
        path_key = self._get_path(key)
        self._bucket.upload_fileobj(data, path_key)

        url = self._bucket.meta.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket.name, "Key": key},
            ExpiresIn=300,
        )
        return url

    def delete(self, key: str) -> None:
        self._bucket.Object(key).delete()
