from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

from devlog.renderer import render_video
from devlog.script_parser import ScriptSegment


SEGMENTS = [
    ScriptSegment(text="Hello!", emotion="happy"),
    ScriptSegment(text="This was tricky.", emotion="thinking"),
]


@patch("devlog.renderer.load_sprite_nearest")
@patch("devlog.renderer.concatenate_videoclips")
@patch("devlog.renderer.CompositeVideoClip")
@patch("devlog.renderer.AudioFileClip")
@patch("devlog.renderer.ImageClip")
@patch("devlog.renderer.synthesize_segment")
@patch("devlog.renderer.resolve_sprite")
def test_render_creates_mp4(
    mock_sprite,
    mock_synth,
    mock_imgclip,
    mock_audioclip,
    mock_composite,
    mock_concat,
    mock_load_sprite,
    tmp_path,
):
    mock_sprite.return_value = tmp_path / "sprite.png"
    mock_load_sprite.return_value = np.zeros((100, 100, 3), dtype="uint8")

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

    assert mock_synth.call_count == 2
    mock_final.write_videofile.assert_called_once()
