"""Configuration management for ~/.outlook-cli/config.toml."""

import sys
from pathlib import Path
import tomllib

import tomli_w

from outlook_cli.display import print_error


CONFIG_DIR = Path.home() / ".outlook-cli"
CONFIG_FILE = CONFIG_DIR / "config.toml"


def get_config_dir() -> Path:
    """Return the config directory, creating it if needed."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    return CONFIG_DIR


def load_config() -> dict:
    """Load config from disk, returning empty dict if not found."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        return tomllib.loads(CONFIG_FILE.read_text())
    except tomllib.TOMLDecodeError:
        print_error(f"Corrupt config file: {CONFIG_FILE}")
        sys.exit(1)
    except OSError as exc:
        print_error(f"Cannot read config: {exc}")
        sys.exit(1)


def save_config(config: dict) -> None:
    """Save config dict to disk."""
    try:
        get_config_dir()
        CONFIG_FILE.write_bytes(tomli_w.dumps(config).encode())
        CONFIG_FILE.chmod(0o600)
    except OSError as exc:
        print_error(f"Cannot save config: {exc}")
        sys.exit(1)
