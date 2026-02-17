import subprocess
from pathlib import Path

from devlog.git_scanner import scan_commits


def _make_test_repo(tmp_path: Path) -> Path:
    """Create a tiny git repo with 3 commits."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, capture_output=True, check=True)
    for i in range(1, 4):
        (repo / f"file{i}.py").write_text(f"print({i})")
        subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"feat: add file{i}"],
            cwd=repo,
            capture_output=True,
            check=True,
        )
    return repo


def test_scan_returns_commits(tmp_path):
    repo = _make_test_repo(tmp_path)
    commits = scan_commits(repo, max_count=10)
    assert len(commits) == 3
    assert all("sha" in c and "message" in c and "date" in c for c in commits)


def test_scan_respects_max_count(tmp_path):
    repo = _make_test_repo(tmp_path)
    commits = scan_commits(repo, max_count=2)
    assert len(commits) == 2


def test_scan_most_recent_first(tmp_path):
    repo = _make_test_repo(tmp_path)
    commits = scan_commits(repo, max_count=10)
    assert "file3" in commits[0]["message"]