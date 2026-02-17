import subprocess
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from devlog.cli import app

runner = CliRunner()


def _make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "t@t.com"],
        cwd=repo,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "T"], cwd=repo, capture_output=True, check=True
    )
    (repo / "main.py").write_text("print('hello')")
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "feat: initial"],
        cwd=repo,
        capture_output=True,
        check=True,
    )
    return repo


@patch("devlog.cli.questionary")
@patch("devlog.draft.generate", return_value="- Initial commit summary")
def test_init_produces_draft(mock_llm, mock_q, tmp_path):
    repo = _make_repo(tmp_path)
    draft = tmp_path / "draft.md"

    mock_q.checkbox.return_value.ask.return_value = ["[0] feat: initial"]

    result = runner.invoke(
        app,
        [
            "init",
            "--repo",
            str(repo),
            "--output",
            str(draft),
        ],
    )
    assert result.exit_code == 0
    assert draft.exists()
