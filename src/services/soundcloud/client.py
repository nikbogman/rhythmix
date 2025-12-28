import re
import threading
import httpx

SOUNDCLOUD_WEB_URL = "https://soundcloud.com/"
SOUNDCLOUD_MOBILE_URL = "https://m.soundcloud.com/"


class SoundCloudClient:
    def __init__(self, http_client: httpx.Client):
        self._http_client = http_client
        self._client_id: str | None = None
        self._lock = threading.Lock()

    def get(self, url: str, **kwargs) -> httpx.Response:
        client_id = self._provider.get_client_id()
        params = {**kwargs.get("params", {}), "client_id": client_id}

        response = self._http_client.get(url, params=params)
        if response.status_code in (401, 403):
            self._provider.invalidate_client_id()
            client_id = self._provider.get_client_id()

            params["client_id"] = client_id
            response = self._http_client.get(url, params=params)

        response.raise_for_status()
        return response

    def _get_client_id(self) -> str:
        if self._client_id:
            return self._client_id

        with self._lock:
            if not self._client_id:
                self._client_id = self._fetch_client_id()

        return self._client_id

    def _invalidate_client_id(self) -> None:
        with self._lock:
            self._client_id = None

    def _fetch_client_id(self) -> str:
        try:
            return self._fetch_client_id_web()
        except Exception as web_error:
            try:
                return self._fetch_client_id_mobile()
            except Exception as mobile_error:
                raise RuntimeError(
                    "Could not find SoundCloud client ID.\n"
                    f"Web error: {web_error}\n"
                    f"Mobile error: {mobile_error}"
                )

    def _fetch_client_id_web(self) -> str:
        response = self._http_client.get(SOUNDCLOUD_WEB_URL, timeout=10)
        response.raise_for_status()

        text = response.text
        if not text:
            raise ValueError("Empty SoundCloud web response")

        urls = re.findall(r'https?://[^\s"]+\.js', text)
        if not urls:
            raise ValueError("Could not find script URLs")

        for script_url in urls:
            script_resp = self._http_client.get(script_url, timeout=10)
            script_resp.raise_for_status()

            match = re.search(
                r'[{,]client_id:"(\w+)"',
                script_resp.text,
            )
            if match:
                return match.group(1)

        raise ValueError("Could not find client ID in web scripts")

    def _fetch_client_id_mobile(self) -> str:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5_1 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "CriOS/99.0.4844.47 Mobile/15E148 Safari/604.1"
            )
        }

        response = self._http_client.get(
            SOUNDCLOUD_MOBILE_URL,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()

        match = re.search(r'"clientId":"(\w+?)"', response.text)
        if match:
            return match.group(1)

        raise ValueError("Could not find client ID in mobile page")
