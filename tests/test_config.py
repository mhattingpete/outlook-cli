"""Unit tests for config.py."""

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
