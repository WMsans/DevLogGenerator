from pathlib import Path

from devlog.llm import generate

SUMMARIZE_SYSTEM = (
    "You are a developer writing a casual video dev log script. "
    "Summarize the following git commits into a bullet-point list of updates, "
    "ordered from oldest to newest. "
    "Be concise but technically accurate. Output only the bullet list."
)


def generate_draft(
    commits: list[dict],
    selected_indices: list[int],
    output_path: Path,
    project_name: str = "Project",
    model: str = "qwen3:8b",
) -> None:
    """Generate a draft.md from selected commits via LLM summarization."""
    selected = [commits[i] for i in selected_indices]
    # Sort from oldest to newest (ascending)
    selected.sort(key=lambda x: x["date"])

    commit_text = "\n".join(
        f"- [{c['sha'][:7]}] {c['message']} ({c['date']})" for c in selected
    )

    prompt = f"Commits:\n{commit_text}"
    summary = generate(prompt, model=model, system=SUMMARIZE_SYSTEM)

    frontmatter = (
        f"---\n"
        f'project: "{project_name}"\n'
        f"commits:\n"
        + "".join(f'  - "{c["sha"][:7]}"\n' for c in selected)
        + f"---\n\n"
    )

    body = f"## Updates\n\n{summary}\n"

    output_path.write_text(frontmatter + body)