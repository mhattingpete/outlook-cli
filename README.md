# outlook-cli

A command-line tool for Microsoft Outlook (Work/School accounts). Search, read, send, and reply to emails. List, read, and create calendar events. Built with the [O365](https://github.com/O365/python-o365) library and [Typer](https://typer.tiangolo.com/).

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- An Azure App Registration (free) with **Microsoft Graph** delegated permissions:
  - `Mail.ReadWrite`
  - `Mail.Send`
  - `Calendars.ReadWrite`

### Azure App Setup

1. Go to [Azure Portal > App registrations](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)
2. Click **New registration**
3. Name it anything (e.g. "Outlook CLI"), set **Supported account types** to your preference
4. Under **Authentication > Advanced settings**, set **Allow public client flows** to **Yes** and save
5. Under **API permissions**, add the three **Delegated** permissions listed above
6. If your tenant requires admin consent, have an admin grant consent for the app
7. Copy the **Application (client) ID** — you'll need it for `outlook auth login`

## Installation

```bash
git clone https://github.com/mhattingpete/outlook-cli.git
cd outlook-cli
uv sync
```

## Getting Started

```bash
# Authenticate with your Azure app
outlook auth login --client-id YOUR_CLIENT_ID

# Follow the device code flow — open the URL and enter the code

# Check status
outlook auth status
```

## Commands

### Authentication

```bash
outlook auth login [--client-id ID] [--tenant-id ID]   # Authenticate via device code flow
outlook auth logout                                      # Remove stored token
outlook auth status                                      # Show auth status and config
```

### Email

```bash
# Search / list messages
outlook mail search                                      # List recent inbox messages
outlook mail search "quarterly report"                   # Full-text search
outlook mail search --unread                             # Unread messages only
outlook mail search --from alice@company.com             # Filter by sender
outlook mail search --start-date 2025-01-01 --end-date 2025-02-01
outlook mail search --important --has-attachments        # Combine filters
outlook mail search --folder "Sent Items" --limit 10     # Different folder

# Read a message
outlook mail read MESSAGE_ID

# Send a message
outlook mail send --to bob@company.com --subject "Hello" --body "Hi Bob!"
outlook mail send --to bob@company.com --cc carol@company.com --subject "Update" --body "FYI"

# Reply to a message
outlook mail reply MESSAGE_ID --body "Thanks for the update!"
outlook mail reply MESSAGE_ID --body "Noted, thanks." --reply-all

# Mark as read/unread
outlook mail mark MESSAGE_ID                             # Mark as read (default)
outlook mail mark MESSAGE_ID --unread                    # Mark as unread
```

### Calendar

```bash
# List events (default: next 7 days)
outlook cal list
outlook cal list --start 2025-03-01 --end 2025-03-31    # Custom date range
outlook cal list --subject "standup"                     # Filter by subject
outlook cal list --location "Room A"                     # Filter by location
outlook cal list --all-day                               # All-day events only
outlook cal list --recurring                             # Recurring events only
outlook cal list --organizer boss@company.com            # Filter by organizer

# Read event details (shows attendees, recurrence, etc.)
outlook cal read EVENT_ID

# Create an event
outlook cal create --subject "Lunch" --start "2025-02-08 12:00" --end "2025-02-08 13:00"
outlook cal create --subject "Workshop" \
  --start "2025-02-10 09:00" --end "2025-02-10 17:00" \
  --body "Full day workshop" --location "Conference Room B"
```

## Configuration

Config and tokens are stored in `~/.outlook-cli/`:

```
~/.outlook-cli/
├── config.toml          # client_id, tenant_id
└── o365_token.token     # OAuth token (auto-managed)
```

## Development

```bash
# Install dev dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Run the CLI
uv run outlook --help
```

## License

MIT
