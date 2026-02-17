import asyncio
from pathlib import Path

import edge_tts

from devlog.tts.base import TTSProvider

DEFAULT_VOICE = "en-US-AvaNeural"


class EdgeTTSProvider(TTSProvider):
    def __init__(self, voice: str = DEFAULT_VOICE):
        self.voice = voice

    def synthesize(self, text: str, output_path: Path, **kwargs) -> Path:
        voice = kwargs.get("voice", self.voice)
        communicate = edge_tts.Communicate(text, voice=voice)
        asyncio.run(communicate.save(str(output_path)))
        return output_path

    @classmethod
    def name(cls) -> str:
        return "edge-tts"
