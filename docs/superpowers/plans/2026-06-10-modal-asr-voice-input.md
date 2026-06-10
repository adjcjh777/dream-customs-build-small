# Modal ASR Voice Input Plan - 2026-06-10

## Goal

Replace the browser-only voice placeholder with a real Gradio audio recording/upload input that sends a filepath into the existing Dream QA intake, then connect voice transcription to a Modal-hosted ASR adapter.

## Root Cause

- The visible round microphone was custom JavaScript using browser speech recognition.
- The backend `audio_input` was only `gr.State(None)`, so no recorded file reached `HostedASRClient`.
- The Modal backend had text and vision routes but no `/asr` route.

## Guardrails

- ASR only transcribes audio; dream understanding remains MiniCPM-driven.
- Do not store or print endpoint URLs, hosted tokens, HF tokens, Modal tokens, or secret values.
- Keep text-only fallback working when audio permission, recording, upload, or hosted ASR fails.

## Tasks

- [x] Add failing tests for default Modal ASR, real Gradio audio input, and audio payload decoding.
- [x] Change default ASR backend to `modal`.
- [x] Replace the fake browser dictation input with `gr.Audio(sources=["microphone", "upload"], type="filepath")`.
- [x] Add Modal `/asr` route with a small ASR adapter.
- [x] Run full tests, eval, local UI smoke, and Modal deploy/smoke.
- [ ] Run public Space verification after HF merge.
- [ ] Commit, push, sync to Hugging Face Space, merge, and re-check Chrome.

## Progress

- Full pytest passes with 101 tests.
- Today Tip eval passes 11 cases.
- Local Gradio config confirms real audio input and Modal ASR default.
- Modal deploy created the ASR route; unauthenticated route smoke confirmed the route is reachable and protected.
- HF API cannot write Space secrets with the current token, so code derives the ASR endpoint from the existing Modal text endpoint when `DREAM_CUSTOMS_ASR_ENDPOINT` is absent.
