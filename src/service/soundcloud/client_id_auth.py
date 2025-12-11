import httpx
from service.soundcloud.client_id_provider import SoundCloudClientIdProvider


class SoundCloudClientIdAuth(httpx.Auth):
    requires_response_body = True

    def __init__(self, client_id_provider: SoundCloudClientIdProvider):
        self.client_id_provider = client_id_provider

    async def async_auth_flow(self, request: httpx.Request):
        client_id = await self.client_id_provider.get()

        request.url = request.url.copy_add_param("client_id", client_id)
        response = yield request

        if response.status_code in (401, 403):
            await self.client_id_provider.invalidate()
            client_id = await self.client_id_provider.refetch()

            request.url = request.url.copy_add_param("client_id", client_id)
            yield request
