from pathlib import Path

from git import Repo


def get_diff(repo_path: Path, commit_sha: str) -> str:
    """Return the unified diff for a single commit."""
    repo = Repo(repo_path)
    commit = repo.commit(commit_sha)
    if commit.parents:
        diffs = commit.parents[0].diff(commit, create_patch=True, unified=3)
    else:
        diffs = commit.diff(None, create_patch=True, unified=3)
    parts = []
    for d in diffs:
        header = f"--- {d.a_path or '/dev/null'}\n+++ {d.b_path or '/dev/null'}"
        if d.diff:
            patch = d.diff.decode("utf-8", errors="replace") if isinstance(d.diff, bytes) else d.diff
            parts.append(f"{header}\n{patch}")
        else:
            parts.append(header)
    return "\n".join(parts)


def get_diff_text(repo_path: Path, commit_sha: str) -> str:
    """Return a clean, readable diff string for a commit."""
    repo = Repo(repo_path)
    commit = repo.commit(commit_sha)
    parent = commit.parents[0] if commit.parents else None
    diffs = parent.diff(commit, create_patch=True) if parent else commit.diff(None, create_patch=True)
    parts = []
    for d in diffs:
        header = f"--- {d.a_path or '/dev/null'}\n+++ {d.b_path or '/dev/null'}"
        patch = d.diff.decode("utf-8", errors="replace") if isinstance(d.diff, bytes) else d.diff
        parts.append(f"{header}\n{patch}")
    return "\n".join(parts)