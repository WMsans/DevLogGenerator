from pathlib import Path

import cv2
import numpy as np
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


def load_sprite_nearest(path: Path, target_height: int) -> np.ndarray:
    """Load and resize sprite using nearest-neighbor interpolation for pixel art."""
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Failed to load sprite: {path}")

    scale = target_height / img.shape[0]
    new_width = int(img.shape[1] * scale)
    resized = cv2.resize(
        img,
        (new_width, target_height),
        interpolation=cv2.INTER_NEAREST,
    )

    if img.shape[2] == 4:
        resized = cv2.cvtColor(resized, cv2.COLOR_BGRA2RGBA)
    else:
        resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

    return resized


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
        audio_path = work_dir / f"seg_{i}.wav"
        synthesize_segment(seg.text, audio_path)
        audio_clip = AudioFileClip(str(audio_path))

        sprite_path = resolve_sprite(seg.emotion, sprite_dir)
        sprite_img = load_sprite_nearest(sprite_path, size[1] // 2)
        sprite_clip = ImageClip(sprite_img).with_duration(audio_clip.duration)

        bg = ImageClip(
            np.full((*size[::-1], 3), BG_COLOR, dtype="uint8")
        ).with_duration(audio_clip.duration)

        frame = CompositeVideoClip([bg, sprite_clip]).with_audio(audio_clip)
        clips.append(frame)

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(str(output_path), fps=fps, logger=None)
