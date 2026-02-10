"""O365 authentication with device code flow via MSAL."""

import sys

from msal import PublicClientApplication
from O365 import Account, FileSystemTokenBackend

from outlook_cli.config import get_config_dir, load_config
from outlook_cli.display import console, print_error


SCOPES = ["message_all", "calendar_all"]
TOKEN_FILENAME = "o365_token"
MSAL_AUTHORITY = "https://login.microsoftonline.com/{tenant_id}"


def _token_backend() -> FileSystemTokenBackend:
    return FileSystemTokenBackend(
        token_path=get_config_dir(),
        token_filename=TOKEN_FILENAME,
    )


def _build_account(client_id: str, tenant_id: str = "common") -> Account:
    return Account(
        (client_id,),
        auth_flow_type="public",
        tenant_id=tenant_id,
        token_backend=_token_backend(),
    )


def _get_graph_scopes(client_id: str, tenant_id: str = "common") -> list[str]:
    """Convert O365 scope helpers to full Microsoft Graph scope URLs."""
    account = _build_account(client_id, tenant_id)
    return account.protocol.get_scopes_for(SCOPES)


def authenticate(client_id: str, tenant_id: str = "common") -> bool:
    """Run device code auth flow using MSAL. Returns True on success."""
    backend = _token_backend()
    scopes = _get_graph_scopes(client_id, tenant_id)
    authority = MSAL_AUTHORITY.format(tenant_id=tenant_id)

    app = PublicClientApplication(
        client_id,
        authority=authority,
        token_cache=backend,
    )

    flow = app.initiate_device_flow(scopes=scopes)
    if "user_code" not in flow:
        print_error(f"Device code flow failed: {flow.get('error_description', 'unknown error')}")
        return False

    console.print(f"\n[bold]To sign in, visit:[/] [link]{flow['verification_uri']}[/link]")
    console.print(f"[bold]Enter code:[/] [bold cyan]{flow['user_code']}[/bold cyan]\n")

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        backend.save_token(force=True)
        return True

    print_error(result.get("error_description", "Authentication failed."))
    return False


def is_authenticated() -> bool:
    """Check whether a valid token exists."""
    config = load_config()
    client_id = config.get("client_id")
    if not client_id:
        return False

    account = _build_account(client_id, config.get("tenant_id", "common"))
    return account.is_authenticated


def get_account() -> Account:
    """Return an authenticated Account or exit with an error."""
    config = load_config()
    client_id = config.get("client_id")

    if not client_id:
        print_error("Not configured. Run: outlook auth login --client-id <ID>")
        sys.exit(1)

    account = _build_account(client_id, config.get("tenant_id", "common"))

    if not account.is_authenticated:
        print_error("Not authenticated. Run: outlook auth login")
        sys.exit(1)

    return account
