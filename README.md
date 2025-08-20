# Offers SDK for Python
A modern, async-first Python SDK for interacting with the Offers API, designed for ease of use and robustness in production applications.

## Features
Async-first Design: Built with `asyncio` and `httpx` for modern, high-performance applications.

Automatic Token Management: Handles access token caching and refreshing automatically and transparently. Includes a persistent file-based cache for efficiency between CLI runs.

Synchronous Wrapper: A convenient sync wrapper (`SyncOffersClient`) is included for seamless integration into synchronous codebases.

Fully Type-Hinted: Provides a great developer experience with modern IDEs and allows for static analysis.

Robust Error Handling: Exposes a clean hierarchy of custom exceptions for specific API errors.

Declarative Configuration: Uses `pydantic-settings` to manage configuration from environment variables or `.env` files.

Companion CLI: Includes a powerful command-line tool (`offers-cli`) for easy interaction and testing.

## Installation
```bash
pip install offers-sdk-applift
```

## Configuration
The SDK is configured via environment variables. The easiest way to manage this during local development is to create a .env file in the root of your project.

Create a file named .env and add the following variables:
```env
# .env file

# [REQUIRED] Your long-lived refresh token for the Offers API.
OFFERS_SDK_REFRESH_TOKEN="your-super-secret-refresh-token-goes-here"

# [OPTIONAL] Override the default API base URL.
# OFFERS_API_BASE_URL="https://staging-api.example.com/api/v1"

# [OPTIONAL] Configure token lifetime and refresh buffer in seconds.
# TOKEN_EXPIRATION_SECONDS=300
# TOKEN_EXPIRATION_BUFFER_SECONDS=30
```

The SDK will automatically load variables from this file.

## Quickstart
Here is a quick example of how to use the async client to register a product and retrieve its offers.

```python
from dotenv import load_dotenv
load_dotenv()  # Load .env needed before initialization of SDK

import asyncio
import uuid
from offers_sdk_applift import HttpxOffersClient, APIError

async def main():
    """
    A simple demonstration of the async client.
    """
    product_id = uuid.uuid4()
    
    # The client is an async context manager to ensure connections are closed.
    async with HttpxOffersClient.from_credentials(
        refresh_token="your-super-secret-refresh-token"
    ) as client:
        try:
            # 1. Register a new product
            print(f"Registering new product: {product_id}")
            product = await client.register_product(
                product_id=product_id,
                name="Awesome Gadget",
                description="The latest and greatest gadget."
            )
            print(f"-> Successfully registered with ID: {product.id}")

            # 2. Retrieve offers for the new product
            print(f"\nFetching offers for product: {product.id}")
            offers = await client.get_offers(product_id=product.id)
            
            if not offers:
                print("-> No offers found for this product.")
            else:
                print(f"-> Found {len(offers)} offer(s):")
                for offer in offers:
                    print(f"  - Offer ID: {offer.id}, Price: {offer.price}, Stock: {offer.items_in_stock}")

        except APIError as e:
            print(f"An API error occurred: Status {e.status_code}, Message: {e.message}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # Ensure you have set your OFFERS_SDK_REFRESH_TOKEN in your environment or a .env file
    asyncio.run(main())

```

## Usage
The SDK provides both an asynchronous and a synchronous client.

### Asynchronous Client (`HttpxOffersClient`)
This is the primary, high-performance client. It should be used with `async` with and `await`.

```python
import uuid
from offers_sdk_applift import HttpxOffersClient
from offers_sdk_applift.exceptions import ProductNotFoundError

async def manage_offers():
    # Use the factory to create a client. It will load the token
    # from the environment automatically.
    async with HttpxOffersClient.from_credentials(refresh_token="your-super-secret-refresh-token") as client:
        try:
            offers = await client.get_offers(uuid.uuid4())
            # ... process offers
        except ProductNotFoundError:
            print("That product could not be found.")
```

### Synchronous Client (`SyncOffersClient`)

For use in standard synchronous Python code (e.g., a simple script, a Flask app). It provides the same functionality with a blocking interface.

```python
import uuid
from offers_sdk_applift import SyncOffersClient # Note: This is the final name we decided on
from offers_sdk_applift.exceptions import ProductAlreadyExistsError

def manage_offers_sync():
    # The sync client works as a standard context manager
    with SyncOffersClient.from_credentials(refresh_token="your-super-secret-refresh-token") as client:
        try:
            product_id = uuid.uuid4()
            client.register_product(
                product_id=product_id,
                name="Sync Gadget",
                description="Registered from a sync script."
            )
        except ProductAlreadyExistsError:
            print("This product has already been registered.")
```

## Command-Line Interface (CLI)
The SDK includes a powerful CLI for easy interaction.

### Prerequisites:

Make sure you have installed the package (pip install offers-sdk).

Make sure your OFFERS_SDK_REFRESH_TOKEN is set in your environment or .env file.

### Usage:
```bash
# Get help for all available commands
offers-cli --help

# Register a new product
offers-cli register --name "My CLI Product" --description "Created from the terminal"
#> Generated new Product ID: a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d
#> ✓ Success! Product registered with ID: a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d

# Get offers for the product you just created
offers-cli get-offers a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d
```
## Advanced Usage (Testing and Dependency Injection)
The SDK is built with abstract interfaces (Protocols) to make testing your own application easy. You can type-hint against the interface and inject a fake client in your tests.

### Your Application Code:
```python
from offers_sdk_applift.interfaces import OffersClientInterface # Depend on the interface!
from offers_sdk_applift.models import Offer

async def get_cheapest_offer(client: OffersClientInterface, product_id) -> Offer | None:
    """This function is decoupled from the real client and is easy to test."""
    offers = await client.get_offers(product_id)
    if not offers:
        return None
    return min(offers, key=lambda offer: offer.price)
```

### Your Test Code:
```python
from offers_sdk_applift.interfaces import OffersClientInterface

class FakeOffersClient(OffersClientInterface):
    """A fake client for testing that conforms to the interface."""
    async def get_offers(self, product_id) -> list:
        # Return dummy data, no network call is made.
        return [...] 
    # ... other required methods ...

async def test_my_app_logic():
    fake_client = FakeOffersClient()
    cheapest = await get_cheapest_offer(client=fake_client, product_id=...)
    # ... assert the result ...
```