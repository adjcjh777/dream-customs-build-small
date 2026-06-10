# Dream QA Tip-First Card Smoke - 2026-06-10

## Scope

- Put the final Today Tip before supporting interpretation.
- Make supporting interpretation use the user's waking-life answer when it names a concrete task.
- Preserve English-only output quality and the existing Chinese toggle.

## TDD Red

Focused red commands:

```text
.venv/bin/python -m pytest tests/test_render.py tests/test_ui_actions.py tests/test_today_tip_quality_eval.py -q
.venv/bin/python scripts/evaluate_today_tip_quality.py
```

Observed failures before implementation:

```text
test_today_tip_card_prioritizes_tip_before_interpretation
test_english_interpretation_uses_user_answer_before_tip
test_today_tip_quality_eval_passes_fixture_cases
elevator_email_first_sentence: missing_interpretation_terms:overdue email
```

## Local Verification

Commands:

```text
.venv/bin/python -m pytest -q
.venv/bin/python scripts/evaluate_today_tip_quality.py
git diff --check
```

Observed:

```text
97 passed, 2 warnings
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
status=tip
title=Today Tip
tip_before_reflection=True
interpretation_has_email=True
interpretation_has_floor14=True
has_chinese_leakage=False
has_immediately=False
```

## Hugging Face Space Sync

Pending.

## Public User-View Review

Pending.
