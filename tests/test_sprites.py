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
