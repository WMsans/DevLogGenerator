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
