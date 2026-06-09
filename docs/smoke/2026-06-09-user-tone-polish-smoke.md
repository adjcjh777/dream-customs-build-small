# Dream QA User Tone Polish Smoke - 2026-06-09

## Scope

- Remove English-mode Chinese anchor leakage observed in the public Space user walk-through.
- Make Today Tip actions warmer, smaller, and less command-like.
- Remove backend jargon from the public user flow.
- Keep Chinese mode available through the language toggle.

## Local Verification

Commands:

```text
.venv/bin/python -m pytest -q
.venv/bin/python scripts/evaluate_today_tip_quality.py
git diff --check
```

Observed:

```text
95 passed, 2 warnings
{"case_count": 11, "failures": {}, "passes": true}
git diff --check clean
```

## Local Gradio Config

Observed from `http://127.0.0.1:7860/config`:

```text
title=Dream QA
version=4.44.1
mode=blocks
component_count=72
```

## Local Action Smoke

English dream:

```text
I dreamed I was in an elevator where the floor buttons melted like wax. The number 14 kept blinking, and I felt late but strangely calm.
```

English answer:

```text
I want to make starting my overdue email easier without feeling trapped by it.
```

Observed:

```text
en_after_submit=ask
question=When you think about the elevator and the melted button, what real thing today feels hard to start?
en_after_answer=tip
title=Today Tip
has_chinese_leakage=False
has_first_sentence=True
has_immediately=False
```

Chinese smoke:

```text
zh_after_skip=tip
title=今日小 Tips
has_zh_title=True
```

## Hugging Face Space Sync

Pending.

## Public User-View Review

Pending.
