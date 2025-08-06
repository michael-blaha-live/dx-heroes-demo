from .api_error import APIError


class ProductNotFoundError(APIError):
    """Raised when a product is not found (404)."""
    pass
