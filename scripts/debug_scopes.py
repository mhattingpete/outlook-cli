"""Debug: see what scopes O365 expands to."""
from O365 import Account

account = Account(("fake",), auth_flow_type="public", tenant_id="common")

# What our current SCOPES expand to:
for scope_helper in ["message_all", "calendar_all"]:
    expanded = account.protocol.get_scopes_for([scope_helper])
    print(f"{scope_helper} -> {expanded}")

# Full expansion
full = account.protocol.get_scopes_for(["message_all", "calendar_all"])
print(f"\nFull expansion ({len(full)} scopes):")
for s in sorted(full):
    print(f"  {s}")
