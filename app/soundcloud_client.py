import asyncio
import re
from typing import Any, Dict, Optional
import httpx


class SoundCloudClient:
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.client_id: Optional[str] = None
        self.web_url = "https://soundcloud.com/"
        self.api_url = "https://api-v2.soundcloud.com"

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        retries: int = 3,
        backoff: int = 300,
    ):
        for attempt in range(retries):
            try:
                response = await self.client.get(
                    url=url, headers=headers, params=params
                )
                response.raise_for_status()
                return response
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if attempt < retries - 1:
                    sleep_time = backoff * attempt / 1000
                    print(
                        f"[Retry {attempt+1}] Error: {e}. Retrying in {sleep_time:.2f}s"
                    )
                    await asyncio.sleep(sleep_time)
                else:
                    print(f"[Failed after {retries} tries] Error: {e}")
                    raise

    async def get_client_id_web(self) -> str:
        response = await self.get(url=self.web_url)
        text = response.text
        if not text or not isinstance(text, str):
            raise ValueError("Could not find client ID")

        urls = re.findall(r'https?://[^\s"]+\.js', text)
        if not urls:
            raise ValueError("Could not find script URLs")

        for script_url in urls:
            script_resp = await self.client.get(url=script_url)
            script_text = script_resp.text
            match = re.search(r'[{,]client_id:"(\w+)"', script_text)
            if match:
                return match.group(1)

        raise ValueError("Could not find client ID in script URLs")

    async def get_client_id_mobile(self) -> str:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5_1 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/99.0.4844.47 "
                "Mobile/15E148 Safari/604.1"
            )
        }
        response = await self.get(url="https://m.soundcloud.com/", headers=headers)
        text = response.text
        match = re.search(r'"clientId":"(\w+?)"', text)
        if match:
            return match.group(1)
        raise ValueError("Could not find client ID")

    async def get_client_id(self, reset: bool = False) -> str:
        if not self.client_id or reset:
            try:
                self.client_id = await self.get_client_id_web()
            except Exception as web_error:
                print(f"Web fetch error: {web_error}")
                try:
                    self.client_id = await self.get_client_id_mobile()
                except Exception as mobile_error:
                    print(f"Mobile fetch error: {mobile_error}")
                    raise RuntimeError(
                        f"Could not find client ID. Provide one manually.\n"
                        f"Web error: {web_error}\nMobile error: {mobile_error}"
                    )
        return self.client_id

    async def get_track(self, track_urn: str):
        response = await self.get(
            url=f"{self.api_url}/tracks/{track_urn}",
            params={"client_id": self.client_id},
            retries=5,
            backoff=150,
        )
        return response.json()

    async def resolve_track(self, track_url: str):
        response = await self.get(
            url=f"{self.api_url}/resolve",
            params={"url": track_url, "client_id": self.client_id},
            retries=5,
            backoff=200,
        )
        return response.json()

    async def get_download_url(self, stream_url: str):
        response = await self.get(
            url=stream_url,
            params={"client_id": self.client_id},
            retries=5,
            backoff=200,
        )
        download_url = response.json().get("url")
        if not download_url:
            raise Exception("No suitable progressive transcoding found.")

        return download_url

    async def close(self):
        await self.client.aclose()
