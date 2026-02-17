# Design: TTS Provider System

## 1. Overview

Add support for multiple TTS backends including live voice recording, enabling users to choose their preferred audio synthesis method via CLI flags. The MVP focuses on edge-tts and live recording, with cloud providers (Minimax) to be added later.

## 2. Goals

- Support multiple TTS providers through a unified interface
- Enable live voice recording with automatic sentence splitting
- Maintain backward compatibility with existing edge-tts functionality
- Allow easy extension for future providers (Minimax, etc.)

## 3. Architecture

### 3.1 Module Structure

```
src/devlog/
    audio.py           # Refactored: provider registry + factory
    tts/
        __init__.py    # Exports TTSProvider, get_provider
        base.py        # Abstract TTSProvider class
        edge.py        # EdgeTTSProvider implementation
        live.py        # LiveRecorder implementation
```

### 3.2 Provider Pattern

```
┌─────────────┐
│   render    │
│  (CLI)      │
└──────┬──────┘
       │ --tts <name>
       ▼
┌─────────────┐     ┌──────────────────┐
│ get_provider│────▶│ TTSProvider      │ (abstract)
└─────────────┘     └────────┬─────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │ EdgeTTS     │   │ LiveRecorder│   │ Minimax     │
   │ Provider    │   │             │   │ (future)    │
   └─────────────┘   └─────────────┘   └─────────────┘
```

## 4. Components

### 4.1 `tts/base.py` — Abstract Base Class

```python
from abc import ABC, abstractmethod
from pathlib import Path
from devlog.script_parser import ScriptSegment

class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, output_path: Path, **kwargs) -> Path:
        """Generate audio for a single sentence. Returns path to audio file."""
        pass

    def synthesize_batch(
        self, segments: list[ScriptSegment], work_dir: Path
    ) -> list[tuple[Path, float]]:
        """
        Synthesize all segments. Returns list of (audio_path, duration) tuples.
        Default implementation calls synthesize() for each segment.
        Override for batch-optimized providers.
        """
        results = []
        for i, seg in enumerate(segments):
            audio_path = work_dir / f"seg_{i}.mp3"
            self.synthesize(seg.text, audio_path, **seg.__dict__)
            duration = self._get_duration(audio_path)
            results.append((audio_path, duration))
        return results

    def _get_duration(self, audio_path: Path) -> float:
        """Get audio duration in seconds."""
        # Implementation using moviepy or pydub
        ...

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Provider identifier for CLI selection."""
        pass
```

### 4.2 `tts/edge.py` — Edge-TTS Provider

```python
import asyncio
from pathlib import Path
import edge_tts
from .base import TTSProvider

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
```

### 4.3 `tts/live.py` — Live Recorder

```python
from pathlib import Path
import pyaudio
import webrtcvad
from .base import TTSProvider

class LiveRecorder(TTSProvider):
    CHUNK_SIZE = 480  # 30ms at 16kHz
    SAMPLE_RATE = 16000
    SILENCE_THRESHOLD_MS = 500

    def __init__(self):
        self.audio = pyaudio.PyAudio()

    def synthesize_batch(
        self, segments: list[ScriptSegment], work_dir: Path
    ) -> list[tuple[Path, float]]:
        """
        1. Display script text for reference
        2. Record continuous audio
        3. Auto-split by silence detection
        4. Match split segments to script segments
        """
        # Display script
        print("Script to record:")
        for i, seg in enumerate(segments):
            print(f"  [{i}] {seg.text}")

        # Record audio
        input("Press Enter to start recording...")
        frames = self._record_audio()
        input("Press Enter to stop recording...")

        # Split by silence
        audio_segments = self._split_by_silence(frames)

        # Validate count matches
        if len(audio_segments) != len(segments):
            raise RuntimeError(
                f"Recorded {len(audio_segments)} segments, "
                f"expected {len(segments)}. Please re-record."
            )

        # Save each segment
        results = []
        for i, audio_data in enumerate(audio_segments):
            path = work_dir / f"seg_{i}.wav"
            self._save_wav(audio_data, path)
            duration = len(audio_data) / self.SAMPLE_RATE
            results.append((path, duration))

        return results

    def _record_audio(self) -> bytes:
        """Record audio from microphone."""
        ...

    def _split_by_silence(self, audio_data: bytes) -> list[bytes]:
        """Use webrtcvad to detect silence and split."""
        vad = webrtcvad.Vad(2)  # Aggressiveness 0-3
        # Implementation: find silence gaps >= SILENCE_THRESHOLD_MS
        ...

    def _save_wav(self, audio_data: bytes, path: Path) -> None:
        """Save raw audio to WAV file."""
        ...

    def synthesize(self, text: str, output_path: Path, **kwargs) -> Path:
        """Not used for live recording; synthesize_batch handles everything."""
        raise NotImplementedError("Use synthesize_batch for LiveRecorder")

    @classmethod
    def name(cls) -> str:
        return "live"

    def __del__(self):
        self.audio.terminate()
```

### 4.4 `audio.py` — Refactored

```python
from pathlib import Path
from devlog.tts.base import TTSProvider
from devlog.tts.edge import EdgeTTSProvider
from devlog.tts.live import LiveRecorder

PROVIDERS: dict[str, type[TTSProvider]] = {
    "edge-tts": EdgeTTSProvider,
    "live": LiveRecorder,
}

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
```

## 5. CLI Integration

### 5.1 Updated `render` Command

```python
@app.command()
def render(
    script: Path = typer.Option("script.md", help="Input script file"),
    output: Path = typer.Option("devlog.mp4", help="Output video file"),
    sprites: Path = typer.Option("assets/sprites", help="Sprite directory"),
    tts: str = typer.Option("edge-tts", help="TTS provider"),
    tts_voice: str = typer.Option(None, help="Voice for TTS provider"),
):
    """Phase 3: Render script.md into devlog.mp4."""
    ...
    provider = get_provider(tts, voice=tts_voice)
    render_video(
        segments=segments,
        output_path=output,
        sprite_dir=sprites,
        work_dir=work_dir,
        tts_provider=provider,
    )
```

### 5.2 CLI Usage Examples

```bash
# Default: edge-tts with default voice
devlog render

# edge-tts with custom voice
devlog render --tts edge-tts --tts-voice en-GB-SoniaNeural

# Live recording
devlog render --tts live
```

## 6. Renderer Updates

The renderer's signature changes to accept a provider:

```python
def render_video(
    segments: list[ScriptSegment],
    output_path: Path,
    sprite_dir: Path,
    work_dir: Path,
    tts_provider: TTSProvider,
    size: tuple[int, int] = DEFAULT_SIZE,
    fps: int = 24,
) -> None:
    """Stitch segments into a final video with avatar and voiceover."""
    audio_segments = tts_provider.synthesize_batch(segments, work_dir)

    clips = []
    for (audio_path, duration), seg in zip(audio_segments, segments):
        audio_clip = AudioFileClip(str(audio_path))
        # Use actual duration from audio, not from provider
        ...
```

## 7. Error Handling

| Scenario | Handling |
|----------|----------|
| Unknown provider | Exit with error listing available providers |
| Missing microphone | Check on init, exit with clear error if unavailable |
| Voice not found (edge-tts) | Warn and fall back to default voice |
| Segment count mismatch (live) | Error with counts, prompt to re-record |
| Recording fails | Retry prompt or exit with error |

## 8. Testing Strategy

### 8.1 Unit Tests

- `test_tts_base.py`: Test base class interface
- `test_tts_edge.py`: Mock edge-tts, verify synthesize calls
- `test_tts_live.py`: Test silence detection logic with synthetic audio
- `test_audio.py`: Test provider factory and registry

### 8.2 Integration Tests

- `test_render_edge_tts`: Full render with edge-tts (requires network)
- `test_render_live_mock`: Simulate live recording with pre-recorded audio

## 9. Dependencies

New dependencies added to `pyproject.toml`:

```toml
dependencies = [
    # ... existing
    "pyaudio>=0.2",      # Microphone access for live recording
    "webrtcvad>=2.0",    # Voice activity detection for silence splitting
]
```

Note: PyAudio may require PortAudio to be installed on the system:
- Windows: Usually bundled with PyAudio wheel
- macOS: `brew install portaudio`
- Linux: `sudo apt-get install portaudio19-dev`

## 10. Future Extensions

### 10.1 Minimax Provider (Post-MVP)

```python
class MinimaxProvider(TTSProvider):
    def __init__(self, api_key: str, voice_id: str):
        self.api_key = api_key
        self.voice_id = voice_id

    def synthesize(self, text: str, output_path: Path, **kwargs) -> Path:
        # Call Minimax API
        ...

    @classmethod
    def name(cls) -> str:
        return "minimax"
```

Additional CLI flags:
```bash
devlog render --tts minimax --tts-voice <voice-id> --tts-api-key <key>
```

### 10.2 Voice Cloning Workflow

Future enhancement: Add `devlog voice-clone` subcommand to create a Minimax cloned voice from audio samples.

## 11. Implementation Order

1. Create `tts/` module structure
2. Implement `base.py` abstract class
3. Port existing edge-tts code to `edge.py`
4. Refactor `audio.py` to factory pattern
5. Update `renderer.py` to accept provider
6. Update CLI with `--tts` and `--tts-voice` flags
7. Implement `live.py` with silence detection
8. Add tests for each component
9. Update documentation