from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from devlog.tts.edge import EdgeTTSProvider


def test_edge_tts_provider_name():
    assert EdgeTTSProvider.name() == "edge-tts"


def test_edge_tts_synthesize_calls_edge_tts(tmp_path):
    output_path = tmp_path / "test.mp3"

    with patch("devlog.tts.edge.edge_tts.Communicate") as mock_communicate:
        mock_instance = MagicMock()
        mock_instance.save = AsyncMock()
        mock_communicate.return_value = mock_instance

        provider = EdgeTTSProvider(voice="en-US-AvaNeural")
        result = provider.synthesize("Hello world", output_path)

        assert result == output_path
        mock_communicate.assert_called_once_with("Hello world", voice="en-US-AvaNeural")
        mock_instance.save.assert_called_once()
