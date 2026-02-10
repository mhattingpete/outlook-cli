"""Debug: test interactive browser-based auth flow (alternative to device code).

This uses MSAL's acquire_token_interactive which opens a local browser window
and runs a temporary HTTP server to receive the redirect. This is the same
approach used by outlook-mcp and avoids the device-code flow entirely.

If successful the token cache is saved to ~/.outlook-cli/o365_token so the
O365 library can pick it up for subsequent calls.
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from msal import PublicClientApplication, SerializableTokenCache

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

CLIENT_ID = os.environ["CLIENT_ID"]
TENANT_ID = os.environ["TENANT_ID"]
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

SCOPES = [
    "https://graph.microsoft.com/Mail.ReadWrite",
    "https://graph.microsoft.com/Mail.Send",
    "https://graph.microsoft.com/Calendars.ReadWrite",
]

TOKEN_DIR = Path.home() / ".outlook-cli"
TOKEN_FILE = TOKEN_DIR / "o365_token"

# ---------------------------------------------------------------------------
# Token cache helpers
# ---------------------------------------------------------------------------


def load_cache() -> SerializableTokenCache:
    """Load an existing token cache from disk, if available."""
    cache = SerializableTokenCache()
    if TOKEN_FILE.exists():
        cache.deserialize(TOKEN_FILE.read_text())
    return cache


def save_cache(cache: SerializableTokenCache) -> None:
    """Persist the token cache so O365 can reuse it."""
    if cache.has_state_changed:
        TOKEN_DIR.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(cache.serialize())
        TOKEN_FILE.chmod(0o600)
        print(f"Token cache saved to {TOKEN_FILE}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 60)
    print("Interactive Browser Auth (MSAL acquire_token_interactive)")
    print("=" * 60)
    print(f"Client ID : {CLIENT_ID}")
    print(f"Tenant ID : {TENANT_ID}")
    print(f"Authority : {AUTHORITY}")
    print(f"Scopes    : {SCOPES}")
    print(f"Token file: {TOKEN_FILE}")
    print()

    cache = load_cache()
    app = PublicClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache,
    )

    # Try silent auth first (cached tokens)
    accounts = app.get_accounts()
    result = None

    if accounts:
        print(f"Found {len(accounts)} cached account(s) -- trying silent auth...")
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            print("Silent auth succeeded (reused cached token).\n")

    if not result or "access_token" not in result:
        print("Opening browser for interactive sign-in...")
        print("(If the browser does not open, check your default-browser setting.)\n")
        result = app.acquire_token_interactive(
            scopes=SCOPES,
            prompt="select_account",
        )

    # Save regardless of outcome -- cache state may have changed
    save_cache(cache)

    # Report result
    if "access_token" in result:
        claims = result.get("id_token_claims", {})
        username = claims.get("preferred_username", "unknown")
        name = claims.get("name", "unknown")
        token_preview = result["access_token"][:40] + "..."

        print("SUCCESS!")
        print(f"  Name    : {name}")
        print(f"  Account : {username}")
        print(f"  Token   : {token_preview}")
        print(f"  Scopes  : {result.get('scope', 'N/A')}")

        # Also dump the full token cache as pretty JSON for inspection
        print(f"\nToken cache contents ({TOKEN_FILE}):")
        cache_data = json.loads(cache.serialize())
        for section, entries in cache_data.items():
            if entries:
                print(f"  {section}: {len(entries)} entries")
    else:
        print("FAILED!")
        print(f"  Error      : {result.get('error', 'unknown')}")
        print(f"  Description: {result.get('error_description', 'N/A')}")
        print(f"  Correlation: {result.get('correlation_id', 'N/A')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
