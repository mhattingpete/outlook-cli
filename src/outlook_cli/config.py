"""Configuration management for ~/.outlook-cli/config.toml."""

from pathlib import Path
import tomllib

import tomli_w


CONFIG_DIR = Path.home() / ".outlook-cli"
CONFIG_FILE = CONFIG_DIR / "config.toml"


def get_config_dir() -> Path:
    """Return the config directory, creating it if needed."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def load_config() -> dict:
    """Load config from disk, returning empty dict if not found."""
    if not CONFIG_FILE.exists():
        return {}
    return tomllib.loads(CONFIG_FILE.read_text())


def save_config(config: dict) -> None:
    """Save config dict to disk."""
    get_config_dir()
    CONFIG_FILE.write_bytes(tomli_w.dumps(config).encode())
