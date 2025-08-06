import uuid
import httpx
from typing import List

from offers_sdk_applift.config import get_settings
from offers_sdk_applift.interfaces import OffersClientInterface, AsyncHttpClientInterface, TokenManagerInterface
from offers_sdk_applift.auth import TokenManager
from offers_sdk_applift.models import RegisterProductRequest, Product, Offer
from offers_sdk_applift.exceptions import (
    APIError, ProductNotFoundError, ProductAlreadyExistsError, AuthenticationError
)

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
        
        http_client = HttpxClient(base_url=settings.OFFERS_API_BASE_URL)
        token_manager = TokenManager(
            refresh_token=refresh_token, 
            http_client=http_client,
            expiration_seconds=settings.TOKEN_EXPIRATION_SECONDS,
            buffer_seconds=settings.TOKEN_EXPIRATION_BUFFER_SECONDS,
        )
        return cls(http_client=http_client, token_manager=token_manager)

    async def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """A private helper to orchestrate token retrieval and request execution."""
        access_token = await self._token_manager.get_access_token()
        headers = {
            "Bearer": f"{access_token}",
            **(kwargs.pop("headers", {})),
        }

        try:
            response = await self._http_client.request(
                method, url, headers=headers, **kwargs
            )
            match response.status_code:
                case 401: 
                    raise AuthenticationError("Request failed: Invalid access token.")
                case 404: 
                    raise ProductNotFoundError(response.status_code, response.text)
                case 409: 
                    raise ProductAlreadyExistsError(response.status_code, response.text)

            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            # We specifically catch HTTP errors and preserve the original status code
            raise APIError(status_code=e.response.status_code, message=str(e)) from e
        except Exception as e:
            # This catches other errors (e.g., timeouts, network issues)
            # and wraps them in a generic 500 error.
            if isinstance(e, APIError):
                raise  # Don't re-wrap our own exceptions
            raise APIError(status_code=500, message=str(e)) from e

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
