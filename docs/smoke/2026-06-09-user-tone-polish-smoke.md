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

Initial HF PR:

```text
discussion=18
title=Polish Dream QA user tone
refs/pr/18=64306abd58defe5ed57402a1f8ef93a92b88d00f
status=merged
space/main=79a74147ba4b179c8376823668f0f6aeb531fb36
```

Public config after PR #18:

```text
title=Dream QA
version=4.44.1
mode=blocks
component_count=72
```

## Public User-View Review

Initial public review after PR #18:

```text
first_screen_has_advanced=True
first_screen_has_runtime_settings=False
first_screen_has_model_routes=False
question=When you think about the floor 14 and the elevator, is there one real thing today that you want to make easier to start?
question_has_chinese_leakage=False
```

The final card improved the Tiny action, but the primary Today Tip still drifted toward generic elevator grounding instead of the user's overdue-email answer. Follow-up fix: answer-aware Today Tip polish now binds email/message answers to the primary suggestion as well as the Tiny action.

Follow-up local action smoke:

```text
status=tip
has_overdue_email=True
has_first_sentence=True
has_immediately=False
has_chinese_leakage=False
```

Follow-up commands:

```text
.venv/bin/python -m pytest tests/test_ui_actions.py tests/test_today_tip_quality_eval.py -q
.venv/bin/python scripts/evaluate_today_tip_quality.py
.venv/bin/python -m pytest -q
git diff --check
```

Observed:

```text
11 passed, 2 warnings
{"case_count": 11, "failures": {}, "passes": true}
95 passed, 2 warnings
git diff --check clean
```

Final HF follow-up: Pending.
