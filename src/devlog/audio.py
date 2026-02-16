import asyncio
from pathlib import Path

import edge_tts

DEFAULT_VOICE = "en-US-AvaNeural"


def synthesize_segment(
    text: str,
    output_path: Path,
    voice: str = DEFAULT_VOICE,
) -> Path:
    """Synthesize text to an MP3 file using edge-tts. Returns the output path."""
    communicate = edge_tts.Communicate(text, voice=voice)

    async def _save():
        await communicate.save(str(output_path))

    asyncio.run(_save())
    return output_path
