import asyncio
import re

from app.service.http import HttpClient

WEB_URL = "https://soundcloud.com/"
MOBILE_URL = "https://m.soundcloud.com/"


class SoundCloudClientIdProvider:
    def __init__(self, http: HttpClient):
        self.http = http
        self._client_id: str | None = None
        self._lock = asyncio.Lock()

    async def get(self) -> str:
        if self._client_id:
            return self._client_id
        return await self.refetch()

    async def refetch(self) -> str:
        async with self._lock:
            if self._client_id:
                return self._client_id

            client_id = await self._fetch_client_id()
            self._client_id = client_id
            return client_id

    async def _fetch_client_id(self) -> str:
        try:
            client_id = await self._fetch_client_id_web()
        except Exception as web_error:
            print(f"Web fetch error: {web_error}")
            try:
                client_id = await self._fetch_client_id_mobile()
            except Exception as mobile_error:
                print(f"Mobile fetch error: {mobile_error}")
                raise RuntimeError(
                    f"Could not find client ID. Provide one manually.\n"
                    f"Web error: {web_error}\nMobile error: {mobile_error}"
                )

        return client_id

    async def _fetch_client_id_web(self) -> str:
        response = await self.http.get(url=WEB_URL)
        text = response.text
        if not text or not isinstance(text, str):
            raise ValueError("Could not find client ID")

        urls = re.findall(r'https?://[^\s"]+\.js', text)
        if not urls:
            raise ValueError("Could not find script URLs")

        for script_url in urls:
            script_resp = await self.http.get(url=script_url)
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
        response = await self.http.get(url=MOBILE_URL, headers=headers)
        text = response.text
        match = re.search(r'"clientId":"(\w+?)"', text)
        if match:
            return match.group(1)
        raise ValueError("Could not find client ID")

    async def invalidate(self):
        self._client_id = None
