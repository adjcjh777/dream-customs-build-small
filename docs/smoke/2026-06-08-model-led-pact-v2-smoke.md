# Model-Led Pact V2 Smoke

Date: 2026-06-08
Branch: feature/dream-customs-ui-voice-settings

## Local

- Command: `.venv/bin/python -m pytest -q`
- Result: PASS, `86 passed, 2 warnings`
- Command: `git diff --check`
- Result: PASS
- Command: `.venv/bin/python scripts/evaluate_demo_quality.py`
- Result: PASS, `case_count` is `10`, `passes` is `true`, `failures` is empty
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
- Space sync command: `git push space feature/dream-customs-ui-voice-settings`
- Space sync result: BLOCKED
- Blocker:

```text
You are not authorized to push to this repo.
Make sure that you are properly logged in.
```

- Live Space config checked: not re-checked for this implementation SHA because Space sync is blocked by push authorization.
- Live Space manual case checked: not re-checked for this implementation SHA because the implementation branch is not deployed to the Space.
- Notes: GitHub branch `feature/dream-customs-ui-voice-settings` is pushed through commit `19e6e5c`. Do not force-push public Space `main` or handle tokens in chat; Space sync needs an authenticated HF credential or manual PR/merge by someone with access.
