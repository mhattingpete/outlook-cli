# CLAUDE.md — outlook-cli

## Project Overview

CLI tool for Microsoft Outlook (Work/School accounts). Uses the O365 library for Microsoft Graph API access, Typer for CLI framework, and Rich for terminal formatting.

## Quick Reference

```bash
uv run pytest tests/ -v          # Run tests
uv run outlook --help             # CLI help
uv sync                           # Install dependencies
```

## Project Structure

```
src/outlook_cli/
├── main.py              # Typer app entry point, registers sub-command groups
├── config.py            # Config loading/saving (~/.outlook-cli/config.toml)
├── auth.py              # O365 Account creation, device code flow, token management
├── display.py           # Rich formatting: tables, panels, HTML stripping
└── commands/
    ├── auth_cmd.py      # outlook auth login|logout|status
    ├── mail_cmd.py      # outlook mail search|read|send|reply|mark
    └── cal_cmd.py       # outlook cal list|read|create

tests/
├── conftest.py          # Shared fixtures (mock_account, mock_message, mock_event)
├── test_config.py       # Unit: config file I/O
├── test_auth.py         # Unit: auth logic with mocked O365
├── test_display.py      # Unit: Rich output via StringIO capture
├── test_auth_cmd.py     # CLI integration: auth commands via CliRunner
├── test_mail_cmd.py     # CLI integration: core mail commands
├── test_mail_enhanced.py # CLI integration: mail filters, reply, mark
├── test_cal_cmd.py      # CLI integration: core cal commands
├── test_cal_enhanced.py # CLI integration: cal filters
└── test_main_cli.py     # CLI integration: version, help
```

## Architecture

- **Auth flow**: Device code via MSAL `PublicClientApplication`. O365's `FileSystemTokenBackend` is passed as MSAL's `token_cache` so both libraries share the same token. Token stored in `~/.outlook-cli/`.
- **CLI framework**: Typer with `add_typer()` sub-command groups. Each command module exposes an `app = typer.Typer()`.
- **Display**: Rich Console for all output. `getattr()` with defaults for safe O365 object access.
- **Config**: TOML-based (`tomllib` for reading, `tomli-w` for writing).

## Key Patterns

- **O365 query builder**: `mailbox.new_query().on_attribute("field").equals(value)` for OData filters. `mailbox.q().search("text")` for full-text search. These cannot be combined (Graph API limitation).
- **Error exits**: Commands call `print_error()` then `raise typer.Exit(1)` for user-facing errors. `auth.get_account()` calls `sys.exit(1)` if not authenticated.
- **Display safety**: All O365 object attribute access in display.py uses `getattr(obj, "attr", default)` since not all fields are always present.
- **HTML handling**: `_strip_html()` converts HTML email bodies to plain text for terminal display.

## Testing Strategy

Two layers:
1. **Unit tests**: Mock O365 at the boundary, test logic directly. Config tests use `tmp_path`.
2. **CLI integration tests**: `typer.testing.CliRunner` invokes commands, `@patch` mocks `get_account()`.

Rich output goes to its own Console (not stdout), so CLI integration tests patch display functions and assert they were called correctly rather than checking `result.output`.

## Dependencies

- `O365` — Microsoft Graph API client
- `msal` — MSAL authentication (device code flow); transitive dep of O365
- `typer` — CLI framework
- `rich` — Terminal formatting
- `tomli-w` — TOML writing
- `pytest` — Testing (dev)
- `python-dotenv` — .env loading (dev, used by debug scripts)
