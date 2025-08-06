import pytest
from respx import MockRouter
from pathlib import Path

from offers_sdk.config import get_settings
from dotenv import load_dotenv
from offers_sdk.interfaces import TokenManagerInterface, OffersClientInterface
from offers_sdk.http import HttpxClient
from offers_sdk.client import HttpxOffersClient


@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    """Loads the .env.test file for the entire test session."""
    current_path = Path(__file__)
    
    tests_dir = current_path.parent
    
    project_root = tests_dir.parent.parent
    
    dotenv_path = project_root / ".env.test"
    print(dotenv_path)
    load_dotenv(dotenv_path=dotenv_path, override=True)


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Clears the settings cache after every test to ensure isolation."""
    yield
    get_settings.cache_clear()

class FakeTokenManager(TokenManagerInterface):
    """A fake token manager that conforms to the interface for testing."""
    DUMMY_TOKEN = "fake-access-token-for-testing"

    async def get_access_token(self) -> str:
        return self.DUMMY_TOKEN


@pytest.fixture
def mock_token_manager() -> TokenManagerInterface:
    """Provides a fake TokenManager instance for tests."""
    return FakeTokenManager()


@pytest.fixture
def offers_client(
    mock_token_manager: TokenManagerInterface, respx_mock: MockRouter
) -> OffersClientInterface:
    """

    Provides a fully mocked HttpxOffersClient for testing.
    It injects a REAL HttpxClient (which respx will patch) and a
    FAKE TokenManager.
    """
    http_client = HttpxClient(base_url="https://api.test.com")
    client = HttpxOffersClient(http_client=http_client, token_manager=mock_token_manager)
    return client