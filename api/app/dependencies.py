from fastapi import FastAPI, Request
import httpx
from contextlib import asynccontextmanager
import boto3
from api.app.services.file.resolver import FileResolver
from api.app.services.file.storage import FileStorage
from app.services.soundcloud.client_id_provider import SoundCloudClientIdProvider
from app.services.soundcloud.client_id_auth import SoundCloudClientIdAuth
from app.services.soundcloud.resolver import SoundCloudResolver
from functools import cache
from mypy_boto3_s3.service_resource import Bucket
from app.config import Settings


@asynccontextmanager
async def create_soundcloud_resolver():
    provider_http_client = httpx.AsyncClient(
        transport=httpx.AsyncHTTPTransport(retries=3)
    )
    provider = SoundCloudClientIdProvider(provider_http_client)
    auth = SoundCloudClientIdAuth(provider)

    resolver_http_client = httpx.AsyncClient(auth=auth)
    resolver = SoundCloudResolver(resolver_http_client)

    yield resolver

    await resolver_http_client.aclose()
    await provider_http_client.aclose()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with create_soundcloud_resolver() as soundcloud_resolver:
        app.state.soundcloud_resolver = soundcloud_resolver
        yield


def get_soundcloud_resolver(request: Request) -> SoundCloudResolver:
    return request.app.state.soundcloud_resolver


@cache
def get_settings():
    return Settings()


@cache
def get_sqs_queue():
    settings = get_settings()
    sqs = boto3.resource(
        "sqs",
        endpoint_url=settings.sqs_endpoint_url,
        region_name=settings.sqs_region_name,
        aws_secret_access_key=settings.sqs_aws_secret_access_key,
        aws_access_key_id=settings.sqs_aws_access_key_id,
        use_ssl=False,
    )
    queue = sqs.get_queue_by_name(QueueName=settings.sqs_queue_name)
    return queue


@cache
def get_s3_bucket(bucket_name: str) -> Bucket:
    settings = get_settings()
    s3 = boto3.resource(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        region_name=settings.s3_region_name,
        aws_secret_access_key=settings.s3_aws_secret_access_key,
        aws_access_key_id=settings.s3_aws_access_key_id,
        use_ssl=False,
    )
    bucket = s3.Bucket(settings.s3_bucket_name)
    return bucket


@cache
def get_file_storage() -> FileStorage:
    bucket = get_s3_bucket()
    return FileStorage(bucket)


@cache
def get_file_resolver() -> FileResolver:
    storage = get_file_storage()
    return FileResolver(storage)
