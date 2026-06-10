# Modal ASR Voice Input Smoke - 2026-06-10

## Scope

Verify that Dream QA voice input uses a real Gradio audio component and that the backend can route recorded/uploaded audio to Modal ASR.

No endpoint URLs, bearer tokens, Hugging Face tokens, Modal tokens, or secret values should be printed or recorded.

## Evidence

- Focused regression: `.venv/bin/python -m pytest tests/test_app_logic.py::test_defaults_use_modal_model_entrypoint tests/test_ui_actions.py::test_voice_input_uses_gradio_audio_file_for_modal_asr tests/test_modal_contract.py::test_decode_audio_payload_accepts_audio_key -q` -> 3 passed.
- Full pytest: `.venv/bin/python -m pytest -q` -> 101 passed, 2 warnings.
- Today Tip eval: `.venv/bin/python scripts/evaluate_today_tip_quality.py` -> 11 cases passed.
- Whitespace check: `git diff --check` -> passed.
- Local Gradio config: `Voice note` is a real `audio` component with `sources=["microphone", "upload"]`, `format="wav"`; `Voice input` default value is `modal`.
- Modal deploy: `dream-customs-minicpm-backend` redeployed with a new `asr` web function. CLI output URLs were redacted.
- Modal ASR auth smoke: route reachable without printing URL; unauthenticated request returned `status="unauthorized"`, confirming the route exists and requires the hosted token.
- HF Space secret update attempt: API returned 403 for writing `DREAM_CUSTOMS_ASR_ENDPOINT`. The app now derives the ASR endpoint from the existing Modal text endpoint when the explicit ASR endpoint secret is missing, so no endpoint value was printed or stored.
- Public Space check: pending.
