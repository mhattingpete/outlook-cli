"""Unit tests for auth.py."""

from unittest.mock import MagicMock, patch

import pytest

from outlook_cli.auth import authenticate, get_account, is_authenticated


@patch("outlook_cli.auth.PublicClientApplication")
@patch("outlook_cli.auth._get_graph_scopes", return_value=["https://graph.microsoft.com/Mail.ReadWrite"])
@patch("outlook_cli.auth._token_backend")
def test_authenticate_success(mock_backend, mock_scopes, mock_msal_cls):
    msal_app = MagicMock()
    mock_msal_cls.return_value = msal_app
    msal_app.initiate_device_flow.return_value = {
        "user_code": "ABCD-EFGH",
        "verification_uri": "https://microsoft.com/devicelogin",
    }
    msal_app.acquire_token_by_device_flow.return_value = {"access_token": "tok123"}

    assert authenticate("client-id", "common") is True
    msal_app.initiate_device_flow.assert_called_once()
    mock_backend.return_value.save_token.assert_called_once_with(force=True)


@patch("outlook_cli.auth.PublicClientApplication")
@patch("outlook_cli.auth._get_graph_scopes", return_value=["https://graph.microsoft.com/Mail.ReadWrite"])
@patch("outlook_cli.auth._token_backend")
def test_authenticate_failure(mock_backend, mock_scopes, mock_msal_cls):
    msal_app = MagicMock()
    mock_msal_cls.return_value = msal_app
    msal_app.initiate_device_flow.return_value = {
        "user_code": "ABCD-EFGH",
        "verification_uri": "https://microsoft.com/devicelogin",
    }
    msal_app.acquire_token_by_device_flow.return_value = {
        "error_description": "User cancelled",
    }

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
