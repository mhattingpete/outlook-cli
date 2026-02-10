"""CLI integration tests for enhanced mail commands: search filters, reply, mark."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from outlook_cli.main import app

runner = CliRunner()


# ── Search with filters ──────────────────────────────────────


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_search_unread_filter(mock_get, mock_account):
    mock_get.return_value = mock_account
    inbox = mock_account.mailbox().inbox_folder()
    inbox.get_messages.return_value = iter([])

    result = runner.invoke(app, ["mail", "search", "--unread"])
    assert result.exit_code == 0
    inbox.get_messages.assert_called_once()


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_search_sender_filter(mock_get, mock_account):
    mock_get.return_value = mock_account
    inbox = mock_account.mailbox().inbox_folder()
    inbox.get_messages.return_value = iter([])

    result = runner.invoke(app, ["mail", "search", "--from", "alice@example.com"])
    assert result.exit_code == 0
    inbox.get_messages.assert_called_once()


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_search_date_range_filter(mock_get, mock_account):
    mock_get.return_value = mock_account
    inbox = mock_account.mailbox().inbox_folder()
    inbox.get_messages.return_value = iter([])

    result = runner.invoke(app, [
        "mail", "search",
        "--start-date", "2025-01-01",
        "--end-date", "2025-02-01",
    ])
    assert result.exit_code == 0
    inbox.get_messages.assert_called_once()


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_search_important_filter(mock_get, mock_account):
    mock_get.return_value = mock_account
    inbox = mock_account.mailbox().inbox_folder()
    inbox.get_messages.return_value = iter([])

    result = runner.invoke(app, ["mail", "search", "--important"])
    assert result.exit_code == 0
    inbox.get_messages.assert_called_once()


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_search_has_attachments_filter(mock_get, mock_account):
    mock_get.return_value = mock_account
    inbox = mock_account.mailbox().inbox_folder()
    inbox.get_messages.return_value = iter([])

    result = runner.invoke(app, ["mail", "search", "--has-attachments"])
    assert result.exit_code == 0
    inbox.get_messages.assert_called_once()


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_search_text_with_filters_warns(mock_get, mock_account, mock_message):
    """Text search + filters should warn that filters are ignored."""
    mock_get.return_value = mock_account
    inbox = mock_account.mailbox().inbox_folder()
    inbox.get_messages.return_value = iter([mock_message])

    result = runner.invoke(app, ["mail", "search", "hello", "--unread"])
    assert result.exit_code == 0
    assert "warning" in result.output.lower()


# ── Reply command ─────────────────────────────────────────────


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_reply(mock_get):
    account = mock_get.return_value
    mailbox = account.mailbox.return_value
    msg = MagicMock()
    reply_msg = MagicMock()
    msg.reply.return_value = reply_msg
    mailbox.get_message.return_value = msg

    result = runner.invoke(app, ["mail", "reply", "msg-123", "--body", "Thanks"])
    assert result.exit_code == 0
    msg.reply.assert_called_once()
    reply_msg.send.assert_called_once()


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_reply_all(mock_get):
    account = mock_get.return_value
    mailbox = account.mailbox.return_value
    msg = MagicMock()
    reply_msg = MagicMock()
    msg.reply_all.return_value = reply_msg
    mailbox.get_message.return_value = msg

    result = runner.invoke(app, [
        "mail", "reply", "msg-123", "--body", "Thanks", "--reply-all",
    ])
    assert result.exit_code == 0
    msg.reply_all.assert_called_once()
    reply_msg.send.assert_called_once()


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_reply_message_not_found(mock_get):
    account = mock_get.return_value
    mailbox = account.mailbox.return_value
    mailbox.get_message.return_value = None

    result = runner.invoke(app, ["mail", "reply", "nonexistent", "--body", "Hi"])
    assert result.exit_code != 0


# ── Mark command ──────────────────────────────────────────────


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_mark_read(mock_get):
    account = mock_get.return_value
    mailbox = account.mailbox.return_value
    msg = MagicMock()
    mailbox.get_message.return_value = msg

    result = runner.invoke(app, ["mail", "mark", "msg-123"])
    assert result.exit_code == 0
    msg.mark_as_read.assert_called_once()


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_mark_unread(mock_get):
    account = mock_get.return_value
    mailbox = account.mailbox.return_value
    msg = MagicMock()
    mailbox.get_message.return_value = msg

    result = runner.invoke(app, ["mail", "mark", "msg-123", "--unread"])
    assert result.exit_code == 0
    msg.mark_as_unread.assert_called_once()


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_mark_message_not_found(mock_get):
    account = mock_get.return_value
    mailbox = account.mailbox.return_value
    mailbox.get_message.return_value = None

    result = runner.invoke(app, ["mail", "mark", "nonexistent"])
    assert result.exit_code != 0


# ── Error handling tests ─────────────────────────────────────


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_search_invalid_start_date(mock_get, mock_account):
    mock_get.return_value = mock_account
    result = runner.invoke(app, ["mail", "search", "--start-date", "not-a-date"])
    assert result.exit_code != 0


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_search_invalid_end_date(mock_get, mock_account):
    mock_get.return_value = mock_account
    result = runner.invoke(app, ["mail", "search", "--end-date", "bad"])
    assert result.exit_code != 0


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_reply_send_failure(mock_get):
    account = mock_get.return_value
    mailbox = account.mailbox.return_value
    msg = MagicMock()
    reply_msg = MagicMock()
    reply_msg.send.return_value = False
    msg.reply.return_value = reply_msg
    mailbox.get_message.return_value = msg

    result = runner.invoke(app, ["mail", "reply", "msg-123", "--body", "Thanks"])
    assert result.exit_code != 0


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_mark_read_failure(mock_get):
    account = mock_get.return_value
    mailbox = account.mailbox.return_value
    msg = MagicMock()
    msg.mark_as_read.return_value = False
    mailbox.get_message.return_value = msg

    result = runner.invoke(app, ["mail", "mark", "msg-123"])
    assert result.exit_code != 0


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_mark_unread_failure(mock_get):
    account = mock_get.return_value
    mailbox = account.mailbox.return_value
    msg = MagicMock()
    msg.mark_as_unread.return_value = False
    mailbox.get_message.return_value = msg

    result = runner.invoke(app, ["mail", "mark", "msg-123", "--unread"])
    assert result.exit_code != 0
