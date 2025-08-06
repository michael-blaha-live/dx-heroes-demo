from typing import Protocol, List
import uuid

from offers_sdk_applift.models import Product, Offer


class OffersClientInterface(Protocol):
    """
    Defines the abstract interface (contract) for an asynchronous Offers API client.
    """

    async def register_product(
        self, product_id: uuid.UUID, name: str, description: str
    ) -> Product:
        """Registers a new product with the service."""
        ...

    async def get_offers(self, product_id: uuid.UUID) -> List[Offer]:
        """Retrieves all available offers for a specific product."""
        ...

    async def close(self) -> None:
        """Gracefully closes the client and its resources."""
        ...
