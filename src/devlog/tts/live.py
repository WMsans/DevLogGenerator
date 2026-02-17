import wave
from pathlib import Path

import webrtcvad

from devlog.script_parser import ScriptSegment
from devlog.tts.base import TTSProvider


class LiveRecorder(TTSProvider):
    CHUNK_SIZE = 480
    SAMPLE_RATE = 16000
    SILENCE_THRESHOLD_MS = 500
    CHANNELS = 1

    def __init__(self):
        self._audio = None

    def _get_audio(self):
        if self._audio is None:
            import pyaudio

            self._audio = pyaudio.PyAudio()
        return self._audio

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
        import pyaudio

        audio = self._get_audio()
        stream = audio.open(
            format=pyaudio.paInt16,
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
                    current_segment_frames.extend(frames[i - silence_frames : i])
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
            audio += b"\x7f\x7f" * segment_duration
            audio += b"\x00\x00" * silence_duration
        return audio

    @classmethod
    def name(cls) -> str:
        return "live"

    def __del__(self):
        if hasattr(self, "_audio") and self._audio is not None:
            self._audio.terminate()
