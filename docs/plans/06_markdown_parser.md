## Task 5: Markdown Parser for `{{EXPAND}}` Tags

**Files:**
- Create: `src/devlog/md_parser.py`
- Create: `tests/test_md_parser.py`

**Step 1: Write the failing test**

```python
# tests/test_md_parser.py
from devlog.md_parser import parse_draft, DraftBlock


def test_parse_plain_lines():
    text = "## Updates

* Feature A summary
* Feature B summary
"
    blocks = parse_draft(text)
    assert len(blocks) == 1
    assert blocks[0].expand is False


def test_parse_expand_tags():
    text = (
        "## Updates

"
        "* Feature A summary
"
        "{{EXPAND}} * Feature B summary
"
        "* Feature C summary
"
    )
    blocks = parse_draft(text)
    expand_blocks = [b for b in blocks if b.expand]
    assert len(expand_blocks) == 1
    assert "Feature B" in expand_blocks[0].text


def test_parse_preserves_order():
    text = "Line 1
{{EXPAND}} Line 2
Line 3
"
    blocks = parse_draft(text)
    texts = [b.text.strip() for b in blocks]
    assert texts == ["Line 1", "Line 2", "Line 3"]


def test_parse_extracts_frontmatter():
    text = '---
project: "Foo"
---

## Updates
* stuff
'
    blocks = parse_draft(text)
    # Frontmatter is not included in the content blocks
    assert not any("---" in b.text for b in blocks)
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_md_parser.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/devlog/md_parser.py
from __future__ import annotations

import re
from dataclasses import dataclass

EXPAND_RE = re.compile(r"^\{\{EXPAND\}\}\s*(.*)$")
FRONTMATTER_RE = re.compile(r"^---\s*
.*?
---\s*
", re.DOTALL)


@dataclass
class DraftBlock:
    text: str
    expand: bool = False
    line_number: int = 0


def parse_draft(content: str) -> list[DraftBlock]:
    """Parse a draft.md into blocks, identifying {{EXPAND}} tagged lines."""
    # Strip frontmatter
    content = FRONTMATTER_RE.sub("", content)

    blocks: list[DraftBlock] = []
    for lineno, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue

        match = EXPAND_RE.match(stripped)
        if match:
            blocks.append(DraftBlock(text=match.group(1), expand=True, line_number=lineno))
        else:
            blocks.append(DraftBlock(text=stripped, expand=False, line_number=lineno))

    return blocks
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_md_parser.py -v
```

Expected: 4 PASS

**Step 5: Commit**

```bash
git add src/devlog/md_parser.py tests/test_md_parser.py
git commit -m "feat: add markdown parser with EXPAND tag detection"
```
