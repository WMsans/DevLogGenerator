## Task 0: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/devlog/__init__.py`
- Create: `src/devlog/cli.py`
- Create: `src/devlog/config.py`
- Create: `tests/__init__.py`
- Create: `tests/test_cli.py`

**Step 1: Create `pyproject.toml`**

```toml
[project]
name = "devlog"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "typer>=0.9",
    "questionary>=2.0",
    "GitPython>=3.1",
    "requests>=2.31",
    "moviepy>=1.0",
    "TTS>=0.22",
]

[project.scripts]
devlog = "devlog.cli:app"

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Step 2: Create the package root**

```python
# src/devlog/__init__.py
"""Local Dev Log Generator."""
```

**Step 3: Create the CLI entry point**

```python
# src/devlog/cli.py
import typer

app = typer.Typer(help="Generate video dev logs from git history.")


@app.command()
def init():
    """Phase 1: Scan git history and generate draft.md."""
    typer.echo("init: not implemented")


@app.command()
def expand():
    """Phase 2: Expand {{EXPAND}} tags in draft.md into script.md."""
    typer.echo("expand: not implemented")


@app.command()
def render():
    """Phase 3: Render script.md into devlog.mp4."""
    typer.echo("render: not implemented")


if __name__ == "__main__":
    app()
```

**Step 4: Create the config loader stub**

```python
# src/devlog/config.py
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    repo_path: Path = field(default_factory=lambda: Path("."))
    draft_path: Path = field(default_factory=lambda: Path("draft.md"))
    script_path: Path = field(default_factory=lambda: Path("script.md"))
    output_path: Path = field(default_factory=lambda: Path("devlog.mp4"))
    ollama_model: str = "llama3"
    ollama_url: str = "http://localhost:11434"
    max_commits: int = 20
    sprite_dir: Path = field(default_factory=lambda: Path("assets/sprites"))
```

**Step 5: Write a smoke test**

```python
# tests/test_cli.py
from typer.testing import CliRunner
from devlog.cli import app

runner = CliRunner()


def test_init_command_exists():
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "init" in result.stdout.lower()


def test_expand_command_exists():
    result = runner.invoke(app, ["expand"])
    assert result.exit_code == 0
    assert "expand" in result.stdout.lower()


def test_render_command_exists():
    result = runner.invoke(app, ["render"])
    assert result.exit_code == 0
    assert "render" in result.stdout.lower()
```

**Step 6: Install and run tests**

```bash
pip install -e ".[dev]" 2>/dev/null || pip install -e .
pytest tests/test_cli.py -v
```

Expected: 3 PASS

**Step 7: Commit**

```bash
git init
echo "__pycache__/
*.egg-info/
dist/
.venv/" > .gitignore
git add .
git commit -m "chore: scaffold project with CLI skeleton and smoke tests"
```
