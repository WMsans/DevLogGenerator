from pathlib import Path

SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")


def resolve_sprite(emotion: str, sprite_dir: Path) -> Path:
    """Find the sprite image for a given emotion, falling back to neutral."""
    for ext in SUPPORTED_EXTENSIONS:
        candidate = sprite_dir / f"{emotion}{ext}"
        if candidate.exists():
            return candidate

    if emotion != "neutral":
        return resolve_sprite("neutral", sprite_dir)

    raise FileNotFoundError(
        f"No sprite found for '{emotion}' in {sprite_dir}. "
        f"Add at least a neutral.png file."
    )
