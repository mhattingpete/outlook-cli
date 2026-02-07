"""CLI integration tests for mail commands."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from outlook_cli.main import app

runner = CliRunner()


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_search_no_results(mock_get, mock_account):
    mock_get.return_value = mock_account
    inbox = mock_account.mailbox().inbox_folder()
    inbox.get_messages.return_value = iter([])

    result = runner.invoke(app, ["mail", "search"])
    assert result.exit_code == 0
    assert "no messages" in result.output.lower()


@patch("outlook_cli.commands.mail_cmd.print_mail_table")
@patch("outlook_cli.commands.mail_cmd.get_account")
def test_search_with_results(mock_get, mock_print, mock_message):
    account = mock_get.return_value
    inbox = account.mailbox.return_value.inbox_folder.return_value
    inbox.get_messages.return_value = iter([mock_message])

    result = runner.invoke(app, ["mail", "search"])
    assert result.exit_code == 0
    mock_print.assert_called_once()
    assert mock_print.call_args[0][0][0] is mock_message


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_search_with_query(mock_get, mock_account, mock_message):
    mock_get.return_value = mock_account
    inbox = mock_account.mailbox().inbox_folder()
    inbox.get_messages.return_value = iter([mock_message])

    result = runner.invoke(app, ["mail", "search", "test query"])
    assert result.exit_code == 0


@patch("outlook_cli.commands.mail_cmd.print_mail_detail")
@patch("outlook_cli.commands.mail_cmd.get_account")
def test_read_message(mock_get, mock_print, mock_message):
    account = mock_get.return_value
    mailbox = account.mailbox.return_value
    mailbox.get_message.return_value = mock_message

    result = runner.invoke(app, ["mail", "read", "msg-123"])
    assert result.exit_code == 0
    mock_print.assert_called_once_with(mock_message)


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_read_message_not_found(mock_get, mock_account):
    mock_get.return_value = mock_account
    mailbox = mock_account.mailbox()
    mailbox.get_message.return_value = None

    result = runner.invoke(app, ["mail", "read", "nonexistent"])
    assert result.exit_code != 0


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_send_message(mock_get, mock_account):
    mock_get.return_value = mock_account
    new_msg = MagicMock()
    new_msg.send.return_value = True
    mock_account.new_message.return_value = new_msg

    result = runner.invoke(app, [
        "mail", "send",
        "--to", "bob@example.com",
        "--subject", "Hi",
        "--body", "Hello!",
    ])
    assert result.exit_code == 0
    new_msg.to.add.assert_called_with("bob@example.com")
    new_msg.send.assert_called_once()


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_send_message_with_cc(mock_get, mock_account):
    mock_get.return_value = mock_account
    new_msg = MagicMock()
    new_msg.send.return_value = True
    mock_account.new_message.return_value = new_msg

    result = runner.invoke(app, [
        "mail", "send",
        "--to", "bob@example.com",
        "--cc", "carol@example.com",
        "--subject", "Hi",
        "--body", "Hello!",
    ])
    assert result.exit_code == 0
    new_msg.cc.add.assert_called_with("carol@example.com")


@patch("outlook_cli.commands.mail_cmd.get_account")
def test_send_fails(mock_get, mock_account):
    mock_get.return_value = mock_account
    new_msg = MagicMock()
    new_msg.send.return_value = False
    mock_account.new_message.return_value = new_msg

    result = runner.invoke(app, [
        "mail", "send",
        "--to", "bob@example.com",
        "--subject", "Hi",
        "--body", "Hello!",
    ])
    assert result.exit_code != 0
