"""O365 authentication with device code flow."""

import sys

from O365 import Account, FileSystemTokenBackend

from outlook_cli.config import get_config_dir, load_config
from outlook_cli.display import print_error


SCOPES = ["message_all", "calendar_all"]
TOKEN_FILENAME = "o365_token"


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


def authenticate(client_id: str, tenant_id: str = "common") -> bool:
    """Run device code auth flow. Returns True on success."""
    account = _build_account(client_id, tenant_id)
    return account.authenticate(scopes=SCOPES)


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
