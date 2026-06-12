# Morning Question Desk Anchor Chips Smoke - 2026-06-13

Goal: verify the Dream QA 90-second judge path shows visible dream anchors before the single follow-up question, then still produces a grounded Morning Ticket.

## Static and automated gates

- Pull check: `git pull --ff-only` -> `Already up to date.`
- Pytest: `.venv/bin/python -m pytest -q` -> `154 passed, 6 warnings`
- Today Tip quality eval: `.venv/bin/python scripts/evaluate_today_tip_quality.py` -> `11/11`, `passes: true`
- Demo quality eval: `.venv/bin/python scripts/evaluate_demo_quality.py` -> `10/10`, `passes: true`

## Local runtime

- Command: `GRADIO_SERVER_PORT=7864 .venv/bin/python app.py`
- URL: `http://127.0.0.1:7864`
- Default runtime config still reports Modal text / vision / ASR endpoints configured.

## Chrome path

1. Opened the local app in Chrome.
2. Verified hero copy:
   - `Dream QA / The Morning Question Desk`
   - `What did the dream leave you asking?`
   - `Record -> One Question -> Today Tip`
3. Clicked demo chip `melting buttons`.
4. Verified the dream note contains `floor 14` and `overdue email`.
5. Clicked `Ask one question`.
6. Verified One Question stage shows visible anchor chips before the desk question:
   - `elevator`
   - `floor 14`
   - `melted button`
7. Answered: `It reminds me of an overdue email. I only need the first sentence.`
8. Verified the final result:
   - Shows `Morning Ticket`
   - Shows `Today Tip`
   - Shows `Because your dream kept returning to`
   - Shows `Tiny 5-minute action`
   - Shows collapsed `How this was made small`
   - Mentions `overdue email`
   - Mentions `first sentence`
   - Ticket anchors render as `elevator`, `melted button`, `floor 14`
   - Visible page text does not include legacy `permit`, `contraband`, or `sealed pact`

## Product note

The earlier One Question stage had enough textual grounding, but the anchor strip was not visible because the ask-state view did not pass `qa_state.dream_anchors` forward. The ask-state view now carries those anchors, and the English anchor extractor avoids the malformed `for floor` chip on the elevator demo.
