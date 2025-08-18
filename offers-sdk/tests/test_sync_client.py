import uuid
import pytest

from unittest.mock import AsyncMock

from offers_sdk_applift.clients import SyncOffersClient, HttpxOffersClient
from offers_sdk_applift.interfaces import OffersClientInterface


def test_sync_client_factory_creates_correct_types():
    """
    Tests that the .from_credentials() factory correctly constructs the clients.
    """
    # This test doesn't make network calls, so it needs no mocks.
    # It just checks the object structure.
    sync_client = SyncOffersClient.from_credentials(refresh_token="dummy-token")

    assert isinstance(sync_client, SyncOffersClient)
    assert isinstance(sync_client._async_client, HttpxOffersClient)


def test_get_offers_delegates_to_async_client(mocker):
    """
    Tests that calling a method on the sync client correctly calls
    the corresponding method on the wrapped async client.
    """
    # 1. Arrange: Create a mock of the async client
    mock_async_client = AsyncMock(spec=OffersClientInterface)
    
    # 2. Arrange: Create a sync client instance, injecting our mock
    sync_client = SyncOffersClient(async_client=mock_async_client)
    product_id = uuid.uuid4()

    # 3. Act: Call the synchronous method
    sync_client.get_offers(product_id)

    # 4. Assert: Check that the corresponding ASYNC method on our mock
    #    was called exactly once with the correct arguments.
    mock_async_client.get_offers.assert_awaited_once_with(product_id=product_id)
