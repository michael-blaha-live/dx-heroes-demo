import asyncio
from typing import List
import uuid

from offers_sdk.config import get_settings
from offers_sdk.interfaces import SyncOffersClientInterface, OffersClientInterface
from .httpx_offers_client import HttpxOffersClient
from offers_sdk.models import Product, Offer

settings = get_settings()


class SyncOffersClient(SyncOffersClientInterface): # Implements the sync interface
    """
    A synchronous implementation of the SyncOffersAPI protocol.

    This class wraps an asynchronous client that conforms to the OffersAPI
    protocol and exposes its methods as blocking, synchronous calls.
    """

    def __init__(self, async_client: OffersClientInterface):
        """
        Initializes the synchronous client with an async client instance.

        Args:
            async_client (OffersClientInterface): An object that conforms to the
                asynchronous OffersClientInterface protocol.
        """
        self._async_client = async_client

    @classmethod
    def from_credentials(
        cls,
        refresh_token: str,
        base_url: str = "https://api.example.com/api/v1",
    ) -> "SyncOffersClientInterface":
        """
        A convenient factory method to create a client from a refresh token.

        This is the recommended way for most users to instantiate the client.
        It creates the HttpxOffersClient and injects it.

        Args:
            refresh_token (str): The long-lived refresh token.
            base_url (str): The base URL for the API.

        Returns:
            SyncOffersAPI: A new instance of the synchronous client.
        """
        async_client = HttpxOffersClient(refresh_token=refresh_token, base_url=base_url)
        return cls(async_client=async_client)

    def register_product(
        self, product_id: uuid.UUID, name: str, description: str
    ) -> Product:
        return asyncio.run(self._async_client.register_product(
            product_id=product_id, name=name, description=description
        ))

    def get_offers(self, product_id: uuid.UUID) -> List[Offer]:
        return asyncio.run(self._async_client.get_offers(product_id=product_id))

    def close(self):
        asyncio.run(self._async_client.close())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
