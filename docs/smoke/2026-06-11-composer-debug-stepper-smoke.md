# Dream QA Composer / Debug / Stepper Smoke - 2026-06-11

Goal: verify the Dream QA UI pass that moves image and voice entry into the main composer, makes the progress stepper state-driven, and adds a collapsed debug panel at the bottom of the page.

## Local Runtime

- Command: `GRADIO_SERVER_NAME=127.0.0.1 GRADIO_SERVER_PORT=7862 .venv/bin/python app.py`
- URL: `http://127.0.0.1:7862`

## Automated Checks

- `.venv/bin/python -m pytest tests/test_ui_actions.py -q` -> 13 passed.
- `.venv/bin/python -m pytest tests/test_app_logic.py::test_debug_settings_do_not_expose_hosted_secrets -q` -> 1 passed.
- `.venv/bin/python -m pytest -q` -> 103 passed.
- `.venv/bin/python scripts/evaluate_today_tip_quality.py` -> `{"case_count": 11, "failures": {}, "passes": true}`.
- `git diff --check` -> pass.

## Chrome Smoke

- First screen shows one inline microphone button inside the Dream note composer.
- The previous visible `Voice note` Gradio module is hidden from the ordinary path.
- The image entry is a collapsed `＋` drawer inside the composer.
- The bottom of the page shows a collapsed `Debug` panel.
- After submitting a text dream, the stepper changes from `1 Record` active to `2 Question` active with `1 Record` complete.
- After skipping the follow-up question, the stepper marks `1 Record`, `2 Question`, and `3 Interpret` complete, with `4 Today Tip` active.
- Expanding `Debug` shows runtime JSON with backend state and configured flags, without exposing endpoint or token values.
