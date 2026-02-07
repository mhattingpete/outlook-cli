"""Shared test fixtures."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture()
def config_dir(tmp_path, monkeypatch):
    """Redirect config dir to a temp directory."""
    import outlook_cli.config as config_mod

    monkeypatch.setattr(config_mod, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(config_mod, "CONFIG_FILE", tmp_path / "config.toml")
    return tmp_path


@pytest.fixture()
def mock_account():
    """Return a MagicMock that mimics an O365 Account."""
    account = MagicMock()
    account.is_authenticated = True

    # Mailbox
    mailbox = MagicMock()
    account.mailbox.return_value = mailbox
    inbox = MagicMock()
    mailbox.inbox_folder.return_value = inbox

    # Calendar
    schedule = MagicMock()
    account.schedule.return_value = schedule
    calendar = MagicMock()
    schedule.get_default_calendar.return_value = calendar

    return account


@pytest.fixture()
def mock_message():
    """Return a MagicMock that mimics an O365 Message."""
    msg = MagicMock()
    msg.sender = "alice@example.com"
    msg.subject = "Test Subject"
    msg.received = MagicMock()
    msg.received.strftime.return_value = "2025-02-07 10:00"
    msg.object_id = "msg-123"
    msg.to = ["bob@example.com"]
    msg.cc = []
    msg.body = "Hello, world!"
    return msg


@pytest.fixture()
def mock_event():
    """Return a MagicMock that mimics an O365 Event."""
    event = MagicMock()
    event.subject = "Team Meeting"
    event.start = MagicMock()
    event.start.strftime.return_value = "2025-02-08 10:00"
    event.end = MagicMock()
    event.end.strftime.return_value = "2025-02-08 11:00"
    event.location = {"displayName": "Room 1"}
    event.object_id = "evt-456"
    event.body = "Weekly sync"
    return event
