from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_key: str
    bucket_name: str

    sqs_endpoint_url: str
    sqs_region_name: str
    sqs_aws_secret_access_key: str
    sqs_aws_access_key_id: str
    sqs_queue_name: str

    s3_endpoint_url: str
    s3_region_name: str
    s3_aws_secret_access_key: str
    s3_aws_access_key_id: str
    s3_bucket_name: str

    model_config = SettingsConfigDict(env_file=".env")


