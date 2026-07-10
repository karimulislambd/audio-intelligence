"""Question answering over a transcript."""
from __future__ import annotations

from groq import Groq

import config
from audio.prompts import QA_SYSTEM


def answer(transcript: str, question: str, history: list[dict] | None = None) -> str:
    """Answer a question grounded in the transcript, with optional prior turns."""
    client = Groq(api_key=config.require_api_key())
    text = transcript[: config.MAX_TRANSCRIPT_CHARS]
    messages: list[dict] = [
        {"role": "system", "content": QA_SYSTEM},
        {"role": "system", "content": f"TRANSCRIPT:\n{text}"},
    ]
    for turn in history or []:
        messages.append({"role": turn["role"], "content": turn["text"]})
    messages.append({"role": "user", "content": question})
    resp = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=messages,
        temperature=config.LLM_TEMPERATURE,
    )
    return resp.choices[0].message.content or ""
