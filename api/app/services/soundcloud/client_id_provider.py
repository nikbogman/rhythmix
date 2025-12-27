import asyncio
import re
from typing import Optional

import httpx


SOUNDCLOUD_WEB_URL = "https://soundcloud.com/"
SOUNDCLOUD_MOBILE_URL = "https://m.soundcloud.com/"


class SoundCloudClientIdProvider:
    _client_id: Optional[str]

    def __init__(self, http_client: httpx.AsyncClient):
        self._http_client = http_client

        self._client_id = None
        self._lock = asyncio.Lock()

    async def get(self) -> str:
        if not self._client_id:
            return await self.refetch()

        return self._client_id

    async def get_client_id(self) -> str:
        if not self._client_id:
            async with self._lock:
                if not self._client_id:
                    self._client_id = await self._fetch_client_id()

        return self._client_id

    async def invalidate_client_id(self):
        self._client_id = None

    async def _fetch_client_id(self) -> str:
        try:
            return await self._fetch_client_id_web()
        except Exception as web_error:
            try:
                return await self._fetch_client_id_mobile()
            except Exception as mobile_error:
                raise RuntimeError(
                    f"Could not find client ID. Provide one manually.\n"
                    f"Web error: {web_error}\nMobile error: {mobile_error}"
                )

    async def _fetch_client_id_web(self) -> str:
        response = await self._http_client.get(url=SOUNDCLOUD_WEB_URL)
        response.raise_for_status()
        text = response.text
        if not text or not isinstance(text, str):
            raise ValueError("Could not find client ID")

        urls = re.findall(r'https?://[^\s"]+\.js', text)
        if not urls:
            raise ValueError("Could not find script URLs")

        for script_url in urls:
            script_resp = await self._http_client.get(url=script_url)
            script_resp.raise_for_status()
            script_text = script_resp.text
            match = re.search(r'[{,]client_id:"(\w+)"', script_text)
            if match:
                return match.group(1)

        raise ValueError("Could not find client ID in script URLs")

    async def _fetch_client_id_mobile(self) -> str:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5_1 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/99.0.4844.47 "
                "Mobile/15E148 Safari/604.1"
            )
        }
        response = await self._http_client.get(
            url=SOUNDCLOUD_MOBILE_URL, headers=headers
        )
        response.raise_for_status()
        text = response.text
        match = re.search(r'"clientId":"(\w+?)"', text)
        if match:
            return match.group(1)

        raise ValueError("Could not find client ID")
