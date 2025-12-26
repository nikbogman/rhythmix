import ssl
from functools import cache

from pydantic_settings import BaseSettings, SettingsConfigDict

MAX_FILE_SIZE = 1024 * 1024 * 5  # 5mb
DEFAULT_DOWNLOAD_DURATION = 30  # 30s
AUDIO_CACHE_TTL = 300  # 5min

SOUNDCLOUD_WEB_URL = "https://soundcloud.com/"
SOUNDCLOUD_MOBILE_URL = "https://m.soundcloud.com/"
SOUNDCLOUD_API_URL = "https://api-v2.soundcloud.com"

SOUNDCLOUD_PROTOCOLS = ["progressive", "hls"]
SOUNDCLOUD_MIMETYPE = "audio/mpeg"

REDIS_SSL = ssl.CERT_NONE

DELETE_BATCH_SIZE = 5


class Settings(BaseSettings):
    redis_url: str
    api_key: str

    model_config = SettingsConfigDict(env_file=".env")


@cache
def get_settings():
    return Settings()
