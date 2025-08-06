import uuid
from typing import Protocol, List
from offers_sdk.models import Product, Offer


class SyncOffersClientInterface(Protocol):
    """
    Defines the abstract interface (contract) for a synchronous Offers API client.
    """

    def register_product(
        self, product_id: uuid.UUID, name: str, description: str
    ) -> Product:
        """Registers a new product with the service. This is a blocking call."""
        ...

    def get_offers(self, product_id: uuid.UUID) -> List[Offer]:
        """Retrieves all available offers for a product. This is a blocking call."""
        ...

    def close(self) -> None:
        """Closes the client and releases underlying resources."""
        ...
