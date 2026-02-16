## Task 8: TTS Audio Pipeline

**Files:**
- Create: `src/devlog/audio.py`
- Create: `tests/test_audio.py`

**Step 1: Write the failing test**

```python
# tests/test_audio.py
from pathlib import Path
from unittest.mock import patch, MagicMock

from devlog.audio import synthesize_segment


@patch("devlog.audio.TTS")
def test_synthesize_creates_wav(mock_tts_class, tmp_path):
    mock_tts = MagicMock()
    mock_tts_class.return_value = mock_tts

    output = tmp_path / "segment.wav"
    synthesize_segment("Hello world", output)

    mock_tts.tts_to_file.assert_called_once()
    call_kwargs = mock_tts.tts_to_file.call_args
    assert str(output) in str(call_kwargs)


@patch("devlog.audio.TTS")
def test_synthesize_uses_provided_model(mock_tts_class, tmp_path):
    mock_tts = MagicMock()
    mock_tts_class.return_value = mock_tts

    output = tmp_path / "segment.wav"
    synthesize_segment("Test", output, model_name="tts_models/en/ljspeech/tacotron2-DDC")

    mock_tts_class.assert_called_once_with(model_name="tts_models/en/ljspeech/tacotron2-DDC")
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_audio.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/devlog/audio.py
from pathlib import Path

from TTS.api import TTS

DEFAULT_MODEL = "tts_models/en/ljspeech/tacotron2-DDC"

_tts_cache: dict[str, TTS] = {}


def _get_tts(model_name: str) -> TTS:
    """Cache TTS model instances to avoid reloading."""
    if model_name not in _tts_cache:
        _tts_cache[model_name] = TTS(model_name=model_name)
    return _tts_cache[model_name]


def synthesize_segment(
    text: str,
    output_path: Path,
    model_name: str = DEFAULT_MODEL,
) -> Path:
    """Synthesize text to a WAV file. Returns the output path."""
    tts = _get_tts(model_name)
    tts.tts_to_file(text=text, file_path=str(output_path))
    return output_path
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_audio.py -v
```

Expected: 2 PASS

**Step 5: Commit**

```bash
git add src/devlog/audio.py tests/test_audio.py
git commit -m "feat: add TTS audio synthesis wrapper"
```
