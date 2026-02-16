## Task 6: Script Expander (Phase 2 — Expand)

**Files:**
- Create: `src/devlog/expander.py`
- Create: `tests/test_expander.py`

**Step 1: Write the failing test**

```python
# tests/test_expander.py
from pathlib import Path
from unittest.mock import patch

from devlog.expander import expand_draft
from devlog.md_parser import DraftBlock


FAKE_BLOCKS = [
    DraftBlock(text="* Feature A is done", expand=False, line_number=1),
    DraftBlock(text="* Feature B had tricky bugs", expand=True, line_number=2),
]


@patch("devlog.expander.get_diff_text", return_value="+def allocate():
+    return malloc(64)")
@patch("devlog.expander.generate", return_value="(emotion: thinking)
Feature B required rewriting the allocator to use 64-byte blocks.")
def test_expand_creates_script(mock_llm, mock_diff, tmp_path):
    output = tmp_path / "script.md"
    expand_draft(
        blocks=FAKE_BLOCKS,
        output_path=output,
        repo_path=tmp_path,
        commit_sha="abc1234",
    )
    content = output.read_text()
    assert "(emotion:" in content
    assert "allocator" in content.lower()


@patch("devlog.expander.get_diff_text", return_value="")
@patch("devlog.expander.generate", return_value="Expanded text")
def test_expand_passes_through_plain_blocks(mock_llm, mock_diff, tmp_path):
    output = tmp_path / "script.md"
    expand_draft(
        blocks=FAKE_BLOCKS,
        output_path=output,
        repo_path=tmp_path,
        commit_sha="abc1234",
    )
    content = output.read_text()
    assert "Feature A" in content
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_expander.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/devlog/expander.py
from pathlib import Path

from devlog.diff_fetcher import get_diff_text
from devlog.llm import generate
from devlog.md_parser import DraftBlock

EXPAND_SYSTEM = (
    "You are writing a video dev log script. Given a bullet point and its code diff, "
    "write a detailed, conversational explanation (2-4 sentences). "
    "Prefix each paragraph with an emotion tag like (emotion: thinking) or (emotion: happy). "
    "Be technically precise but casual."
)


def expand_draft(
    blocks: list[DraftBlock],
    output_path: Path,
    repo_path: Path,
    commit_sha: str,
    model: str = "qwen3:8b",
) -> None:
    """Expand tagged blocks via LLM + diff context, write script.md."""
    sections: list[str] = []

    for block in blocks:
        if block.expand:
            diff = get_diff_text(repo_path, commit_sha)
            prompt = (
                f"Bullet point: {block.text}

"
                f"Code diff:
```
{diff}
```

"
                "Write the script section:"
            )
            expanded = generate(prompt, model=model, system=EXPAND_SYSTEM)
            sections.append(expanded)
        else:
            sections.append(f"(emotion: happy)
{block.text}")

    output_path.write_text("

".join(sections) + "
")
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_expander.py -v
```

Expected: 2 PASS

**Step 5: Commit**

```bash
git add src/devlog/expander.py tests/test_expander.py
git commit -m "feat: add script expander with diff-aware LLM prompts"
```
