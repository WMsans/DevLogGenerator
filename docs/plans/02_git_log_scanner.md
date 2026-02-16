## Task 1: Git Log Scanner

**Files:**
- Create: `src/devlog/git_scanner.py`
- Create: `tests/test_git_scanner.py`

**Step 1: Write the failing test**

```python
# tests/test_git_scanner.py
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
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_git_scanner.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'devlog.git_scanner'`

**Step 3: Write minimal implementation**

```python
# src/devlog/git_scanner.py
from pathlib import Path

from git import Repo


def scan_commits(repo_path: Path, max_count: int = 20) -> list[dict]:
    """Return recent commits as dicts with sha, message, date, and author."""
    repo = Repo(repo_path)
    results = []
    for commit in repo.iter_commits(max_count=max_count):
        results.append(
            {
                "sha": commit.hexsha,
                "message": commit.message.strip(),
                "date": commit.committed_datetime.isoformat(),
                "author": str(commit.author),
            }
        )
    return results
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_git_scanner.py -v
```

Expected: 3 PASS

**Step 5: Commit**

```bash
git add src/devlog/git_scanner.py tests/test_git_scanner.py
git commit -m "feat: add git log scanner"
```
