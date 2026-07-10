"""Turn a transcript into a structured report: summary, key points, action items, topics."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from groq import Groq

import config
from audio.prompts import ANALYZE_SYSTEM


@dataclass
class Report:
    summary: str = ""
    key_points: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    raw: str = ""


def _coerce_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)] if value else []


def _parse(raw: str) -> Report:
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if not match:
        return Report(summary=raw.strip(), raw=raw)
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return Report(summary=raw.strip(), raw=raw)
    return Report(
        summary=str(data.get("summary", "")),
        key_points=_coerce_list(data.get("key_points")),
        action_items=_coerce_list(data.get("action_items")),
        topics=_coerce_list(data.get("topics")),
        raw=raw,
    )


def analyze(transcript: str) -> Report:
    """Produce a structured report from a transcript."""
    client = Groq(api_key=config.require_api_key())
    text = transcript[: config.MAX_TRANSCRIPT_CHARS]
    resp = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": ANALYZE_SYSTEM},
            {"role": "user", "content": f"Transcript:\n\n{text}"},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    return _parse(resp.choices[0].message.content or "")
