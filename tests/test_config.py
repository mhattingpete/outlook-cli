"""Unit tests for config.py."""

import pytest

from outlook_cli.config import get_config_dir, load_config, save_config


def test_get_config_dir_creates_directory(config_dir):
    result = get_config_dir()
    assert result == config_dir
    assert result.is_dir()


def test_load_config_empty_when_no_file(config_dir):
    assert load_config() == {}


def test_save_and_load_roundtrip(config_dir):
    data = {"client_id": "abc-123", "tenant_id": "my-tenant"}
    save_config(data)

    loaded = load_config()
    assert loaded == data


def test_save_overwrites(config_dir):
    save_config({"client_id": "old"})
    save_config({"client_id": "new"})

    assert load_config()["client_id"] == "new"


def test_load_config_exits_on_corrupt_toml(config_dir):
    """Corrupt TOML file should exit with an error, not crash."""
    import outlook_cli.config as config_mod

    config_mod.CONFIG_FILE.write_text("not valid [ toml =")
    with pytest.raises(SystemExit):
        load_config()


def test_save_config_sets_file_permissions(config_dir):
    """Saved config file should have 0o600 permissions."""
    import stat

    save_config({"client_id": "test"})
    import outlook_cli.config as config_mod

    mode = config_mod.CONFIG_FILE.stat().st_mode
    assert stat.S_IMODE(mode) == 0o600
