import subprocess
from pathlib import Path

from devlog.diff_fetcher import get_diff


def _make_repo_with_diff(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=repo, capture_output=True, check=True)

    (repo / "app.py").write_text("x = 1\n")
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, capture_output=True, check=True)

    (repo / "app.py").write_text("x = 1\ny = 2\n")
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "add y"], cwd=repo, capture_output=True, check=True)

    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return repo, sha


def test_get_diff_returns_patch(tmp_path):
    repo, sha = _make_repo_with_diff(tmp_path)
    diff = get_diff(repo, sha)
    assert "+y = 2" in diff


def test_get_diff_contains_filename(tmp_path):
    repo, sha = _make_repo_with_diff(tmp_path)
    diff = get_diff(repo, sha)
    assert "app.py" in diff