from typing import Any, Dict, Optional
import httpx
import asyncio


class HttpClient:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

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
