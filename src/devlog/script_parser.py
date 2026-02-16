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
        text = "\n".join(current_lines).strip()
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
