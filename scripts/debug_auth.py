"""Debug: test device code flow."""
import os
from pathlib import Path

from dotenv import load_dotenv
from msal import PublicClientApplication

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

CLIENT_ID = os.environ["CLIENT_ID"]
TENANT_ID = os.environ["TENANT_ID"]
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

SCOPES = [
    "https://graph.microsoft.com/Mail.ReadWrite",
    "https://graph.microsoft.com/Mail.Send",
    "https://graph.microsoft.com/Calendars.ReadWrite",
]

print(f"Client: {CLIENT_ID}")
print(f"Tenant: {TENANT_ID}")
print(f"Scopes: {SCOPES}")
print()

app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
flow = app.initiate_device_flow(scopes=SCOPES)

if "user_code" not in flow:
    print(f"ERROR: {flow.get('error_description', 'unknown')}")
    exit(1)

print(f"Visit: {flow['verification_uri']}")
print(f"Code:  {flow['user_code']}")
print()
print("Waiting for authentication...")

result = app.acquire_token_by_device_flow(flow)

if "access_token" in result:
    print(f"\nSUCCESS!")
    print(f"Account: {result.get('id_token_claims', {}).get('preferred_username', 'unknown')}")
else:
    print(f"\nFAILED: {result.get('error')}")
    print(f"Detail: {result.get('error_description')}")
