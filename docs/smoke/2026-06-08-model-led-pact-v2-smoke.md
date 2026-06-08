# Model-Led Pact V2 Smoke

Date: 2026-06-08
Branch: feature/dream-customs-ui-voice-settings

## Local

- Command: `.venv/bin/python -m pytest -q`
- Result: PASS, `83 passed, 2 warnings`
- Command: `git diff --check`
- Result: PASS
- Command: `.venv/bin/python scripts/evaluate_demo_quality.py`
- Result: PASS, `case_count` is `10`
- Command: `GRADIO_SERVER_PORT=7862 .venv/bin/python app.py`
- Result: PASS, local URL served at `http://0.0.0.0:7862`

## Manual Demo Case

Input:

```text
I kept missing an elevator. The buttons melted like wax, and the floor number froze at 14.
```

Acceptance:

- Natural English card: PASS
- No repeated article regression: PASS
- No invented lever detail: PASS
- Uses at least two dream details: PASS, elevator and melted buttons
- Practical suggestion is actionable: PASS
- Weird task is harmless and dream-grounded: PASS
- Local UI loads at `http://127.0.0.1:7862`: PASS

Observed final pass excerpt:

```text
Visitor: Late Elevator
Alliance reading: You can treat the elevator and the floor as last night's way of asking for one promise to become smaller and easier to carry today.
Life tip for today: Pick one real task that feels like the elevator, then define only its first step for the next 10 minutes.
5-minute odd task: Draw a tiny elevator button on paper, press it once, and work for five minutes.
Emotional contraband: unfiled pressure, melted buttons, a pocket of unstarted tasks
Bedtime release: The elevator has docked for tonight. Unfinished floors can report tomorrow.
```

## Hugging Face Space

- Push target checked: `space https://huggingface.co/spaces/build-small-hackathon/dream-customs`
- Live Space config checked:
- Live Space manual case checked:
- Notes: pending final Space sync attempt for this implementation branch.
