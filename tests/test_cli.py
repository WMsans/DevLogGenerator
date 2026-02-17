from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from devlog.cli import app

runner = CliRunner()


@patch("devlog.cli.questionary")
@patch("devlog.cli.scan_commits")
@patch("devlog.cli.generate_draft")
def test_init_command_exists(mock_draft, mock_scan, mock_q, tmp_path):
    mock_scan.return_value = [
        {"sha": "abc123", "message": "test", "date": "2024-01-01"}
    ]
    mock_q.checkbox.return_value.ask.return_value = ["[0] test"]

    result = runner.invoke(app, ["init", "--repo", str(tmp_path)])
    assert result.exit_code == 0
    assert "draft" in result.stdout.lower()


@patch("devlog.cli.parse_draft")
@patch("devlog.cli.expand_draft")
def test_expand_command_exists(mock_expand, mock_parse, tmp_path):
    draft = tmp_path / "draft.md"
    draft.write_text("---\nproject: Test\n---\n\n## Updates\n- test\n")

    mock_parse.return_value = []

    result = runner.invoke(app, ["expand", "--draft", str(draft)])
    assert result.exit_code == 0
    assert "script" in result.stdout.lower()


@patch("devlog.cli.parse_script")
@patch("devlog.cli.render_video")
def test_render_command_exists(mock_render, mock_parse, tmp_path):
    script = tmp_path / "script.md"
    script.write_text("(emotion: happy)\nHello!")

    mock_parse.return_value = [
        type("Segment", (), {"text": "Hello!", "emotion": "happy"})
    ]

    result = runner.invoke(app, ["render", "--script", str(script)])
    assert result.exit_code == 0
    assert "video" in result.stdout.lower()
