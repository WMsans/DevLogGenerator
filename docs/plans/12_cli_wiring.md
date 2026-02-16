## Task 11: Wire Everything Into the CLI

**Files:**
- Modify: `src/devlog/cli.py`
- Create: `tests/test_cli_integration.py`

**Step 1: Write the integration test**

```python
# tests/test_cli_integration.py
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
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=repo, capture_output=True, check=True)
    (repo / "main.py").write_text("print('hello')")
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "feat: initial"], cwd=repo, capture_output=True, check=True)
    return repo


@patch("devlog.cli.questionary")
@patch("devlog.draft.generate", return_value="- Initial commit summary")
def test_init_produces_draft(mock_llm, mock_q, tmp_path):
    repo = _make_repo(tmp_path)
    draft = tmp_path / "draft.md"

    # Mock questionary to select first commit
    mock_q.checkbox.return_value.ask.return_value = ["[0] feat: initial"]

    result = runner.invoke(app, [
        "init",
        "--repo", str(repo),
        "--output", str(draft),
    ])
    assert result.exit_code == 0
    assert draft.exists()
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_cli_integration.py -v
```

Expected: FAIL — CLI doesn't accept `--repo` / `--output` yet

**Step 3: Rewrite the CLI to wire all phases**

```python
# src/devlog/cli.py
from pathlib import Path

import questionary
import typer

from devlog.config import Config
from devlog.draft import generate_draft
from devlog.expander import expand_draft
from devlog.git_scanner import scan_commits
from devlog.md_parser import parse_draft
from devlog.renderer import render_video
from devlog.script_parser import parse_script

app = typer.Typer(help="Generate video dev logs from git history.")


@app.command()
def init(
    repo: Path = typer.Option(".", help="Path to git repo"),
    output: Path = typer.Option("draft.md", help="Output draft file"),
    model: str = typer.Option("llama3", help="Ollama model name"),
    max_commits: int = typer.Option(20, help="Max commits to scan"),
    project: str = typer.Option("Project", help="Project name for frontmatter"),
):
    """Phase 1: Scan git history and generate draft.md."""
    commits = scan_commits(repo, max_count=max_commits)
    if not commits:
        typer.echo("No commits found.")
        raise typer.Exit(1)

    choices = [f"[{i}] {c['message']}" for i, c in enumerate(commits)]
    selected = questionary.checkbox("Select commits for the dev log:", choices=choices).ask()

    if not selected:
        typer.echo("No commits selected.")
        raise typer.Exit(1)

    indices = [int(s.split("]")[0].strip("[")) for s in selected]

    generate_draft(
        commits=commits,
        selected_indices=indices,
        output_path=output,
        project_name=project,
        model=model,
    )
    typer.echo(f"Draft written to {output}")
    typer.echo("Edit the file and add {{EXPAND}} tags, then run: devlog expand")


@app.command()
def expand(
    draft: Path = typer.Option("draft.md", help="Input draft file"),
    output: Path = typer.Option("script.md", help="Output script file"),
    repo: Path = typer.Option(".", help="Path to git repo"),
    model: str = typer.Option("llama3", help="Ollama model name"),
):
    """Phase 2: Expand {{EXPAND}} tags in draft.md into script.md."""
    if not draft.exists():
        typer.echo(f"Draft not found: {draft}")
        raise typer.Exit(1)

    content = draft.read_text()
    blocks = parse_draft(content)

    expand_blocks = [b for b in blocks if b.expand]
    if not expand_blocks:
        typer.echo("No {{EXPAND}} tags found. Writing script as-is.")

    # Extract first commit sha from frontmatter for diff context
    import re
    sha_match = re.search(r'- "(\w+)"', content)
    commit_sha = sha_match.group(1) if sha_match else "HEAD"

    expand_draft(
        blocks=blocks,
        output_path=output,
        repo_path=repo,
        commit_sha=commit_sha,
        model=model,
    )
    typer.echo(f"Script written to {output}")
    typer.echo("Review the script, then run: devlog render")


@app.command()
def render(
    script: Path = typer.Option("script.md", help="Input script file"),
    output: Path = typer.Option("devlog.mp4", help="Output video file"),
    sprites: Path = typer.Option("assets/sprites", help="Sprite directory"),
):
    """Phase 3: Render script.md into devlog.mp4."""
    if not script.exists():
        typer.echo(f"Script not found: {script}")
        raise typer.Exit(1)

    content = script.read_text()
    segments = parse_script(content)

    if not segments:
        typer.echo("No segments found in script.")
        raise typer.Exit(1)

    work_dir = Path(".devlog_tmp")
    work_dir.mkdir(exist_ok=True)

    render_video(
        segments=segments,
        output_path=output,
        sprite_dir=sprites,
        work_dir=work_dir,
    )
    typer.echo(f"Video rendered to {output}")


if __name__ == "__main__":
    app()
```

**Step 4: Run all tests**

```bash
pytest tests/ -v
```

Expected: ALL PASS

**Step 5: Commit**

```bash
git add src/devlog/cli.py tests/test_cli_integration.py
git commit -m "feat: wire all phases into CLI with options"
```
