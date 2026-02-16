## Task 7: Script Parser (emotion tags → render blocks)

**Files:**
- Create: `src/devlog/script_parser.py`
- Create: `tests/test_script_parser.py`

**Step 1: Write the failing test**

```python
# tests/test_script_parser.py
from devlog.script_parser import parse_script, ScriptSegment


def test_parse_single_segment():
    text = "(emotion: happy)
Hey everyone! Feature A is done.
"
    segments = parse_script(text)
    assert len(segments) == 1
    assert segments[0].emotion == "happy"
    assert "Feature A" in segments[0].text


def test_parse_multiple_segments():
    text = (
        "(emotion: happy)
Great news!

"
        "(emotion: thinking)
But this part was tricky.
"
    )
    segments = parse_script(text)
    assert len(segments) == 2
    assert segments[0].emotion == "happy"
    assert segments[1].emotion == "thinking"


def test_parse_defaults_to_neutral():
    text = "No emotion tag here.
"
    segments = parse_script(text)
    assert len(segments) == 1
    assert segments[0].emotion == "neutral"
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_script_parser.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/devlog/script_parser.py
from __future__ import annotations

import re
from dataclasses import dataclass

EMOTION_RE = re.compile(r"^\(emotion:\s*(\w+)\)\s*$")


@dataclass
class ScriptSegment:
    text: str
    emotion: str = "neutral"


def parse_script(content: str) -> list[ScriptSegment]:
    """Parse script.md into segments with emotion metadata."""
    segments: list[ScriptSegment] = []
    current_emotion = "neutral"
    current_lines: list[str] = []

    def flush():
        text = "
".join(current_lines).strip()
        if text:
            segments.append(ScriptSegment(text=text, emotion=current_emotion))
        current_lines.clear()

    for line in content.splitlines():
        match = EMOTION_RE.match(line.strip())
        if match:
            flush()
            current_emotion = match.group(1)
        else:
            current_lines.append(line)

    flush()
    return segments
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_script_parser.py -v
```

Expected: 3 PASS

**Step 5: Commit**

```bash
git add src/devlog/script_parser.py tests/test_script_parser.py
git commit -m "feat: add script parser for emotion-tagged segments"
```
