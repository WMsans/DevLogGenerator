from typer.testing import CliRunner
from devlog.cli import app

runner = CliRunner()


def test_init_command_exists():
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "init" in result.stdout.lower()


def test_expand_command_exists():
    result = runner.invoke(app, ["expand"])
    assert result.exit_code == 0
    assert "expand" in result.stdout.lower()


def test_render_command_exists():
    result = runner.invoke(app, ["render"])
    assert result.exit_code == 0
    assert "render" in result.stdout.lower()