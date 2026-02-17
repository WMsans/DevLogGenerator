from pathlib import Path

from devlog.tts.base import TTSProvider
from devlog.tts.edge import EdgeTTSProvider
from devlog.tts.live import LiveRecorder

PROVIDERS: dict[str, type[TTSProvider]] = {
    "edge-tts": EdgeTTSProvider,
    "live": LiveRecorder,
}

DEFAULT_VOICE = "en-US-AvaNeural"


def get_provider(name: str, **kwargs) -> TTSProvider:
    """
    Factory function to get a TTS provider instance.

    Args:
        name: Provider name ("edge-tts", "live", etc.)
        **kwargs: Provider-specific options (e.g., voice="en-US-AvaNeural")

    Returns:
        Configured TTSProvider instance

    Raises:
        ValueError: If provider name is not recognized
    """
    if name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown TTS provider '{name}'. Available: {available}")

    provider_class = PROVIDERS[name]
    return provider_class(**kwargs)


def list_providers() -> list[str]:
    """Return list of available provider names."""
    return list(PROVIDERS.keys())


def synthesize_segment(
    text: str,
    output_path: Path,
    voice: str = DEFAULT_VOICE,
) -> Path:
    """Legacy function for backward compatibility. Uses edge-tts."""
    provider = get_provider("edge-tts", voice=voice)
    return provider.synthesize(text, output_path)
