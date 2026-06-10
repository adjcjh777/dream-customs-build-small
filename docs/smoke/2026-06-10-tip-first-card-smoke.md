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

HF PR:

```text
discussion=21
title=Prioritize Dream QA Today Tip card
refs/pr/21=81829c97ea1d72efd98c54e7c92094a789881151
status=merged
space/main=65ca5f6ca1110b4eca649fa13066507d3fe842b9
runtime_stage=RUNNING_APP_STARTING
hardware=zero-a10g
public_config_title=Dream QA
public_config_version=4.44.1
public_config_mode=blocks
public_config_component_count=72
```

## Public User-View Review

Final public browser review:

```text
first_screen_title=Dream QA
question=When you think about the floor 14 and the elevator, is there one real thing today that you want to make easier to start?
question_has_chinese_leakage=False
small_suggestion_index=566
tiny_action_index=793
supporting_reflection_index=983
tip_before_reflection=True
today_tip=For today, treat the floor 14 as permission to start gently: open the overdue email and write only the first sentence.
tiny_action=Set a five-minute timer, open the email, and write only the first sentence. You do not have to send it yet.
supporting_reflection=Maybe the floor 14 is not asking you to finish the overdue email at once. It is pointing to the gentler threshold: opening it and writing one first sentence.
card_has_chinese_leakage=False
card_has_immediately=False
```

Result: public Space now prioritizes the actionable Today Tip before supporting reflection, and the supporting reflection uses the user's waking-life email answer.
