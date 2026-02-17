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
