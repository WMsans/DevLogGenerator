## Task 2: Diff Fetcher

**Files:**
- Create: `src/devlog/diff_fetcher.py`
- Create: `tests/test_diff_fetcher.py`

**Step 1: Write the failing test**

```python
# tests/test_diff_fetcher.py
import subprocess
from pathlib import Path

from devlog.diff_fetcher import get_diff


def _make_repo_with_diff(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=repo, capture_output=True, check=True)

    (repo / "app.py").write_text("x = 1
")
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, capture_output=True, check=True)

    (repo / "app.py").write_text("x = 1
y = 2
")
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
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_diff_fetcher.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/devlog/diff_fetcher.py
from pathlib import Path

from git import Repo


def get_diff(repo_path: Path, commit_sha: str) -> str:
    """Return the unified diff for a single commit."""
    repo = Repo(repo_path)
    commit = repo.commit(commit_sha)
    if commit.parents:
        return commit.parents[0].diff(commit, create_patch=True, unified=3).__str__()
    # First commit — diff against empty tree
    return commit.diff(None, create_patch=True, unified=3).__str__()


def get_diff_text(repo_path: Path, commit_sha: str) -> str:
    """Return a clean, readable diff string for a commit."""
    repo = Repo(repo_path)
    commit = repo.commit(commit_sha)
    parent = commit.parents[0] if commit.parents else None
    diffs = parent.diff(commit, create_patch=True) if parent else commit.diff(None, create_patch=True)
    parts = []
    for d in diffs:
        header = f"--- {d.a_path or '/dev/null'}
+++ {d.b_path or '/dev/null'}"
        patch = d.diff.decode("utf-8", errors="replace") if isinstance(d.diff, bytes) else d.diff
        parts.append(f"{header}
{patch}")
    return "
".join(parts)
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_diff_fetcher.py -v
```

Expected: 2 PASS

**Step 5: Commit**

```bash
git add src/devlog/diff_fetcher.py tests/test_diff_fetcher.py
git commit -m "feat: add diff fetcher for individual commits"
```
