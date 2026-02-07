"""CLI integration tests for main app."""

from typer.testing import CliRunner

from outlook_cli.main import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "outlook-cli 0.1.0" in result.output


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "auth" in result.output
    assert "mail" in result.output
    assert "cal" in result.output
