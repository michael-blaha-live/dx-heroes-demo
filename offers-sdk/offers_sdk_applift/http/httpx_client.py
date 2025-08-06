from typing import Any
from httpx import Response, AsyncClient
from offers_sdk_applift.interfaces  import AsyncHttpClientInterface


class HttpxClient(AsyncHttpClientInterface):
    """Concrete implementation of the HTTP client using httpx."""
    def __init__(self, base_url: str):
        self._client = AsyncClient(base_url=base_url)

    async def request(self, method: str, url: str, **kwargs: Any) -> Response:
        return await self._client.request(method, url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> Response:
        return await self._client.post(url, **kwargs)

    async def get(self, url: str, **kwargs: Any) -> Response:
        return await self._client.get(url, **kwargs)
        
    async def aclose(self) -> None:
        await self._client.aclose()
