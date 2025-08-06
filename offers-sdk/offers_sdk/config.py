
import functools
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Defines the application settings.
    """
    # This is the mandatory variable we defined before.
    OFFERS_SDK_REFRESH_TOKEN: str
    
    OFFERS_API_BASE_URL: str

    TOKEN_EXPIRATION_SECONDS: int
    TOKEN_EXPIRATION_BUFFER_SECONDS: int
    
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding='utf-8')


@functools.lru_cache
def get_settings() -> Settings:
    """Returns a cached instance of the application settings."""
    return Settings()
