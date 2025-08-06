from typing import Protocol, Any
from httpx import Response


class AsyncHttpClientInterface(Protocol):
    """
    An interface for an async HTTP client. Abstraction for high level clients.
    """
    async def request(self, method: str, url: str, **kwargs: Any) -> Response:
        ...

    async def post(self, url: str, **kwargs: Any) -> Response:
        ...
    
    async def get(self, url: str, **kwargs: Any) -> Response:
        ...

    async def aclose(self) -> None:
        ...
