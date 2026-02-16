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
                f"Bullet point: {block.text}\n\n"
                f"Code diff:\n```\n{diff}\n```\n\n"
                "Write the script section:"
            )
            expanded = generate(prompt, model=model, system=EXPAND_SYSTEM)
            sections.append(expanded)
        else:
            sections.append(f"(emotion: happy)\n{block.text}")

    output_path.write_text("\n\n".join(sections) + "\n")
