from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    repo_path: Path = field(default_factory=lambda: Path("."))
    draft_path: Path = field(default_factory=lambda: Path("draft.md"))
    script_path: Path = field(default_factory=lambda: Path("script.md"))
    output_path: Path = field(default_factory=lambda: Path("devlog.mp4"))
    ollama_model: str = "llama3"
    ollama_url: str = "http://localhost:11434"
    max_commits: int = 20
    sprite_dir: Path = field(default_factory=lambda: Path("assets/sprites"))