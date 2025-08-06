from .base_offer_sdk_error import BaseOffersSDKError


class AuthenticationError(BaseOffersSDKError):
    """Raised when authentication fails (401)."""
    pass
