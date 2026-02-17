from pathlib import Path
from unittest.mock import patch

from devlog.draft import generate_draft


FAKE_COMMITS = [
    {"sha": "abc123", "message": "feat: add login", "date": "2025-01-15T10:00:00", "author": "Dev"},
    {"sha": "def456", "message": "fix: null pointer in parser", "date": "2025-01-14T09:00:00", "author": "Dev"},
]


@patch("devlog.draft.generate", return_value="- Added user login with OAuth2 flow\n- Fixed null pointer in the JSON parser")
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
    call_args = mock_llm.call_args[0][0] if mock_llm.call_args[0] else mock_llm.call_args[1]["prompt"]
    assert "login" in call_args.lower()


@patch("devlog.draft.generate", return_value="- Fixed parser\n- Added login")
def test_generate_draft_sorts_chronologically(mock_llm, tmp_path):
    # def456 (Jan 14) is older than abc123 (Jan 15)
    # But we provide them in Jan 15, Jan 14 order
    output = tmp_path / "draft.md"
    generate_draft(
        commits=FAKE_COMMITS,
        selected_indices=[0, 1],
        output_path=output,
        project_name="MyApp",
    )
    content = output.read_text()
    
    # Check frontmatter order
    # It should be def456 followed by abc123
    idx_def = content.find("def456")
    idx_abc = content.find("abc123")
    assert idx_def < idx_abc, "Oldest commit should appear first in frontmatter"

    # Check the prompt order sent to LLM
    call_args = mock_llm.call_args[0][0] if mock_llm.call_args[0] else mock_llm.call_args[1]["prompt"]
    idx_def_prompt = call_args.find("def456")
    idx_abc_prompt = call_args.find("abc123")
    assert idx_def_prompt < idx_abc_prompt, "Oldest commit should appear first in the LLM prompt"