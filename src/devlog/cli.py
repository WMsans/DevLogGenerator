import re
from pathlib import Path

import questionary
import typer

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
    model: str = typer.Option("qwen3:8b", help="Ollama model name"),
    max_commits: int = typer.Option(20, help="Max commits to scan"),
    project: str = typer.Option("Project", help="Project name for frontmatter"),
):
    """Phase 1: Scan git history and generate draft.md."""
    commits = scan_commits(repo, max_count=max_commits)
    if not commits:
        typer.echo("No commits found.")
        raise typer.Exit(1)

    choices = [f"[{i}] {c['message']}" for i, c in enumerate(commits)]
    selected = questionary.checkbox(
        "Select commits for the dev log:", choices=choices
    ).ask()

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
    model: str = typer.Option("qwen3:8b", help="Ollama model name"),
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
