from typer.testing import CliRunner
from respx import MockRouter

from offers_sdk.cli import app
from offers_sdk.interfaces import OffersClientInterface


runner = CliRunner()


def test_cli_register_success(
    monkeypatch, respx_mock: MockRouter, offers_client: OffersClientInterface
):
    """
    Tests a successful run of the 'register' command.
    """
    # Mock the API endpoint that the underlying client will call
    respx_mock.post(url__regex=r".*/products/register").respond(
        201, json={"id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"}
    )
    # Inject our fully mocked client into the CLI
    monkeypatch.setattr("offers_sdk.cli.get_client", lambda: offers_client)

    # FIX: Provide ALL required options, including --description
    result = runner.invoke(
        app,
        [
            "register",
            "--name",
            "CLI Test Product",
            "--description",
            "A product for the test.",
        ],
    )

    # Assert the command succeeded and printed the right output
    assert result.exit_code == 0, f"CLI failed: {result.exception}\n{result.stdout}"

    assert "Success!" in result.stdout
    assert "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d" in result.stdout
