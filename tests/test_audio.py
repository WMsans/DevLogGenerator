from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from devlog.audio import synthesize_segment


@patch("devlog.audio.edge_tts.Communicate")
def test_synthesize_creates_mp3(mock_communicate_class, tmp_path):
    mock_communicate = MagicMock()
    mock_communicate.save = AsyncMock()
    mock_communicate_class.return_value = mock_communicate

    output = tmp_path / "segment.mp3"
    synthesize_segment("Hello world", output)

    mock_communicate_class.assert_called_once()
    mock_communicate.save.assert_called_once_with(str(output))


@patch("devlog.audio.edge_tts.Communicate")
def test_synthesize_uses_provided_voice(mock_communicate_class, tmp_path):
    mock_communicate = MagicMock()
    mock_communicate.save = AsyncMock()
    mock_communicate_class.return_value = mock_communicate

    output = tmp_path / "segment.mp3"
    synthesize_segment("Test", output, voice="en-US-GuyNeural")

    mock_communicate_class.assert_called_once_with("Test", voice="en-US-GuyNeural")
