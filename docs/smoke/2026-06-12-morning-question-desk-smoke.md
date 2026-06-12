# Morning Question Desk Smoke - 2026-06-12

Goal: verify the Dream QA shell now behaves like `The Morning Question Desk` instead of a generic dream interpreter or legacy customs form.

## Static Gates

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/evaluate_today_tip_quality.py
.venv/bin/python scripts/evaluate_demo_quality.py
```

Results:

- `152 passed`
- Today Tip quality eval: `11/11`, `passes: true`
- Demo quality eval: `10/10`, `passes: true`

## Chrome Smoke

Local server:

```bash
GRADIO_SERVER_PORT=7864 .venv/bin/python app.py
```

Chrome observations on `http://127.0.0.1:7864`:

- Hero shows `Dream QA / The Morning Question Desk`.
- Main question shows `What did the dream leave you asking?`.
- Stepper is `Record -> One Question -> Today Tip`.
- Three real demo chips are visible: `elevator`, `floor 14`, `melting buttons`.
- Clicking `melting buttons` fills the dream note with the floor-14 overdue-email demo.
- Completing the demo produces a `Morning Ticket`.
- The ticket renders anchor chips: `elevator`, `melted button`, `floor 14`.
- Ticket sections include `Today Tip`, `Tiny 5-minute action`, `Supporting reflection`, and collapsed `How this was made small`.
- Visible page text did not include legacy `permit`, `contraband`, or `sealed pact`.

Known note: Chrome console still reports a Gradio warning, `Too many arguments provided for the endpoint`, after the chip click. The chip output, textarea state, and downstream ticket flow work correctly, and `/config` shows each chip event has one language input and two outputs.
