"""CLI integration tests for auth commands."""

from unittest.mock import patch

from typer.testing import CliRunner

from outlook_cli.main import app

runner = CliRunner()


def test_login_no_client_id():
    """Login with no stored config and no --client-id should fail."""
    with patch("outlook_cli.commands.auth_cmd.load_config", return_value={}):
        result = runner.invoke(app, ["auth", "login"])
    assert result.exit_code != 0
    assert "client" in result.output.lower()


@patch("outlook_cli.commands.auth_cmd.authenticate", return_value=True)
@patch("outlook_cli.commands.auth_cmd.save_config")
def test_login_with_client_id(mock_save, mock_auth):
    result = runner.invoke(app, ["auth", "login", "--client-id", "test-id"])
    assert result.exit_code == 0
    assert "successfully" in result.output.lower() or "ok" in result.output.lower()
    mock_auth.assert_called_once()


@patch("outlook_cli.commands.auth_cmd.authenticate", return_value=False)
@patch("outlook_cli.commands.auth_cmd.save_config")
def test_login_auth_failure(mock_save, mock_auth):
    result = runner.invoke(app, ["auth", "login", "--client-id", "test-id"])
    assert result.exit_code != 0


def test_logout_no_token(config_dir):
    """Logout when no token exists should be graceful."""
    with patch("outlook_cli.commands.auth_cmd.get_config_dir", return_value=config_dir):
        result = runner.invoke(app, ["auth", "logout"])
    assert result.exit_code == 0


def test_logout_removes_token(config_dir):
    token_file = config_dir / "o365_token.token"
    token_file.write_text("fake-token")

    with patch("outlook_cli.commands.auth_cmd.get_config_dir", return_value=config_dir):
        result = runner.invoke(app, ["auth", "logout"])

    assert result.exit_code == 0
    assert not token_file.exists()


@patch("outlook_cli.commands.auth_cmd.is_authenticated", return_value=True)
@patch("outlook_cli.commands.auth_cmd.load_config", return_value={"client_id": "abc", "tenant_id": "xyz"})
def test_status_authenticated(mock_config, mock_auth):
    result = runner.invoke(app, ["auth", "status"])
    assert result.exit_code == 0
    assert "abc" in result.output


@patch("outlook_cli.commands.auth_cmd.is_authenticated", return_value=False)
@patch("outlook_cli.commands.auth_cmd.load_config", return_value={})
def test_status_not_authenticated(mock_config, mock_auth):
    result = runner.invoke(app, ["auth", "status"])
    assert result.exit_code == 0
    assert "not" in result.output.lower()
