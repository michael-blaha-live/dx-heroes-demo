import uuid
from pydantic import BaseModel


class Product(BaseModel):
    """Data model for a registered product response."""
    id: uuid.UUID
