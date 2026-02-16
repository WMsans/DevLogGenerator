## Task 9: Sprite / Asset Resolver

**Files:**
- Create: `src/devlog/sprites.py`
- Create: `tests/test_sprites.py`
- Create: `assets/sprites/.gitkeep`

**Step 1: Write the failing test**

```python
# tests/test_sprites.py
from pathlib import Path

from devlog.sprites import resolve_sprite


def test_resolve_existing_sprite(tmp_path):
    sprite_dir = tmp_path / "sprites"
    sprite_dir.mkdir()
    (sprite_dir / "happy.png").write_bytes(b"PNG_DATA")

    path = resolve_sprite("happy", sprite_dir)
    assert path.name == "happy.png"
    assert path.exists()


def test_resolve_missing_sprite_falls_back_to_neutral(tmp_path):
    sprite_dir = tmp_path / "sprites"
    sprite_dir.mkdir()
    (sprite_dir / "neutral.png").write_bytes(b"PNG_DATA")

    path = resolve_sprite("excited", sprite_dir)
    assert path.name == "neutral.png"


def test_resolve_raises_if_no_fallback(tmp_path):
    sprite_dir = tmp_path / "sprites"
    sprite_dir.mkdir()
    try:
        resolve_sprite("happy", sprite_dir)
        assert False, "Should have raised"
    except FileNotFoundError:
        pass
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_sprites.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/devlog/sprites.py
from pathlib import Path

SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")


def resolve_sprite(emotion: str, sprite_dir: Path) -> Path:
    """Find the sprite image for a given emotion, falling back to neutral."""
    for ext in SUPPORTED_EXTENSIONS:
        candidate = sprite_dir / f"{emotion}{ext}"
        if candidate.exists():
            return candidate

    # Fallback to neutral
    if emotion != "neutral":
        return resolve_sprite("neutral", sprite_dir)

    raise FileNotFoundError(
        f"No sprite found for '{emotion}' in {sprite_dir}. "
        f"Add at least a neutral.png file."
    )
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_sprites.py -v
```

Expected: 3 PASS

**Step 5: Commit**

```bash
mkdir -p assets/sprites
touch assets/sprites/.gitkeep
git add src/devlog/sprites.py tests/test_sprites.py assets/sprites/.gitkeep
git commit -m "feat: add sprite resolver with fallback logic"
```
