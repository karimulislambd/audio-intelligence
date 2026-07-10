"""Unit tests that run in CI without an API key or the Whisper model.

They cover the deterministic logic: JSON report parsing and transcript formatting.
"""
from __future__ import annotations

from audio.analyze import _parse
from audio.transcribe import Segment, Transcript


def test_parse_clean_report():
    raw = (
        '{"summary":"We discussed Q4.","key_points":["revenue up"],'
        '"action_items":["ship feature"],"topics":["finance"]}'
    )
    r = _parse(raw)
    assert r.summary == "We discussed Q4."
    assert r.key_points == ["revenue up"]
    assert r.action_items == ["ship feature"]
    assert r.topics == ["finance"]


def test_parse_report_with_surrounding_text():
    raw = 'Sure!\n{"summary":"A talk on AI","key_points":[],"action_items":[],"topics":["ai"]}\nDone'
    r = _parse(raw)
    assert r.summary == "A talk on AI"
    assert r.topics == ["ai"]


def test_parse_garbage_falls_back():
    r = _parse("not json")
    assert r.summary == "not json"
    assert r.key_points == []


def test_transcript_timestamped_formatting():
    t = Transcript(
        text="hello world",
        segments=[
            Segment(start=0.0, end=2.0, text="hello"),
            Segment(start=65.0, end=67.0, text="world"),
        ],
    )
    out = t.timestamped()
    assert "[00:00] hello" in out
    assert "[01:05] world" in out
