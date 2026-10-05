"""Central configuration for the audio intelligence app."""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

# --- LLM (Groq) for summary + Q&A over the transcript ---
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
LLM_MODEL: str = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))

# --- Speech-to-text (faster-whisper) ---
# "base" balances speed and accuracy on free CPU hosting. "tiny" is faster,
# "small" is more accurate but heavier.
WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
WHISPER_COMPUTE: str = os.getenv("WHISPER_COMPUTE", "int8")  # int8 = small + fast on CPU

# --- Upload guards ---
MAX_AUDIO_MB: int = int(os.getenv("MAX_AUDIO_MB", "25"))
ALLOWED_AUDIO: tuple[str, ...] = ("mp3", "wav", "m4a", "ogg", "flac", "webm")

# Transcript sent to the LLM is capped to stay within context + free-tier limits.
MAX_TRANSCRIPT_CHARS: int = 12000


def require_api_key() -> str:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Get a free key at https://console.groq.com "
            "and add it to a .env file (see .env.example)."
        )
    return GROQ_API_KEY
