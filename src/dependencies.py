from functools import cache

from src.config import Settings, get_settings
import boto3
from boto3.resources.base import ServiceResource

from src.services.storage import Storage
from src.services.storage.disk import DiskStorage
from src.services.storage.s3 import S3Storage


def create_s3_resource(settings: Settings) -> ServiceResource:
    return boto3.resource(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        region_name=settings.s3_region_name,
        aws_access_key_id=settings.s3_aws_access_key_id,
        aws_secret_access_key=settings.s3_aws_secret_access_key,
    )


@cache
def get_s3_resource() -> ServiceResource:
    settings = get_settings()
    return create_s3_resource(settings)


@cache
def get_storage() -> Storage:
    settings = get_settings()

    if settings.env == "prod":
        return S3Storage(settings.storage_base_path, get_s3_resource())

    return DiskStorage(settings.storage_base_path)
