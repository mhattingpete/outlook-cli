"""Unit tests for auth.py."""

from unittest.mock import MagicMock, patch

import pytest

from outlook_cli.auth import authenticate, get_account, is_authenticated


@patch("outlook_cli.auth._build_account")
def test_authenticate_success(mock_build):
    account = MagicMock()
    account.authenticate.return_value = True
    mock_build.return_value = account

    assert authenticate("client-id", "tenant-id") is True
    account.authenticate.assert_called_once_with(scopes=["message_all", "calendar_all"])


@patch("outlook_cli.auth._build_account")
def test_authenticate_failure(mock_build):
    account = MagicMock()
    account.authenticate.return_value = False
    mock_build.return_value = account

    assert authenticate("client-id") is False


@patch("outlook_cli.auth.load_config", return_value={})
def test_is_authenticated_no_config(mock_config):
    assert is_authenticated() is False


@patch("outlook_cli.auth._build_account")
@patch("outlook_cli.auth.load_config", return_value={"client_id": "abc"})
def test_is_authenticated_valid_token(mock_config, mock_build):
    account = MagicMock()
    account.is_authenticated = True
    mock_build.return_value = account

    assert is_authenticated() is True


@patch("outlook_cli.auth._build_account")
@patch("outlook_cli.auth.load_config", return_value={"client_id": "abc"})
def test_is_authenticated_expired_token(mock_config, mock_build):
    account = MagicMock()
    account.is_authenticated = False
    mock_build.return_value = account

    assert is_authenticated() is False


@patch("outlook_cli.auth.load_config", return_value={})
def test_get_account_exits_without_config(mock_config):
    with pytest.raises(SystemExit):
        get_account()


@patch("outlook_cli.auth._build_account")
@patch("outlook_cli.auth.load_config", return_value={"client_id": "abc"})
def test_get_account_exits_when_not_authenticated(mock_config, mock_build):
    account = MagicMock()
    account.is_authenticated = False
    mock_build.return_value = account

    with pytest.raises(SystemExit):
        get_account()


@patch("outlook_cli.auth._build_account")
@patch("outlook_cli.auth.load_config", return_value={"client_id": "abc"})
def test_get_account_returns_account(mock_config, mock_build):
    account = MagicMock()
    account.is_authenticated = True
    mock_build.return_value = account

    result = get_account()
    assert result is account
