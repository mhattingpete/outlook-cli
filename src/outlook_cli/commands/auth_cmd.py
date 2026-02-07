"""Auth commands: login, logout, status."""

from typing import Optional

import typer

from outlook_cli.auth import TOKEN_FILENAME, authenticate, is_authenticated
from outlook_cli.config import get_config_dir, load_config, save_config
from outlook_cli.display import console, print_error, print_success

app = typer.Typer(help="Manage authentication.")


@app.command()
def login(
    client_id: Optional[str] = typer.Option(None, "--client-id", help="Azure app client ID"),
    tenant_id: str = typer.Option("common", "--tenant-id", help="Azure tenant ID"),
) -> None:
    """Authenticate with Microsoft via device code flow."""
    config = load_config()

    if client_id:
        config["client_id"] = client_id
        config["tenant_id"] = tenant_id
        save_config(config)
    else:
        client_id = config.get("client_id")

    if not client_id:
        print_error("No client ID found. Run: outlook auth login --client-id <ID>")
        raise typer.Exit(1)

    tenant_id = config.get("tenant_id", tenant_id)

    if authenticate(client_id, tenant_id):
        print_success("Authenticated successfully.")
    else:
        print_error("Authentication failed.")
        raise typer.Exit(1)


@app.command()
def logout() -> None:
    """Remove stored credentials."""
    token_path = get_config_dir() / f"{TOKEN_FILENAME}.token"
    if token_path.exists():
        token_path.unlink()
        print_success("Logged out — token removed.")
    else:
        console.print("No token file found; already logged out.")


@app.command()
def status() -> None:
    """Show current authentication status and config."""
    config = load_config()
    client_id = config.get("client_id", "not set")
    tenant_id = config.get("tenant_id", "not set")

    console.print(f"[bold]Client ID:[/] {client_id}")
    console.print(f"[bold]Tenant ID:[/] {tenant_id}")

    if is_authenticated():
        print_success("Authenticated.")
    else:
        print_error("Not authenticated.")
