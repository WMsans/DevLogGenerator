from pathlib import Path
from unittest.mock import patch

from devlog.expander import expand_draft
from devlog.md_parser import DraftBlock


FAKE_BLOCKS = [
    DraftBlock(text="* Feature A is done", expand=False, line_number=1),
    DraftBlock(text="* Feature B had tricky bugs", expand=True, line_number=2),
]


@patch(
    "devlog.expander.get_diff_text",
    return_value="+def allocate():\n+    return malloc(64)",
)
@patch(
    "devlog.expander.generate",
    return_value="(emotion: thinking)\nFeature B required rewriting the allocator to use 64-byte blocks.",
)
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
