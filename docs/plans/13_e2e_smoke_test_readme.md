## Task 12: End-to-End Smoke Test & README

**Files:**
- Create: `tests/test_e2e.py`
- Create: `README.md`

**Step 1: Write the E2E test (all mocked externals)**

```python
# tests/test_e2e.py
"""End-to-end workflow test with mocked LLM, TTS, and video."""
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

from typer.testing import CliRunner
from devlog.cli import app

runner = CliRunner()


def _make_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=repo, capture_output=True, check=True)
    (repo / "app.py").write_text("x = 1")
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "feat: add app"], cwd=repo, capture_output=True, check=True)
    return repo


@patch("devlog.cli.questionary")
@patch("devlog.draft.generate", return_value="* App module added")
def test_full_init_expand_flow(mock_llm, mock_q, tmp_path):
    repo = _make_repo(tmp_path)
    draft = tmp_path / "draft.md"
    script = tmp_path / "script.md"

    # Phase 1: Init
    mock_q.checkbox.return_value.ask.return_value = ["[0] feat: add app"]
    result = runner.invoke(app, ["init", "--repo", str(repo), "--output", str(draft)])
    assert result.exit_code == 0
    assert draft.exists()

    # Add an EXPAND tag
    content = draft.read_text()
    content = content.replace("* App module added", "{{EXPAND}} * App module added")
    draft.write_text(content)

    # Phase 2: Expand
    with patch("devlog.expander.generate", return_value="(emotion: happy)
We added the core app module."):
        result = runner.invoke(app, [
            "expand",
            "--draft", str(draft),
            "--output", str(script),
            "--repo", str(repo),
        ])
    assert result.exit_code == 0
    assert script.exists()
    assert "(emotion:" in script.read_text()
```

**Step 2: Run test**

```bash
pytest tests/test_e2e.py -v
```

Expected: PASS

**Step 3: Create README**

```markdown
# devlog — Local Dev Log Generator

Generate narrated video dev logs from your git history, entirely offline.

## Quick Start

```bash
pip install -e .

# Phase 1: Select commits and generate a draft
devlog init --repo ./my-project

# Phase 2: Add {{EXPAND}} tags to draft.md, then expand
devlog expand

# Phase 3: Render the video
devlog render
```

## Requirements

- Python 3.10+
- [Ollama](https://ollama.ai) running locally
- FFmpeg installed (`apt install ffmpeg` / `brew install ffmpeg`)
- Sprite PNGs in `assets/sprites/` (at minimum: `neutral.png`)

## Workflow

1. **`devlog init`** — scans git log, lets you pick commits, generates `draft.md`
2. **Edit `draft.md`** — add `{{EXPAND}}` before any bullet you want a deep dive on
3. **`devlog expand`** — fetches diffs, calls Ollama, produces `script.md`
4. **`devlog render`** — runs TTS + sprite compositing → `devlog.mp4`
```

**Step 4: Run full test suite**

```bash
pytest tests/ -v
```

Expected: ALL PASS

**Step 5: Commit**

```bash
git add tests/test_e2e.py README.md
git commit -m "docs: add README and E2E smoke test"
```
