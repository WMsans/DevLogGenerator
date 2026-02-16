## Task 10: Video Renderer (Phase 3 — Render)

**Files:**
- Create: `src/devlog/renderer.py`
- Create: `tests/test_renderer.py`

**Step 1: Write the failing test**

```python
# tests/test_renderer.py
from pathlib import Path
from unittest.mock import patch, MagicMock, call

from devlog.renderer import render_video
from devlog.script_parser import ScriptSegment


SEGMENTS = [
    ScriptSegment(text="Hello!", emotion="happy"),
    ScriptSegment(text="This was tricky.", emotion="thinking"),
]


@patch("devlog.renderer.concatenate_videoclips")
@patch("devlog.renderer.CompositeVideoClip")
@patch("devlog.renderer.AudioFileClip")
@patch("devlog.renderer.ImageClip")
@patch("devlog.renderer.synthesize_segment")
@patch("devlog.renderer.resolve_sprite")
def test_render_creates_mp4(
    mock_sprite, mock_synth, mock_imgclip, mock_audioclip,
    mock_composite, mock_concat, tmp_path
):
    # Setup mocks
    mock_sprite.return_value = tmp_path / "sprite.png"
    (tmp_path / "sprite.png").write_bytes(b"PNG")

    mock_synth.return_value = tmp_path / "audio.wav"

    mock_audio_inst = MagicMock()
    mock_audio_inst.duration = 3.0
    mock_audioclip.return_value = mock_audio_inst

    mock_img_inst = MagicMock()
    mock_imgclip.return_value = mock_img_inst
    mock_img_inst.with_duration.return_value = mock_img_inst
    mock_img_inst.resized.return_value = mock_img_inst

    mock_comp_inst = MagicMock()
    mock_composite.return_value = mock_comp_inst
    mock_comp_inst.with_audio.return_value = mock_comp_inst

    mock_final = MagicMock()
    mock_concat.return_value = mock_final

    output = tmp_path / "out.mp4"
    render_video(
        segments=SEGMENTS,
        output_path=output,
        sprite_dir=tmp_path,
        work_dir=tmp_path,
    )

    # Verify TTS was called for each segment
    assert mock_synth.call_count == 2
    # Verify final video was written
    mock_final.write_videofile.assert_called_once()
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_renderer.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/devlog/renderer.py
from pathlib import Path

from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    concatenate_videoclips,
)

from devlog.audio import synthesize_segment
from devlog.script_parser import ScriptSegment
from devlog.sprites import resolve_sprite

DEFAULT_SIZE = (1280, 720)
BG_COLOR = (30, 30, 30)


def render_video(
    segments: list[ScriptSegment],
    output_path: Path,
    sprite_dir: Path,
    work_dir: Path,
    size: tuple[int, int] = DEFAULT_SIZE,
    fps: int = 24,
) -> None:
    """Stitch segments into a final video with avatar and voiceover."""
    clips = []

    for i, seg in enumerate(segments):
        # 1. Synthesize audio
        audio_path = work_dir / f"seg_{i}.wav"
        synthesize_segment(seg.text, audio_path)
        audio_clip = AudioFileClip(str(audio_path))

        # 2. Resolve sprite
        sprite_path = resolve_sprite(seg.emotion, sprite_dir)
        sprite_clip = (
            ImageClip(str(sprite_path))
            .with_duration(audio_clip.duration)
            .resized(height=size[1] // 2)
        )

        # 3. Compose frame: background + sprite
        bg = ImageClip(
            # numpy array for solid color
            __import__("numpy").full((*size[::-1], 3), BG_COLOR, dtype="uint8")
        ).with_duration(audio_clip.duration)

        frame = CompositeVideoClip([bg, sprite_clip]).with_audio(audio_clip)
        clips.append(frame)

    # 4. Concatenate all segments
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(str(output_path), fps=fps, logger=None)
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_renderer.py -v
```

Expected: 1 PASS

**Step 5: Commit**

```bash
git add src/devlog/renderer.py tests/test_renderer.py
git commit -m "feat: add video renderer with sprite + TTS compositing"
```
