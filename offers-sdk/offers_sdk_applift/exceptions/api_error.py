from .base_offer_sdk_error import BaseOffersSDKError


class APIError(BaseOffersSDKError):
    """Raised for general API errors (e.g., 4xx, 5xx)."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = f"API Error {status_code}: {message}"
        super().__init__(self.message)
