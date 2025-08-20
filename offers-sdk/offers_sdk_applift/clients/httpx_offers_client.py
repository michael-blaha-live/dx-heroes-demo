import uuid
import httpx
from typing import List

from offers_sdk_applift.config import get_settings
from offers_sdk_applift.interfaces import OffersClientInterface, AsyncHttpClientInterface, TokenManagerInterface
from offers_sdk_applift.auth import TokenManager
from offers_sdk_applift.models import RegisterProductRequest, Product, Offer
from offers_sdk_applift.exceptions import request_exception_handler

from offers_sdk_applift.http import HttpxClient


class HttpxOffersClient(OffersClientInterface):
    """
    The default, production-ready implementation of the OffersAPI protocol
    that uses HTTPX as its transport layer.
    """

    def __init__(
        self,
        http_client: AsyncHttpClientInterface,
        token_manager: TokenManagerInterface,
    ):
        """
        Initializes the client with its dependencies.

        Note: For convenience, it is highly recommended to use the
        `.from_credentials()` factory method instead of calling this
        constructor directly.

        Args:
            http_client: An object that conforms to the AsyncHttpClient protocol.
            token_manager: An object that conforms to the TokenManagerProtocol.
        """
        self._http_client = http_client
        self._token_manager = token_manager

    @classmethod
    def from_credentials(
        cls,
        refresh_token: str,
        base_url: str = "https://api.example.com/api/v1",
    ) -> "HttpxOffersClient":
        """
        A convenient factory to create a client from a refresh token.

        This is the recommended way for most users to instantiate the client.
        It creates and wires up the default dependencies (`HttpxClient`, `TokenManager`).

        Args:
            refresh_token: The long-lived refresh token.
            base_url: The base URL for the API.

        Returns:
            A new instance of the HttpxOffersClient.
        """
        settings = get_settings()
        
        http_client = HttpxClient(base_url=base_url or settings.OFFERS_API_BASE_URL)
        token_manager = TokenManager(
            refresh_token=refresh_token, 
            http_client=http_client,
            expiration_seconds=settings.TOKEN_EXPIRATION_SECONDS,
            buffer_seconds=settings.TOKEN_EXPIRATION_BUFFER_SECONDS,
        )
        return cls(http_client=http_client, token_manager=token_manager)

    @request_exception_handler
    async def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """A private helper to orchestrate token retrieval and request execution."""
        access_token = await self._token_manager.get_access_token()
        headers = {
            "Bearer": f"{access_token}",
            **(kwargs.pop("headers", {})),
        }

        response = await self._http_client.request(
                method, url, headers=headers, **kwargs
            )
        return response

    async def register_product(
        self, product_id: uuid.UUID, name: str, description: str
    ) -> Product:
        request_model = RegisterProductRequest(
            id=product_id, name=name, description=description
        )
        response = await self._make_request(
            "POST", "/products/register", json=request_model.model_dump(mode="json")
        )
        return Product.model_validate(response.json())

    async def get_offers(self, product_id: uuid.UUID) -> List[Offer]:
        response = await self._make_request("GET", f"/products/{product_id}/offers")
        return [Offer.model_validate(item) for item in response.json()]

    async def close(self) -> None:
        """Closes the underlying HTTP client."""
        await self._http_client.aclose()

    async def __aenter__(self):
        """Enters the async runtime context."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exits the async runtime context, ensuring the client is closed."""
        await self.close()
