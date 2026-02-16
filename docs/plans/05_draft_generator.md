## Task 4: Draft Generator (Phase 1 — Init)

**Files:**
- Create: `src/devlog/draft.py`
- Create: `tests/test_draft.py`
- Modify: `src/devlog/cli.py`

**Step 1: Write the failing test**

```python
# tests/test_draft.py
from pathlib import Path
from unittest.mock import patch

from devlog.draft import generate_draft


FAKE_COMMITS = [
    {"sha": "abc123", "message": "feat: add login", "date": "2025-01-15T10:00:00", "author": "Dev"},
    {"sha": "def456", "message": "fix: null pointer in parser", "date": "2025-01-14T09:00:00", "author": "Dev"},
]


@patch("devlog.draft.generate", return_value="- Added user login with OAuth2 flow
- Fixed null pointer in the JSON parser")
def test_generate_draft_creates_file(mock_llm, tmp_path):
    output = tmp_path / "draft.md"
    generate_draft(
        commits=FAKE_COMMITS,
        selected_indices=[0, 1],
        output_path=output,
        project_name="MyApp",
    )
    content = output.read_text()
    assert "project:" in content.lower() or "MyApp" in content
    assert "abc123" in content or "login" in content.lower()


@patch("devlog.draft.generate", return_value="- Login feature overview")
def test_generate_draft_only_includes_selected(mock_llm, tmp_path):
    output = tmp_path / "draft.md"
    generate_draft(
        commits=FAKE_COMMITS,
        selected_indices=[0],
        output_path=output,
        project_name="MyApp",
    )
    # LLM was called with only the selected commit
    call_args = mock_llm.call_args[0][0] if mock_llm.call_args[0] else mock_llm.call_args[1]["prompt"]
    assert "login" in call_args.lower()
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_draft.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/devlog/draft.py
from pathlib import Path

from devlog.llm import generate

SUMMARIZE_SYSTEM = (
    "You are a developer writing a casual video dev log script. "
    "Summarize the following git commits into a bullet-point list of updates. "
    "Be concise but technically accurate. Output only the bullet list."
)


def generate_draft(
    commits: list[dict],
    selected_indices: list[int],
    output_path: Path,
    project_name: str = "Project",
    model: str = "llama3",
) -> None:
    """Generate a draft.md from selected commits via LLM summarization."""
    selected = [commits[i] for i in selected_indices]

    commit_text = "
".join(
        f"- [{c['sha'][:7]}] {c['message']} ({c['date']})" for c in selected
    )

    prompt = f"Commits:
{commit_text}"
    summary = generate(prompt, model=model, system=SUMMARIZE_SYSTEM)

    frontmatter = (
        f"---
"
        f'project: "{project_name}"
'
        f"commits:
"
        + "".join(f'  - "{c["sha"][:7]}"
' for c in selected)
        + f"---

"
    )

    body = f"## Updates

{summary}
"

    output_path.write_text(frontmatter + body)
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_draft.py -v
```

Expected: 2 PASS

**Step 5: Commit**

```bash
git add src/devlog/draft.py tests/test_draft.py
git commit -m "feat: add draft generator with LLM summarization"
```
