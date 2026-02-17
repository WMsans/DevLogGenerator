# TTS Provider System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add support for multiple TTS backends (edge-tts and live recording) via a provider pattern with CLI flags.

**Architecture:** Abstract `TTSProvider` base class with concrete implementations for edge-tts and live recording. Factory function in `audio.py` returns configured provider. Renderer accepts provider via dependency injection.

**Tech Stack:** Python 3.10+, edge-tts, PyAudio, webrtcvad, moviepy

---

### Task 1: Create tts module structure

**Files:**
- Create: `src/devlog/tts/__init__.py`
- Create: `src/devlog/tts/base.py`

**Step 1: Create tts package directory**

```bash
mkdir src/devlog/tts
```

**Step 2: Create `src/devlog/tts/__init__.py`**

```python
from devlog.tts.base import TTSProvider

__all__ = ["TTSProvider"]
```

**Step 3: Create `src/devlog/tts/base.py`**

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
        """
        results = []
        for i, seg in enumerate(segments):
            audio_path = work_dir / f"seg_{i}.mp3"
            self.synthesize(seg.text, audio_path)
            duration = self._get_duration(audio_path)
            results.append((audio_path, duration))
        return results

    def _get_duration(self, audio_path: Path) -> float:
        """Get audio duration in seconds using moviepy."""
        from moviepy import AudioFileClip

        with AudioFileClip(str(audio_path)) as clip:
            return clip.duration

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Provider identifier for CLI selection."""
        pass
```

**Step 4: Commit**

```bash
git add src/devlog/tts/
git commit -m "feat: add TTSProvider abstract base class"
```

---

### Task 2: Implement EdgeTTSProvider

**Files:**
- Create: `src/devlog/tts/edge.py`
- Create: `tests/test_tts_edge.py`

**Step 1: Write the failing test**

Create `tests/test_tts_edge.py`:

```python
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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_tts_edge.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'devlog.tts.edge'"

**Step 3: Create `src/devlog/tts/edge.py`**

```python
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
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_tts_edge.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/devlog/tts/edge.py tests/test_tts_edge.py
git commit -m "feat: add EdgeTTSProvider implementation"
```

---

### Task 3: Update audio.py with provider factory

**Files:**
- Modify: `src/devlog/audio.py`
- Modify: `src/devlog/tts/__init__.py`
- Create: `tests/test_audio_factory.py`

**Step 1: Write the failing test**

Create `tests/test_audio_factory.py`:

```python
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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_audio_factory.py -v
```

Expected: FAIL with "ImportError: cannot import name 'get_provider'"

**Step 3: Update `src/devlog/audio.py`**

Replace entire file with:

```python
from pathlib import Path

from devlog.tts.base import TTSProvider
from devlog.tts.edge import EdgeTTSProvider

PROVIDERS: dict[str, type[TTSProvider]] = {
    "edge-tts": EdgeTTSProvider,
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
```

**Step 4: Update `src/devlog/tts/__init__.py`**

```python
from devlog.tts.base import TTSProvider
from devlog.tts.edge import EdgeTTSProvider

__all__ = ["TTSProvider", "EdgeTTSProvider"]
```

**Step 5: Run test to verify it passes**

```bash
pytest tests/test_audio_factory.py -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add src/devlog/audio.py src/devlog/tts/__init__.py tests/test_audio_factory.py
git commit -m "refactor: add TTS provider factory to audio.py"
```

---

### Task 4: Update renderer to accept TTS provider

**Files:**
- Modify: `src/devlog/renderer.py`
- Modify: `tests/test_renderer.py`

**Step 1: Read current renderer to understand tests**

```bash
pytest tests/test_renderer.py -v
```

**Step 2: Update `src/devlog/renderer.py`**

Change the function signature and implementation:

```python
from pathlib import Path

import cv2
import numpy as np
from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    concatenate_videoclips,
)

from devlog.audio import get_provider
from devlog.script_parser import ScriptSegment
from devlog.sprites import resolve_sprite
from devlog.tts.base import TTSProvider

DEFAULT_SIZE = (1280, 720)
BG_COLOR = (0, 255, 0)


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
    tts_provider: TTSProvider | None = None,
    size: tuple[int, int] = DEFAULT_SIZE,
    fps: int = 24,
) -> None:
    """Stitch segments into a final video with avatar and voiceover."""
    if tts_provider is None:
        tts_provider = get_provider("edge-tts")

    clips = []
    audio_segments = tts_provider.synthesize_batch(segments, work_dir)

    for (audio_path, _), seg in zip(audio_segments, segments):
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
```

**Step 3: Run tests to verify nothing broke**

```bash
pytest tests/test_renderer.py -v
```

Expected: PASS (may need test updates if they mock synthesize_segment)

**Step 4: Commit**

```bash
git add src/devlog/renderer.py
git commit -m "refactor: accept TTSProvider in render_video"
```

---

### Task 5: Update CLI with --tts and --tts-voice flags

**Files:**
- Modify: `src/devlog/cli.py`
- Modify: `tests/test_cli.py`

**Step 1: Write the failing test**

Add to `tests/test_cli.py`:

```python
def test_render_accepts_tts_flag():
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("script.md").write_text("(emotion: neutral)\nHello world")
        Path("assets/sprites").mkdir(parents=True)
        result = runner.invoke(app, ["render", "--tts", "edge-tts", "--tts-voice", "en-US-AvaNeural"])
        assert result.exit_code == 0 or "edge-tts" in result.output
```

**Step 2: Update `src/devlog/cli.py`**

Modify the `render` command:

```python
@app.command()
def render(
    script: Path = typer.Option("script.md", help="Input script file"),
    output: Path = typer.Option("devlog.mp4", help="Output video file"),
    sprites: Path = typer.Option("assets/sprites", help="Sprite directory"),
    tts: str = typer.Option("edge-tts", help="TTS provider (edge-tts, live)"),
    tts_voice: str = typer.Option(None, help="Voice for TTS provider"),
):
    """Phase 3: Render script.md into devlog.mp4."""
    if not script.exists():
        typer.echo(f"Script not found: {script}")
        raise typer.Exit(1)

    content = script.read_text()
    segments = parse_script(content)

    if not segments:
        typer.echo("No segments found in script.")
        raise typer.Exit(1)

    work_dir = Path(".devlog_tmp")
    work_dir.mkdir(exist_ok=True)

    kwargs = {}
    if tts_voice:
        kwargs["voice"] = tts_voice

    try:
        provider = get_provider(tts, **kwargs)
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)

    render_video(
        segments=segments,
        output_path=output,
        sprite_dir=sprites,
        work_dir=work_dir,
        tts_provider=provider,
    )
    typer.echo(f"Video rendered to {output}")
```

Also add import at top:

```python
from devlog.audio import get_provider
```

**Step 3: Run tests**

```bash
pytest tests/test_cli.py -v
```

Expected: PASS

**Step 4: Commit**

```bash
git add src/devlog/cli.py tests/test_cli.py
git commit -m "feat: add --tts and --tts-voice CLI flags to render command"
```

---

### Task 6: Add PyAudio and webrtcvad dependencies

**Files:**
- Modify: `pyproject.toml`

**Step 1: Update `pyproject.toml`**

Add to dependencies array:

```toml
dependencies = [
    "typer>=0.9",
    "questionary>=2.0",
    "GitPython>=3.1",
    "requests>=2.31",
    "moviepy>=1.0",
    "edge-tts>=6.0",
    "opencv-python>=4.8",
    "pyaudio>=0.2",
    "webrtcvad>=2.0",
]
```

**Step 2: Install dependencies**

```bash
pip install -e ".[dev]"
```

**Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add pyaudio and webrtcvad dependencies"
```

---

### Task 7: Implement LiveRecorder with silence detection

**Files:**
- Create: `src/devlog/tts/live.py`
- Create: `tests/test_tts_live.py`

**Step 1: Write the failing tests**

Create `tests/test_tts_live.py`:

```python
import struct
import wave
from pathlib import Path

import pytest

from devlog.tts.live import LiveRecorder


def test_live_recorder_name():
    assert LiveRecorder.name() == "live"


def test_split_by_silence_splits_on_gaps():
    recorder = LiveRecorder.__new__(LiveRecorder)
    recorder.SAMPLE_RATE = 16000
    recorder.SILENCE_THRESHOLD_MS = 500

    audio_data = recorder._create_test_audio_with_silence()
    segments = recorder._split_by_silence(audio_data)

    assert len(segments) == 3


def test_save_wav_creates_valid_file(tmp_path):
    recorder = LiveRecorder.__new__(LiveRecorder)
    recorder.SAMPLE_RATE = 16000

    audio_data = b"\x00\x00" * 16000
    output_path = tmp_path / "test.wav"

    recorder._save_wav(audio_data, output_path)

    assert output_path.exists()
    with wave.open(str(output_path), "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getframerate() == 16000


def test_synthesize_raises_not_implemented():
    recorder = LiveRecorder.__new__(LiveRecorder)
    with pytest.raises(NotImplementedError, match="Use synthesize_batch"):
        recorder.synthesize("text", Path("output.wav"))
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_tts_live.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'devlog.tts.live'"

**Step 3: Create `src/devlog/tts/live.py`**

```python
import struct
import wave
from pathlib import Path

import pyaudio
import webrtcvad

from devlog.script_parser import ScriptSegment
from devlog.tts.base import TTSProvider


class LiveRecorder(TTSProvider):
    CHUNK_SIZE = 480
    SAMPLE_RATE = 16000
    SILENCE_THRESHOLD_MS = 500
    FORMAT = pyaudio.paInt16
    CHANNELS = 1

    def __init__(self):
        self.audio = pyaudio.PyAudio()

    def synthesize(self, text: str, output_path: Path, **kwargs) -> Path:
        raise NotImplementedError("Use synthesize_batch for LiveRecorder")

    def synthesize_batch(
        self, segments: list[ScriptSegment], work_dir: Path
    ) -> list[tuple[Path, float]]:
        print("\nScript to record:")
        for i, seg in enumerate(segments):
            print(f"  [{i}] {seg.text}")
        print()

        input("Press Enter to start recording...")
        print("Recording... Press Enter to stop.")

        audio_data = self._record_audio()
        audio_segments = self._split_by_silence(audio_data)

        if len(audio_segments) != len(segments):
            raise RuntimeError(
                f"Recorded {len(audio_segments)} segments, "
                f"expected {len(segments)}. Please re-record with clearer pauses."
            )

        results = []
        for i, segment_data in enumerate(audio_segments):
            path = work_dir / f"seg_{i}.wav"
            self._save_wav(segment_data, path)
            duration = len(segment_data) / (self.SAMPLE_RATE * 2)
            results.append((path, duration))

        print(f"Recorded {len(results)} segments.")
        return results

    def _record_audio(self) -> bytes:
        stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.SAMPLE_RATE,
            input=True,
            frames_per_buffer=self.CHUNK_SIZE,
        )

        frames = []
        try:
            while True:
                try:
                    data = stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                    frames.append(data)
                except KeyboardInterrupt:
                    break
        finally:
            stream.stop_stream()
            stream.close()

        return b"".join(frames)

    def _split_by_silence(self, audio_data: bytes) -> list[bytes]:
        vad = webrtcvad.Vad(2)
        frame_duration_ms = 30
        frame_size = int(self.SAMPLE_RATE * frame_duration_ms / 1000) * 2

        frames = []
        for i in range(0, len(audio_data) - frame_size, frame_size):
            frame = audio_data[i : i + frame_size]
            frames.append(frame)

        is_speech = [vad.is_speech(f, self.SAMPLE_RATE) for f in frames]

        segments = []
        current_segment_frames = []
        silence_frames = 0
        silence_threshold = self.SILENCE_THRESHOLD_MS // frame_duration_ms

        for i, speech in enumerate(is_speech):
            if speech:
                if silence_frames > 0 and current_segment_frames:
                    current_segment_frames.extend(
                        frames[i - silence_frames : i]
                    )
                current_segment_frames.append(frames[i])
                silence_frames = 0
            else:
                if current_segment_frames:
                    silence_frames += 1
                    if silence_frames >= silence_threshold:
                        segment_data = b"".join(current_segment_frames)
                        if len(segment_data) > self.SAMPLE_RATE * 0.1 * 2:
                            segments.append(segment_data)
                        current_segment_frames = []
                        silence_frames = 0

        if current_segment_frames:
            segment_data = b"".join(current_segment_frames)
            if len(segment_data) > self.SAMPLE_RATE * 0.1 * 2:
                segments.append(segment_data)

        return segments

    def _save_wav(self, audio_data: bytes, path: Path) -> None:
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(self.SAMPLE_RATE)
            wf.writeframes(audio_data)

    def _create_test_audio_with_silence(self) -> bytes:
        segment_duration = int(self.SAMPLE_RATE * 0.3)
        silence_duration = int(self.SAMPLE_RATE * 0.6)

        audio = b""
        for _ in range(3):
            audio += b"\x7F\x7F" * segment_duration
            audio += b"\x00\x00" * silence_duration
        return audio

    @classmethod
    def name(cls) -> str:
        return "live"

    def __del__(self):
        if hasattr(self, "audio"):
            self.audio.terminate()
```

**Step 4: Run tests**

```bash
pytest tests/test_tts_live.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/devlog/tts/live.py tests/test_tts_live.py
git commit -m "feat: add LiveRecorder with silence detection"
```

---

### Task 8: Register LiveRecorder in provider factory

**Files:**
- Modify: `src/devlog/audio.py`
- Modify: `tests/test_audio_factory.py`

**Step 1: Update test**

Add to `tests/test_audio_factory.py`:

```python
from devlog.tts.live import LiveRecorder


def test_list_providers_includes_live():
    providers = list_providers()
    assert "live" in providers


def test_get_provider_returns_live_instance():
    provider = get_provider("live")
    assert isinstance(provider, LiveRecorder)
```

**Step 2: Update `src/devlog/audio.py`**

Add import and register:

```python
from devlog.tts.live import LiveRecorder

PROVIDERS: dict[str, type[TTSProvider]] = {
    "edge-tts": EdgeTTSProvider,
    "live": LiveRecorder,
}
```

**Step 3: Run tests**

```bash
pytest tests/test_audio_factory.py -v
```

Expected: PASS

**Step 4: Commit**

```bash
git add src/devlog/audio.py tests/test_audio_factory.py
git commit -m "feat: register LiveRecorder in provider factory"
```

---

### Task 9: Run full test suite

**Step 1: Run all tests**

```bash
pytest -v
```

**Step 2: Fix any failing tests**

**Step 3: Final commit if fixes needed**

---

### Task 10: Manual verification

**Step 1: Test edge-tts rendering**

```bash
devlog render --tts edge-tts --tts-voice en-US-AvaNeural
```

**Step 2: Verify output video plays correctly**

---

## Summary

This plan implements a TTS provider system with:

1. Abstract `TTSProvider` base class
2. `EdgeTTSProvider` wrapping existing edge-tts
3. `LiveRecorder` with silence-based auto-splitting
4. Factory pattern in `audio.py`
5. CLI flags `--tts` and `--tts-voice`
6. Updated renderer accepting provider via DI

Each task follows TDD: write failing test → implement → verify → commit.