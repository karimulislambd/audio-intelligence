"""Local speech-to-text with faster-whisper (no API, no cost).

The model is loaded once and reused. faster-whisper decodes audio via a bundled
ffmpeg (through the `av` package), so no system ffmpeg install is required.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

from faster_whisper import WhisperModel

import config


@dataclass
class Segment:
    start: float
    end: float
    text: str


@dataclass
class Transcript:
    text: str
    language: str = ""
    duration: float = 0.0
    segments: list[Segment] = field(default_factory=list)

    def timestamped(self) -> str:
        """Return the transcript with [mm:ss] markers per segment."""
        lines = []
        for s in self.segments:
            mm, ss = divmod(int(s.start), 60)
            lines.append(f"[{mm:02d}:{ss:02d}] {s.text.strip()}")
        return "\n".join(lines)


@lru_cache(maxsize=1)
def _model() -> WhisperModel:
    return WhisperModel(
        config.WHISPER_MODEL,
        device="cpu",
        compute_type=config.WHISPER_COMPUTE,
    )


def transcribe(audio_path: str) -> Transcript:
    """Transcribe an audio file into text + timestamped segments."""
    segments_iter, info = _model().transcribe(audio_path, beam_size=1)
    segments: list[Segment] = []
    parts: list[str] = []
    for seg in segments_iter:
        segments.append(Segment(start=seg.start, end=seg.end, text=seg.text))
        parts.append(seg.text.strip())
    return Transcript(
        text=" ".join(parts).strip(),
        language=info.language,
        duration=info.duration,
        segments=segments,
    )
