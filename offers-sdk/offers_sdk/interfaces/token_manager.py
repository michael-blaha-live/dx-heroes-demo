from typing import Protocol


class TokenManagerInterface(Protocol):
    """
    Defines the contract for an object that can provide an access token.
    """
    async def get_access_token(self) -> str:
        """
        Retrieves a valid API access token.

        Any class implementing this protocol is responsible for handling all
        internal logic, such as caching the token, checking its expiration,
        and refreshing it when necessary.

        Returns:
            A valid access token string.
        """
        ...
