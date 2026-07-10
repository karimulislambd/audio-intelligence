"""Streamlit UI for Audio Intelligence.

Upload a meeting/lecture/interview recording -> transcript + structured report +
Q&A over what was said. Run:  streamlit run app.py
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

import config
from audio.analyze import analyze
from audio.qa import answer
from audio.transcribe import transcribe

st.set_page_config(
    page_title="Audio Intelligence",
    page_icon=":material/graphic_eq:",
    layout="wide",
)

# ---- session state ----
for key, default in {"transcript": None, "report": None, "chat": [], "audio_key": None}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def _save_temp(data: bytes, suffix: str) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(data)
    tmp.close()
    return tmp.name


def _sidebar():
    with st.sidebar:
        st.subheader(":material/mic: Your recording")
        uploaded = st.file_uploader("Upload audio", type=list(config.ALLOWED_AUDIO))
        if not uploaded:
            st.caption(f"{', '.join(config.ALLOWED_AUDIO)} · up to {config.MAX_AUDIO_MB} MB")
            return None

        data = uploaded.getvalue()
        size_mb = len(data) / (1024 * 1024)
        if size_mb > config.MAX_AUDIO_MB:
            st.error(f"Audio is {size_mb:.1f} MB — please use one under {config.MAX_AUDIO_MB} MB.")
            return None

        # New file -> reset state.
        if uploaded.name != st.session_state.audio_key:
            st.session_state.update(transcript=None, report=None, chat=[], audio_key=uploaded.name)

        st.audio(data)
        st.divider()
        if not config.GROQ_API_KEY:
            st.error("GROQ_API_KEY missing — set it in your .env file.")
        else:
            st.caption(f"STT: `whisper-{config.WHISPER_MODEL}` · LLM: `{config.LLM_MODEL}`")
        return data, uploaded.name


def _render_report(r):
    st.markdown(f"**Summary** — {r.summary}")
    cols = st.columns(2)
    with cols[0]:
        if r.key_points:
            st.markdown("**Key points**")
            for k in r.key_points:
                st.write(f"- {k}")
    with cols[1]:
        if r.action_items:
            st.markdown("**Action items**")
            for a in r.action_items:
                st.write(f"- {a}")
    if r.topics:
        st.markdown("**Topics:** " + " · ".join(r.topics))


def main():
    st.title("Audio Intelligence")
    st.caption(
        "Upload a meeting, lecture, or interview recording. Get a **transcript**, a "
        "**structured report** (summary, key points, action items), and **ask questions** about it."
    )

    loaded = _sidebar()
    if loaded is None:
        st.info("Upload an audio file from the sidebar to begin.")
        return
    if not config.GROQ_API_KEY:
        st.error("Set GROQ_API_KEY in .env to run the analysis.")
        return

    data, name = loaded
    suffix = Path(name).suffix or ".mp3"

    # --- Transcribe + analyze (once per file) ---
    if st.session_state.transcript is None:
        if st.button("Transcribe & analyze", type="primary"):
            path = _save_temp(data, suffix)
            with st.spinner("Transcribing audio (local Whisper)…"):
                st.session_state.transcript = transcribe(path)
            with st.spinner("Generating structured report…"):
                st.session_state.report = analyze(st.session_state.transcript.text)
            st.rerun()
        return

    t = st.session_state.transcript
    st.success(f"Transcribed {t.duration:.0f}s of {t.language or 'audio'}.")

    if st.session_state.report:
        _render_report(st.session_state.report)
    st.divider()

    with st.expander("Full transcript (timestamped)"):
        st.text(t.timestamped() or t.text)

    # --- Q&A over the transcript ---
    st.markdown("#### Ask about the recording")
    for turn in st.session_state.chat:
        with st.chat_message(turn["role"]):
            st.markdown(turn["text"])

    question = st.chat_input("Ask a question about what was said…")
    if not question:
        return
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            reply = answer(t.text, question, st.session_state.chat)
        st.markdown(reply)
    st.session_state.chat.append({"role": "user", "text": question})
    st.session_state.chat.append({"role": "assistant", "text": reply})


if __name__ == "__main__":
    main()
