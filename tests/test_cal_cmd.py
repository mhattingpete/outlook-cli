"""CLI integration tests for calendar commands."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from outlook_cli.main import app

runner = CliRunner()


@patch("outlook_cli.commands.cal_cmd.get_account")
def test_list_no_events(mock_get, mock_account):
    mock_get.return_value = mock_account
    calendar = mock_account.schedule().get_default_calendar()
    calendar.get_events.return_value = iter([])

    result = runner.invoke(app, ["cal", "list"])
    assert result.exit_code == 0
    assert "no events" in result.output.lower()


@patch("outlook_cli.commands.cal_cmd.get_account")
def test_list_with_events(mock_get, mock_account, mock_event):
    mock_get.return_value = mock_account
    calendar = mock_account.schedule().get_default_calendar()
    calendar.get_events.return_value = iter([mock_event])

    result = runner.invoke(app, ["cal", "list"])
    assert result.exit_code == 0
    assert "Team Meeting" in result.output


@patch("outlook_cli.commands.cal_cmd.get_account")
def test_list_with_date_range(mock_get, mock_account, mock_event):
    mock_get.return_value = mock_account
    calendar = mock_account.schedule().get_default_calendar()
    calendar.get_events.return_value = iter([mock_event])

    result = runner.invoke(app, [
        "cal", "list",
        "--start", "2025-02-01",
        "--end", "2025-02-28",
    ])
    assert result.exit_code == 0


@patch("outlook_cli.commands.cal_cmd.get_account")
def test_read_event(mock_get, mock_account, mock_event):
    mock_get.return_value = mock_account
    calendar = mock_account.schedule().get_default_calendar()
    calendar.get_event.return_value = mock_event

    result = runner.invoke(app, ["cal", "read", "evt-456"])
    assert result.exit_code == 0
    assert "Team Meeting" in result.output


@patch("outlook_cli.commands.cal_cmd.get_account")
def test_read_event_not_found(mock_get, mock_account):
    mock_get.return_value = mock_account
    calendar = mock_account.schedule().get_default_calendar()
    calendar.get_event.return_value = None

    result = runner.invoke(app, ["cal", "read", "nonexistent"])
    assert result.exit_code != 0


@patch("outlook_cli.commands.cal_cmd.get_account")
def test_create_event(mock_get, mock_account):
    mock_get.return_value = mock_account
    calendar = mock_account.schedule().get_default_calendar()
    new_event = MagicMock()
    calendar.new_event.return_value = new_event

    result = runner.invoke(app, [
        "cal", "create",
        "--subject", "Lunch",
        "--start", "2025-02-08 12:00",
        "--end", "2025-02-08 13:00",
    ])
    assert result.exit_code == 0
    assert "lunch" in result.output.lower()
    new_event.save.assert_called_once()


@patch("outlook_cli.commands.cal_cmd.get_account")
def test_create_event_with_optional_fields(mock_get, mock_account):
    mock_get.return_value = mock_account
    calendar = mock_account.schedule().get_default_calendar()
    new_event = MagicMock()
    calendar.new_event.return_value = new_event

    result = runner.invoke(app, [
        "cal", "create",
        "--subject", "Workshop",
        "--start", "2025-02-08 09:00",
        "--end", "2025-02-08 17:00",
        "--body", "Full day workshop",
        "--location", "Conference Room A",
    ])
    assert result.exit_code == 0
    assert new_event.body == "Full day workshop"
    assert new_event.location == "Conference Room A"
