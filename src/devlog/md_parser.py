from __future__ import annotations

import re
from dataclasses import dataclass

EXPAND_RE = re.compile(r"^\{\{EXPAND\}\}\s*(.*)$")
FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)


@dataclass
class DraftBlock:
    text: str
    expand: bool = False
    line_number: int = 0


def parse_draft(content: str) -> list[DraftBlock]:
    content = FRONTMATTER_RE.sub("", content)

    blocks: list[DraftBlock] = []
    for lineno, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue

        match = EXPAND_RE.match(stripped)
        if match:
            blocks.append(
                DraftBlock(text=match.group(1), expand=True, line_number=lineno)
            )
        else:
            blocks.append(DraftBlock(text=stripped, expand=False, line_number=lineno))

    return blocks
