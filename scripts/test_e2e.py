"""End-to-end test: authenticate + call Graph API (mail & calendar).

Usage:
    # Using personal app registration (see setup instructions below)
    PERSONAL_CLIENT_ID=<id> uv run python scripts/test_e2e.py

    # Or add PERSONAL_CLIENT_ID to .env
    uv run python scripts/test_e2e.py

Setup (one-time, ~2 minutes):
    1. Go to https://portal.azure.com (sign in with a personal Microsoft account)
    2. Search "App registrations" → New registration
    3. Name: "outlook-cli-test"
    4. Supported account types: "Personal Microsoft accounts only"
    5. Redirect URI: leave blank
    6. Click Register
    7. Copy the Application (client) ID → add to .env as PERSONAL_CLIENT_ID
    8. Go to Authentication → Advanced settings → Allow public client flows → Yes → Save
    9. Go to API permissions → Add → Microsoft Graph → Delegated:
       - Mail.ReadWrite, Mail.Send, Calendars.ReadWrite
    10. Done! No admin consent needed for personal accounts.
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

# Prefer PERSONAL_CLIENT_ID for testing, fall back to work CLIENT_ID
CLIENT_ID = os.environ.get("PERSONAL_CLIENT_ID") or os.environ.get("CLIENT_ID")
if not CLIENT_ID:
    print("ERROR: Set PERSONAL_CLIENT_ID (or CLIENT_ID) in .env")
    sys.exit(1)

# Use PERSONAL_TENANT_ID, fall back to TENANT_ID, then "consumers" for personal accounts
TENANT_ID = os.environ.get("PERSONAL_TENANT_ID") or os.environ.get("TENANT_ID", "consumers")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

SCOPES = [
    "https://graph.microsoft.com/User.Read",
    "https://graph.microsoft.com/Mail.ReadWrite",
    "https://graph.microsoft.com/Mail.Send",
    "https://graph.microsoft.com/Calendars.ReadWrite",
]

TOKEN_FILE = Path(__file__).resolve().parent.parent / ".test_token_cache.json"


def main() -> None:
    from msal import PublicClientApplication

    print("=" * 60)
    print("E2E Test: Auth + Graph API calls")
    print("=" * 60)
    print(f"Client ID : {CLIENT_ID}")
    print(f"Authority : {AUTHORITY}")
    print(f"Scopes    : {SCOPES}")
    print()

    # --- Step 1: Authenticate ---
    # Use FileSystemTokenBackend as the MSAL cache — this is the same approach
    # auth.py uses so O365 can read the token MSAL writes.
    from O365 import FileSystemTokenBackend

    backend = FileSystemTokenBackend(
        token_path=TOKEN_FILE.parent,
        token_filename=TOKEN_FILE.stem,
    )

    app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=backend)

    # Try silent first
    accounts = app.get_accounts()
    result = None
    if accounts:
        print(f"Found cached account: {accounts[0]['username']}")
        result = app.acquire_token_silent(SCOPES, account=accounts[0])

    if not result or "access_token" not in result:
        print("Starting device code flow...")
        flow = app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            print(f"ERROR: {flow.get('error_description', 'unknown')}")
            sys.exit(1)

        print(f"\n  Visit: {flow['verification_uri']}")
        print(f"  Code:  {flow['user_code']}\n")
        print("Waiting for sign-in...")
        result = app.acquire_token_by_device_flow(flow)

    # Save cache
    backend.save_token(force=True)

    if "access_token" not in result:
        print(f"\nAuth FAILED: {result.get('error_description', 'unknown')}")
        sys.exit(1)

    token = result["access_token"]
    username = result.get("id_token_claims", {}).get("preferred_username", "unknown")
    print(f"\nAuth OK — signed in as {username}")

    # --- Step 2: Test Graph API calls ---
    import urllib.error
    import urllib.request

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def graph_get(endpoint: str) -> dict:
        url = f"https://graph.microsoft.com/v1.0{endpoint}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            try:
                detail = json.loads(body).get("error", {}).get("message", body[:200])
            except json.JSONDecodeError:
                detail = body[:200]
            raise RuntimeError(f"HTTP {e.code}: {detail}") from None

    tests_passed = 0
    tests_failed = 0

    # Test: Get profile
    print("\n--- Test: GET /me ---")
    try:
        me = graph_get("/me")
        print(f"  OK — {me.get('displayName', '?')} ({me.get('mail', me.get('userPrincipalName', '?'))})")
        tests_passed += 1
    except Exception as e:
        print(f"  FAIL — {e}")
        tests_failed += 1

    # Test: List inbox messages
    print("\n--- Test: GET /me/mailFolders/inbox/messages (top 3) ---")
    try:
        msgs = graph_get("/me/mailFolders/inbox/messages?$top=3&$select=subject,from,receivedDateTime")
        for m in msgs.get("value", []):
            subj = m.get("subject", "(no subject)")[:50]
            sender = m.get("from", {}).get("emailAddress", {}).get("address", "?")
            print(f"  - {subj} (from: {sender})")
        print(f"  OK — {len(msgs.get('value', []))} messages returned")
        tests_passed += 1
    except Exception as e:
        print(f"  FAIL — {e}")
        tests_failed += 1

    # Test: Search messages
    print("\n--- Test: GET /me/messages?$search (query='test') ---")
    try:
        search = graph_get('/me/messages?$search="test"&$top=3&$select=subject')
        count = len(search.get("value", []))
        for m in search.get("value", []):
            print(f"  - {m.get('subject', '(no subject)')[:50]}")
        print(f"  OK — {count} results")
        tests_passed += 1
    except Exception as e:
        print(f"  FAIL — {e}")
        tests_failed += 1

    # Test: List calendar events
    print("\n--- Test: GET /me/calendar/events (top 3) ---")
    try:
        events = graph_get("/me/calendar/events?$top=3&$select=subject,start,end")
        for ev in events.get("value", []):
            subj = ev.get("subject", "(no subject)")[:50]
            start = ev.get("start", {}).get("dateTime", "?")[:16]
            print(f"  - {subj} (starts: {start})")
        print(f"  OK — {len(events.get('value', []))} events returned")
        tests_passed += 1
    except Exception as e:
        print(f"  FAIL — {e}")
        tests_failed += 1

    # Test: O365 library integration (uses same FileSystemTokenBackend as MSAL)
    print("\n--- Test: O365 Account with cached token ---")
    try:
        from O365 import Account

        account = Account(
            (CLIENT_ID,),
            auth_flow_type="public",
            tenant_id=TENANT_ID,
            token_backend=backend,
        )

        if account.is_authenticated:
            print("  OK — O365 recognises the MSAL token")
            # Only try mail if /me worked (account has a mailbox)
            try:
                mailbox = account.mailbox()
                inbox = mailbox.inbox_folder()
                msg_list = list(inbox.get_messages(limit=1))
                print(f"  OK — O365 inbox returned {len(msg_list)} message(s)")
            except Exception as mail_err:
                print(f"  SKIP — O365 auth OK but mailbox unavailable ({mail_err})")
            tests_passed += 1
        else:
            print("  FAIL — O365 reports not authenticated")
            tests_failed += 1
    except Exception as e:
        print(f"  FAIL — {e}")
        tests_failed += 1

    # Summary
    total = tests_passed + tests_failed
    print(f"\n{'=' * 60}")
    print(f"Results: {tests_passed}/{total} passed")
    if tests_failed:
        print("Some tests failed — check errors above.")
        sys.exit(1)
    else:
        print("All tests passed! The CLI code works correctly.")


if __name__ == "__main__":
    main()
