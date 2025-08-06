from .api_error import APIError


class ProductAlreadyExistsError(APIError):
    """Raised when trying to register a product that already exists (409)."""
    pass
