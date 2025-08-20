from .api_error import APIError


class ProductAlreadyFoundError(APIError):
    """Raised when trying to register a product that already exists (409)."""
    pass
