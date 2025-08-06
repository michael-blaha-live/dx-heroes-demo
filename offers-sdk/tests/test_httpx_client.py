import uuid
import pytest
from respx import MockRouter

from offers_sdk.interfaces import OffersClientInterface
from offers_sdk.exceptions import ProductNotFoundError, ProductAlreadyExistsError, APIError
from tests.conftest import FakeTokenManager # Import the fake class for assertions


# We mark all tests in this file to be run with asyncio
pytestmark = pytest.mark.asyncio


# --- Tests for the register_product method ---

async def test_register_product_success(
    offers_client: OffersClientInterface, respx_mock: MockRouter
):
    """Tests the happy path for product registration (201 Created)."""
    product_id = uuid.uuid4()
    register_route = respx_mock.post(url__regex=r".*/products/register").respond(
        201, json={"id": str(product_id)}
    )

    product = await offers_client.register_product(
        product_id=product_id, name="Test Product", description="A test."
    )

    assert product.id == product_id
    assert register_route.called
    assert register_route.calls.last.request.headers["Bearer"] == f"{FakeTokenManager.DUMMY_TOKEN}"


async def test_register_product_raises_conflict_on_409(
    offers_client: OffersClientInterface, respx_mock: MockRouter
):
    """Tests that a 409 Conflict correctly raises ProductAlreadyExistsError."""
    product_id = uuid.uuid4()
    respx_mock.post(url__regex=r".*/products/register").respond(
        409, json={"detail": "Product ID already registered"}
    )

    with pytest.raises(ProductAlreadyExistsError):
        await offers_client.register_product(
            product_id=product_id, name="Duplicate Product", description="A test."
        )


async def test_register_product_raises_api_error_on_500(
    offers_client: OffersClientInterface, respx_mock: MockRouter
):
    """Tests that a 500 Internal Server Error raises a generic APIError."""
    product_id = uuid.uuid4()
    respx_mock.post(url__regex=r".*/products/register").respond(500)

    with pytest.raises(APIError) as exc_info:
        await offers_client.register_product(
            product_id=product_id, name="Failing Product", description="A test."
        )

    # It's good practice to assert details about the exception
    assert exc_info.value.status_code == 500


# --- Tests for the get_offers method ---

async def test_get_offers_success(
    offers_client: OffersClientInterface, respx_mock: MockRouter
):
    """Tests the happy path for getting offers (200 OK with data)."""
    product_id = uuid.uuid4()
    offer_id = uuid.uuid4()
    
    respx_mock.get(f"/products/{product_id}/offers").respond(
        200, json=[{"id": str(offer_id), "price": 100, "items_in_stock": 10}]
    )

    offers = await offers_client.get_offers(product_id)

    assert len(offers) == 1
    assert offers[0].id == offer_id
    assert offers[0].price == 100


async def test_get_offers_returns_empty_list_for_product_with_no_offers(
    offers_client: OffersClientInterface, respx_mock: MockRouter
):
    """Tests the valid edge case of a product existing but having no offers (200 OK with empty list)."""
    product_id = uuid.uuid4()
    respx_mock.get(f"/products/{product_id}/offers").respond(200, json=[])

    offers = await offers_client.get_offers(product_id)

    assert isinstance(offers, list)
    assert len(offers) == 0


async def test_get_offers_raises_product_not_found_on_404(
    offers_client: OffersClientInterface, respx_mock: MockRouter
):
    """Tests that a 404 Not Found correctly raises ProductNotFoundError."""
    product_id = uuid.uuid4()
    respx_mock.get(f"/products/{product_id}/offers").respond(404)

    with pytest.raises(ProductNotFoundError):
        await offers_client.get_offers(product_id)


async def test_get_offers_raises_api_error_on_503(
    offers_client: OffersClientInterface, respx_mock: MockRouter
):
    """Tests that a 503 Service Unavailable raises a generic APIError."""
    product_id = uuid.uuid4()
    respx_mock.get(f"/products/{product_id}/offers").respond(503)

    with pytest.raises(APIError) as exc_info:
        await offers_client.get_offers(product_id)
        
    assert exc_info.value.status_code == 503