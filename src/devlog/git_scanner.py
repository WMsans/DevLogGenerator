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