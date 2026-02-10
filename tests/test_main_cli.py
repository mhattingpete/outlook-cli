"""CLI integration tests for main app."""

from typer.testing import CliRunner

from outlook_cli import __version__
from outlook_cli.main import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert f"outlook-cli {__version__}" in result.output


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "auth" in result.output
    assert "mail" in result.output
    assert "cal" in result.output
