import uuid
from pydantic import BaseModel


class RegisterProductRequest(BaseModel):
    """Request model for registering a product."""
    id: uuid.UUID
    name: str
    description: str
