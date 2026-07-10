"""End-to-end smoke test: transcribe a real speech file, then summarize + Q&A.

Expects a WAV path as argv[1] (generate one with Windows SAPI — see README).
Run:  python scripts/smoke_test.py path/to/speech.wav
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from audio.analyze import analyze  # noqa: E402
from audio.qa import answer  # noqa: E402
from audio.transcribe import transcribe  # noqa: E402


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python scripts/smoke_test.py <audio-file>")
        sys.exit(2)

    path = sys.argv[1]
    print(f"[transcribe] {path}")
    t = transcribe(path)
    print(f"  language={t.language}  duration={t.duration:.1f}s")
    print(f"  text: {t.text}\n")

    print("[analyze] structured report…")
    r = analyze(t.text)
    print("  summary     :", r.summary)
    print("  key_points  :", r.key_points)
    print("  action_items:", r.action_items)
    print("  topics      :", r.topics, "\n")

    q = "What was agreed to be done, and by when?"
    print(f"[Q&A] Q: {q}")
    print("[Q&A] A:", answer(t.text, q), "\n")

    ok = bool(t.text) and bool(r.summary)
    print("PASS - audio pipeline is live" if ok else "CHECK - review output above")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
