import uuid
from pydantic import BaseModel, Field


class Offer(BaseModel):
    """Data model for an offer."""
    id: uuid.UUID
    price: int
    items_in_stock: int = Field(..., alias='items_in_stock')
