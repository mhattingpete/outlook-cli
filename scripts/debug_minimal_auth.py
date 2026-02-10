"""Debug: test device code flow with the absolute minimum scope (User.Read).

This isolates whether device-code flow works at all for the registered app,
independent of Mail/Calendar permissions.  If this succeeds but the full-scope
debug_auth.py fails, the problem is scope-related (admin consent, etc.).
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from msal import PublicClientApplication

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

CLIENT_ID = os.environ["CLIENT_ID"]
TENANT_ID = os.environ["TENANT_ID"]
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

# Absolute minimum -- just read the signed-in user's profile.
SCOPES = [
    "https://graph.microsoft.com/User.Read",
]

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 60)
    print("Minimal Device-Code Auth (User.Read only)")
    print("=" * 60)
    print(f"Client ID : {CLIENT_ID}")
    print(f"Tenant ID : {TENANT_ID}")
    print(f"Authority : {AUTHORITY}")
    print(f"Scopes    : {SCOPES}")
    print()

    app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    flow = app.initiate_device_flow(scopes=SCOPES)

    if "user_code" not in flow:
        print(f"ERROR initiating device flow: {flow.get('error_description', 'unknown')}")
        print(f"Full response: {flow}")
        sys.exit(1)

    print(f"Visit : {flow['verification_uri']}")
    print(f"Code  : {flow['user_code']}")
    print()
    print("Waiting for authentication (timeout ~15 min)...")

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        claims = result.get("id_token_claims", {})
        username = claims.get("preferred_username", "unknown")
        name = claims.get("name", "unknown")

        print()
        print("SUCCESS!")
        print(f"  Name    : {name}")
        print(f"  Account : {username}")
        print(f"  Scopes  : {result.get('scope', 'N/A')}")
        print()
        print("Device code flow works with User.Read.")
        print("If debug_auth.py fails, the issue is with the broader scopes")
        print("(Mail.ReadWrite, Mail.Send, Calendars.ReadWrite) -- likely")
        print("admin consent is required for those permissions.")
    else:
        print()
        print("FAILED!")
        print(f"  Error      : {result.get('error', 'unknown')}")
        print(f"  Description: {result.get('error_description', 'N/A')}")
        print(f"  Correlation: {result.get('correlation_id', 'N/A')}")
        print()
        print("Device code flow does not work even with minimal scope.")
        print("This suggests the app registration itself has an issue:")
        print("  - 'Allow public client flows' may be disabled in Azure AD")
        print("  - The app registration may not have User.Read delegated permission")
        print("  - The tenant may block device-code flow via Conditional Access")
        sys.exit(1)


if __name__ == "__main__":
    main()
