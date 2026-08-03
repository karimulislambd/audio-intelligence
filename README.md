# Audio Intelligence

[![CI](https://github.com/karimulislambd/audio-intelligence/actions/workflows/ci.yml/badge.svg)](https://github.com/karimulislambd/audio-intelligence/actions/workflows/ci.yml)
[![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](#)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Lint: ruff](https://img.shields.io/badge/lint-ruff-000000?logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)

> Upload a meeting, lecture, or interview recording and get a **transcript**, a **structured
> report** (summary, key points, action items, topics), and a **Q&A chat** over what was said.

A two-stage pipeline: **local speech-to-text** (faster-whisper, no API cost) feeds an **LLM**
(Llama 3.3 on Groq) that turns raw talk into structured, searchable intelligence.

**Live demo:** https://audio-intelligence-karimulislambd.streamlit.app/

---
  
## What it does

| Step | Output |
|---|---|
| **Transcribe** | Full, timestamped transcript via faster-whisper (runs locally) |
| **Analyze** | JSON report: `summary`, `key_points`, `action_items`, `topics` |
| **Ask** | Chat grounded in the transcript — "what did we decide, and by when?" |

## Why this project

| Skill it demonstrates | Where |
|---|---|
| **Speech-to-text pipelines** | faster-whisper wrapper with timestamped segments (`audio/transcribe.py`) |
| **LLM structured extraction** | JSON-mode report with defensive parsing (`audio/analyze.py`) |
| **Grounded Q&A** | Transcript-conditioned answering (`audio/qa.py`) |
| **Robust engineering** | Size/type guards, transcript capping, graceful JSON fallback |
| **MLOps** | Dockerfile (with CTranslate2 runtime deps), CI, tests, minimal-toolbar config |

## Architecture

```
 audio file ─► faster-whisper (local, CPU) ─► transcript
                                                 │
                       ┌─────────────────────────┼───────────────────────┐
                       ▼                                                   ▼
             LLM: structured report                              LLM: Q&A over transcript
        (summary · key points · actions)                    ("what was agreed, by when?")
```

## Tech stack

- **Speech-to-text:** `faster-whisper` (`base`, int8, CPU) — free, local, no API
- **LLM:** Groq `llama-3.3-70b-versatile` — free tier
- **UI:** Streamlit
- **Quality:** pytest · ruff · GitHub Actions · Docker

## Quickstart

```bash
git clone https://github.com/karimulislambd/audio-intelligence.git
cd audio-intelligence

python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # then paste your free Groq key
streamlit run app.py
```

Get a **free** Groq API key at <https://console.groq.com>.

## Run the tests

```bash
pytest -q          # report parsing + transcript formatting, no API key or model needed
ruff check .
```

## Notes

- The first run downloads the Whisper model once (~150 MB for `base`), then caches it.
- On low-resource hosting, set `WHISPER_MODEL=tiny` for faster transcription.
- No system `ffmpeg` needed — `faster-whisper` decodes audio via a bundled backend.

## Roadmap

- [ ] Speaker diarization (who said what)
- [ ] Export report to Markdown / PDF
- [ ] Long-recording chunking with a rolling summary

---

Built by **Md Karimul Islam** — AI/ML Engineer · Computer Vision · LLM · XAI.
