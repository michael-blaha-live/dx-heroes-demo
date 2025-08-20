import asyncio
import uuid
from typing import Optional

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from .clients import HttpxOffersClient
from .interfaces import OffersClientInterface
from .config import get_settings
from .exceptions import APIError, ProductNotFoundError


app = typer.Typer(
    name="offers-cli",
    help="A CLI for the Offers SDK to register products and retrieve offers.",
    add_completion=False,
)
console = Console()


def get_client() -> OffersClientInterface:
    """
    A helper function to create a configured client instance.
    """
    try:
        settings = get_settings()
        # We call the factory method on the CONCRETE class.
        return HttpxOffersClient.from_credentials(
            refresh_token=settings.OFFERS_SDK_REFRESH_TOKEN
        )
    except ValidationError as e:
        console.print("[bold red]Configuration Error:[/bold red]")
        console.print(f"[dim]{e}[/dim]")
        raise typer.Exit(code=1)


async def _register_async(
    name: str, description: str, product_id: Optional[uuid.UUID]
):
    if product_id is None:
        product_id = uuid.uuid4()
        console.print(f"Generated new Product ID: [cyan]{product_id}[/cyan]")
    
    client = get_client()
    try:
        async with client:
            with console.status("[bold green]Registering product...[/bold green]"):
                product = await client.register_product(
                    product_id=product_id, name=name, description=description
                )
        console.print(
            f"[bold green]✓ Success![/bold green] Product registered with ID: [bold cyan]{product.id}[/bold cyan]"
        )
    except APIError as e:
        console.print(f"[bold red]API Error ({e.status_code}):[/bold red] {e.message}")
        raise typer.Exit(code=1)


async def _get_offers_async(product_id: uuid.UUID):
    client = get_client()
    try:
        async with client:
            with console.status(f"[bold green]Fetching offers for {product_id}...[/bold green]"):
                offers = await client.get_offers(product_id=product_id)

        if not offers:
            console.print(f"[yellow]No offers found for product {product_id}.[/yellow]")
            return

        table = Table(title=f"Offers for Product [cyan]{product_id}[/cyan]")
        table.add_column("Offer ID", style="magenta", no_wrap=True)
        table.add_column("Price", style="green")
        table.add_column("Items in Stock", justify="right", style="blue")

        for offer in offers:
            table.add_row(str(offer.id), str(offer.price), str(offer.items_in_stock))

        console.print(table)
    except ProductNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Product with ID [cyan]{product_id}[/cyan] not found.")
        raise typer.Exit(code=1)
    except APIError as e:
        console.print(f"[bold red]API Error ({e.status_code}):[/bold red] {e.message}")
        raise typer.Exit(code=1)


# --- Synchronous CLI Commands ---
# These are the functions Typer will call. They are synchronous.

@app.command()
def register(
    name: str = typer.Option(..., "--name", "-n", help="The name of the product to register."),
    description: str = typer.Option(..., "--description", "-d", help="A description for the product."),
    product_id: Optional[uuid.UUID] = typer.Option(None, "--id", help="Optional UUID for the product."),
):
    """Register a new product with the Offers service."""
    # The sync function's only job is to run the async version.
    asyncio.run(_register_async(name, description, product_id))


@app.command()
def get_offers(
    product_id: uuid.UUID = typer.Argument(..., help="The UUID of the product to retrieve offers for.")
):
    """Get all available offers for a given product ID."""
    asyncio.run(_get_offers_async(product_id))