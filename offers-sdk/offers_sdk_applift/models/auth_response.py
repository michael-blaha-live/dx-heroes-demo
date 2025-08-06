from pydantic import BaseModel


class AuthResponse(BaseModel):
    """Data model for the authentication response."""
    access_token: str
