# AGENTS.md

Guidelines for agentic coding agents working in this repository.

## Project Overview

DevLog Generator is a CLI tool that transforms git history into narrated video dev logs using a local LLM (Ollama), TTS (edge-tts), and video compositing (moviepy). The system uses a three-phase workflow: Init (scan git → draft.md) → Expand (expand tags → script.md) → Render (script.md → devlog.mp4).

## Build/Lint/Test Commands

```bash
# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/test_cli.py

# Run a single test function
pytest tests/test_cli.py::test_init_command_exists

# Run tests with verbose output
pytest -v

# Run tests with coverage
pytest --cov=devlog

# Type check (if mypy is installed)
mypy src/devlog

# Lint (if ruff is installed)
ruff check src/devlog
ruff format --check src/devlog
```

## Code Style Guidelines

### Imports

- Group imports in this order: standard library, third-party, local
- Use absolute imports from the package root (e.g., `from devlog.cli import app`)
- Keep imports alphabetically sorted within each group

```python
# Standard library
from dataclasses import dataclass, field
from pathlib import Path

# Third-party
import typer

# Local (if applicable)
from devlog.config import Config
```

### Formatting

- Maximum line length: 88 characters (Black default)
- Use 4 spaces for indentation (no tabs)
- Blank lines between top-level functions and classes: 2
- Blank lines between methods: 1

### Types

- Python 3.10+ syntax for type hints (use `list[str]` not `List[str]`)
- Use `dataclass` for configuration and data structures
- Always include type hints on function parameters and return types
- Use `Path` from pathlib for file paths, not strings

```python
def process_commits(repo_path: Path, max_count: int = 20) -> list[str]:
    ...
```

### Naming Conventions

- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods/attributes: `_leading_underscore`
- CLI command functions: Use simple verb names (`init`, `expand`, `render`)

### Error Handling

- Use explicit exceptions with descriptive messages
- Let errors propagate up to CLI layer where typer can display them
- Use `typer.Exit(code=1)` for controlled CLI exits with error messages

```python
if not repo_path.exists():
    typer.echo(f"Error: Repository not found at {repo_path}", err=True)
    raise typer.Exit(code=1)
```

### CLI Patterns

- Use `typer.Typer()` for the main app
- Decorate commands with `@app.command()`
- Provide short docstrings for command help text
- Use `typer.echo()` for output, `err=True` for stderr

### Testing Patterns

- Use `CliRunner` from `typer.testing` to test CLI commands
- Assert on `exit_code` and `stdout` content
- One test file per module: `test_cli.py` for `cli.py`
- Test function names: `test_<what>_<condition>`

```python
from typer.testing import CliRunner
from devlog.cli import app

runner = CliRunner()

def test_init_command_exists():
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
```

### Docstrings

- Use triple-double-quote format: `"""Description."""`
- Keep docstrings concise (one line preferred for simple functions)
- For CLI commands, docstrings appear as help text in the CLI

### Comments

- Do NOT add comments unless explicitly requested
- Code should be self-documenting through clear naming and structure
- Exception: Complex algorithms may have brief explanatory notes

### File Organization

```
src/devlog/
    __init__.py      # Package init, version info
    cli.py           # CLI entry point with typer app
    config.py        # Configuration dataclass
    [module].py      # Additional modules as needed

tests/
    __init__.py
    test_cli.py      # Tests for cli module
    test_[module].py # One test file per source module

docs/
    design_doc.md    # Architecture and design decisions
    plans/           # Implementation plans by phase
```

### Dependencies

- Core dependencies are defined in `pyproject.toml` under `[project.dependencies]`
- Dev dependencies go in `[project.optional-dependencies.dev]`
- Always check `pyproject.toml` before adding new imports to verify availability

## Architecture Notes

- Three-phase pipeline: Init → Expand → Render
- Intermediate files (`draft.md`, `script.md`) serve as contracts between phases
- User is in the loop between phases (can edit intermediate files)
- Ollama runs locally at `http://localhost:11434` by default
- Output video is `devlog.mp4` by default