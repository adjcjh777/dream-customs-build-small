# Modal Default Entrypoint Smoke - 2026-06-10

## Scope

Verify that Dream QA now enters the Modal-hosted MiniCPM route by default for text and vision while preserving deterministic fallback behavior when hosted endpoint secrets are not available in the local shell.

No endpoint URLs, bearer tokens, Hugging Face tokens, Modal tokens, or secret values were printed or recorded.

## Local Default Action Smoke

Command:

```bash
.venv/bin/python - <<'PY'
import json
from dream_customs.ui.actions import submit_dream_action, skip_to_card_action

state, view_json = submit_dream_action(
    dream_text='I dreamed of a late elevator with melted buttons.',
    mood='Uneasy',
)
view = json.loads(view_json)
print({
    'submit_status': view['status'],
    'submit_phase': view['phase'],
    'text_backend': view['debug']['text_backend'],
    'vision_backend': view['debug']['vision_backend'],
    'question_present': bool(view['question']),
})

state, view_json = skip_to_card_action(state)
view = json.loads(view_json)
print({
    'card_status': view['status'],
    'card_phase': view['phase'],
    'card_title': view['card_title'],
    'tip_mentions_elevator': 'elevator' in view['card_text'].lower(),
})
PY
```

Observed:

```text
{'submit_status': 'ask', 'submit_phase': 'ask', 'text_backend': 'modal', 'vision_backend': 'modal', 'question_present': True}
{'card_status': 'tip', 'card_phase': 'tip', 'card_title': 'Today Tip', 'tip_mentions_elevator': True}
```

Result: pass. The default backend values are `modal` and the local no-secret path still falls back to a usable dream Q&A flow.

## Test Evidence

- Focused regression: `.venv/bin/python -m pytest tests/test_ui_actions.py::test_mobile_defaults_to_modal_backends tests/test_app_logic.py::test_defaults_use_modal_model_entrypoint -q`
- Full suite: `.venv/bin/python -m pytest -q` -> 98 passed, 2 warnings.
- Today Tip eval: `.venv/bin/python scripts/evaluate_today_tip_quality.py` -> 11 cases passed.
- Whitespace check: `git diff --check` -> passed.
- Local Gradio config: `Text generation` default value is `modal`; `Image understanding` default value is `modal`.
- Public Space check: pending.
