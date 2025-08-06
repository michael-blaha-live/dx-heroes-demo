import os
import asyncio
import json
import time
import httpx

from typing import Optional
from platformdirs import user_cache_dir
from filelock import FileLock

from offers_sdk.interfaces import TokenManagerInterface
from offers_sdk.exceptions import AuthenticationError, APIError


class TokenManager(TokenManagerInterface):
    """
    Manages the lifecycle of an access token.
    Its single responsibility is to provide a valid token.
    """
    def __init__(
        self,
        refresh_token: str,
        http_client: httpx.AsyncClient,
        expiration_seconds: int = 300,  
        buffer_seconds: int = 30,
        ):
        self._refresh_token = refresh_token
        self._http_client = http_client
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        self._lock = asyncio.Lock()
        self._expiration_seconds = expiration_seconds
        self._buffer_seconds = buffer_seconds
        
        cache_dir = user_cache_dir("offers_sdk", "OffersSDK")
        os.makedirs(cache_dir, exist_ok=True)
        self._cache_file_path = os.path.join(cache_dir, "token_cache.json")
        # Lock file to prevent inter-process race conditions
        self._file_lock = FileLock(f"{self._cache_file_path}.lock")
    
    def _load_from_cache(self) -> bool:
        """Tries to load and validate a token from the filesystem cache."""
        if not os.path.exists(self._cache_file_path):
            return False
        
        try:
            with open(self._cache_file_path, "r") as f:
                cache_data = json.load(f)
            
            # Check if the cached token is still valid
            if time.monotonic() < cache_data.get("expires_at", 0) - self._buffer_seconds:
                self._access_token = cache_data["access_token"]
                self._token_expires_at = cache_data["expires_at"]
                return True
        except (IOError, json.JSONDecodeError, KeyError):
            # If file is corrupt or invalid, we'll just fetch a new token
            return False
        return False

    def _save_to_cache(self):
        """Saves the current in-memory token to the filesystem cache."""
        cache_data = {
            "access_token": self._access_token,
            "expires_at": self._token_expires_at,
        }
        try:
            with open(self._cache_file_path, "w") as f:
                json.dump(cache_data, f)
        except IOError:
            # If we can't write the cache, it's not a critical failure.
            # The app can still function, it just won't be as fast next time.
            pass

    async def get_access_token(self) -> str:
        """Retrieves a valid API access token from cache or by refreshing."""
        # Use a file lock to ensure only one process at a time can modify the cache
        with self._file_lock:
            async with self._lock:
                # 1. Try to load from the file cache first.
                if self._load_from_cache():
                    return self._access_token

                # 2. If file cache is invalid, check in-memory token.
                if self._access_token and time.monotonic() < self._token_expires_at - self._buffer_seconds:
                    return self._access_token
                
                # 3. If all else fails, fetch a new token from the API
                max_retries = 3
                retry_delay_seconds = 5

                for attempt in range(max_retries):
                    try:
                        headers = {"Bearer": self._refresh_token}
                        response = await self._http_client.post("/auth", headers=headers)

                        if response.status_code == 201:
                            data = response.json()
                            self._access_token = data["access_token"]
                            self._token_expires_at = time.monotonic() + self._expiration_seconds
                            
                            # 4. Save the new token to the cache file
                            self._save_to_cache()
                            
                            return self._access_token
                        
                        
                        detail = response.json().get("detail", "")
                        if "another is valid" in detail and attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay_seconds)
                            continue
                        
                        raise AuthenticationError(f"Failed to refresh token: {response.text}")

                    except (httpx.HTTPStatusError, json.JSONDecodeError) as e:
                        raise APIError(getattr(e, 'response.status_code', 500), str(e)) from e
                
                raise AuthenticationError(f"Failed to refresh token after {max_retries} attempts.")
