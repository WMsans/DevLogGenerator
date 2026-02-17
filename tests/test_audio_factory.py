import pytest

from devlog.audio import get_provider, list_providers
from devlog.tts.edge import EdgeTTSProvider


def test_list_providers_returns_available():
    providers = list_providers()
    assert "edge-tts" in providers


def test_get_provider_returns_edge_tts_instance():
    provider = get_provider("edge-tts", voice="en-GB-SoniaNeural")
    assert isinstance(provider, EdgeTTSProvider)
    assert provider.voice == "en-GB-SoniaNeural"


def test_get_provider_raises_for_unknown():
    with pytest.raises(ValueError, match="Unknown TTS provider"):
        get_provider("unknown-provider")
