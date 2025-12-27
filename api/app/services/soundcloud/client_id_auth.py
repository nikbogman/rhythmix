import httpx
from app.services.soundcloud.client_id_provider import SoundCloudClientIdProvider


class SoundCloudClientIdAuth(httpx.Auth):
    requires_response_body = True

    def __init__(self, provider: SoundCloudClientIdProvider):
        self._provider = provider

    async def async_auth_flow(self, request: httpx.Request):
        client_id = await self._provider.get_client_id()
        request.url = request.url.copy_add_param("client_id", client_id)
        response = yield request

        if response.status_code in (401, 403):
            await self._provider.invalidate_client_id()

            client_id = await self._provider.get_client_id()
            request.url = request.url.copy_add_param("client_id", client_id)
            response = yield request

        return response
