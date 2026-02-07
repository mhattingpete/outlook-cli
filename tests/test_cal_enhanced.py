"""CLI integration tests for enhanced calendar commands: list filters."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from outlook_cli.main import app

runner = CliRunner()


# ── List with filters ─────────────────────────────────────────


@patch("outlook_cli.commands.cal_cmd.get_account")
def test_list_subject_filter(mock_get, mock_account):
    mock_get.return_value = mock_account
    calendar = mock_account.schedule().get_default_calendar()
    calendar.get_events.return_value = iter([])

    result = runner.invoke(app, ["cal", "list", "--subject", "meeting"])
    assert result.exit_code == 0
    calendar.get_events.assert_called_once()


@patch("outlook_cli.commands.cal_cmd.get_account")
def test_list_location_filter(mock_get, mock_account):
    mock_get.return_value = mock_account
    calendar = mock_account.schedule().get_default_calendar()
    calendar.get_events.return_value = iter([])

    result = runner.invoke(app, ["cal", "list", "--location", "Room"])
    assert result.exit_code == 0
    calendar.get_events.assert_called_once()


@patch("outlook_cli.commands.cal_cmd.get_account")
def test_list_all_day_filter(mock_get, mock_account):
    mock_get.return_value = mock_account
    calendar = mock_account.schedule().get_default_calendar()
    calendar.get_events.return_value = iter([])

    result = runner.invoke(app, ["cal", "list", "--all-day"])
    assert result.exit_code == 0
    calendar.get_events.assert_called_once()


@patch("outlook_cli.commands.cal_cmd.get_account")
def test_list_recurring_filter(mock_get, mock_account):
    mock_get.return_value = mock_account
    calendar = mock_account.schedule().get_default_calendar()
    calendar.get_events.return_value = iter([])

    result = runner.invoke(app, ["cal", "list", "--recurring"])
    assert result.exit_code == 0
    calendar.get_events.assert_called_once()


@patch("outlook_cli.commands.cal_cmd.get_account")
def test_list_combined_filters(mock_get, mock_account):
    """Multiple filters can be combined in a single query."""
    mock_get.return_value = mock_account
    calendar = mock_account.schedule().get_default_calendar()
    calendar.get_events.return_value = iter([])

    result = runner.invoke(app, [
        "cal", "list",
        "--subject", "standup",
        "--recurring",
    ])
    assert result.exit_code == 0
    calendar.get_events.assert_called_once()


@patch("outlook_cli.commands.cal_cmd.get_account")
def test_list_subject_filter_with_results(mock_get, mock_account, mock_event):
    mock_get.return_value = mock_account
    calendar = mock_account.schedule().get_default_calendar()
    calendar.get_events.return_value = iter([mock_event])

    result = runner.invoke(app, ["cal", "list", "--subject", "Team"])
    assert result.exit_code == 0
    assert "Team Meeting" in result.output


@patch("outlook_cli.commands.cal_cmd.get_account")
def test_list_organizer_filter(mock_get, mock_account):
    mock_get.return_value = mock_account
    calendar = mock_account.schedule().get_default_calendar()
    calendar.get_events.return_value = iter([])

    result = runner.invoke(app, ["cal", "list", "--organizer", "boss@example.com"])
    assert result.exit_code == 0
    calendar.get_events.assert_called_once()


@patch("outlook_cli.commands.cal_cmd.get_account")
def test_list_all_day_no_results(mock_get, mock_account):
    mock_get.return_value = mock_account
    calendar = mock_account.schedule().get_default_calendar()
    calendar.get_events.return_value = iter([])

    result = runner.invoke(app, ["cal", "list", "--all-day"])
    assert result.exit_code == 0
    assert "no events" in result.output.lower()
