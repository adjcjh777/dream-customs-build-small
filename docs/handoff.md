# Dream Customs / 梦境海关 Handoff

Last updated: 2026-06-05

## Current State

The project is in concept/spec stage. A visual HTML concept note already exists at:

- `docs/dream-customs-concept/index.html`

Supporting images:

- `docs/dream-customs-concept/assets/dream-passport.svg`
- `docs/dream-customs-concept/assets/multimodal-intake.svg`
- `docs/dream-customs-concept/assets/alliance-card.svg`

This handoff adds project context documents for implementation:

- `docs/spec.md`
- `docs/prd.md`
- `docs/handoff.md`
- `docs/superpowers/plans/2026-06-05-dream-customs-mvp.md`
- `AGENTS.md`

## Product Decision

Build Dream Customs as a "dream alliance" app, not a dream diagnosis app.

Final positioning:

> 梦境海关帮你和昨晚的梦结盟：把不安转成明天的小建议，把怪梦转成一件有趣的小事。

## Model Decision

Use:

- `openbmb/MiniCPM-V-4.6` for image/sketch/note understanding.
- `openbmb/MiniCPM5-1B` for text reasoning, negotiation, and final output.

Do not broaden to arbitrary small models unless MiniCPM paths fail.

Voice input is allowed, but current MiniCPM pair does not directly transcribe raw audio. Use a small ASR adapter only for transcription. Keep dream understanding and final generation inside MiniCPM.

## Contest Constraints

- Build Small Hackathon.
- Build window: 2026-06-05 to 2026-06-15.
- App should ship as Gradio on Hugging Face Space.
- Total model parameters must be <= 32B.
- Strongest track: An Adventure in Thousand Token Wood.
- Secondary narrative: Backyard AI due to real sleep/dream use case.

## MVP User Flow

1. User submits dream using text, image, voice, or a combination.
2. Audio is transcribed by a small adapter.
3. Image is converted into visual clues by MiniCPM-V-4.6.
4. App builds a `DreamIntake` object.
5. MiniCPM5-1B generates dream visitor and 2-3 negotiation questions.
6. User answers or skips.
7. MiniCPM5-1B generates final "Today's Pact" card.
8. Gradio renders a screenshot-friendly HTML card.

## Required Output Fields

- `visitor_name`
- `permit_id`
- `contraband`
- `risk_level`
- `alliance_reading`
- `practical_suggestion`
- `weird_task`
- `bedtime_release`
- `safety_note`

## Safety Boundary

The product must never present itself as therapy, medical advice, or diagnosis. It should use playful, non-certain language. Severe distress should trigger a professional-help suggestion.

## Recommended First Implementation

Create a minimal Python package:

```text
app.py
requirements.txt
README.md
dream_customs/
  __init__.py
  schema.py
  prompts.py
  safety.py
  render.py
  pipeline.py
  models.py
tests/
  test_schema.py
  test_safety.py
  test_render.py
  test_pipeline.py
```

Start with mocked model clients and deterministic examples. Add real model loading only after schema, safety, rendering, and pipeline tests pass.

## Implementation Priorities

1. Text-only flow.
2. Card rendering.
3. Safety layer.
4. Image clue extraction.
5. Voice transcription adapter.
6. Demo examples.
7. Space packaging.

## Known Repository Issue

The current directory is under git root `/Users/junhaocheng`, whose remote is `adjcjh777/vlarepo.git`. This is likely not the intended Build Small repository. Also, `.git/info/exclude` currently ignores paths beneath this workspace root.

Do not push these files to the VLA remote by accident. Before implementation, either:

1. initialize a dedicated repo in `/Users/junhaocheng/working-dir/ai-competitions/build-small-hackthon`, or
2. move this context into the intended Build Small repository/Space repo.

## Open Questions For User

These do not block initial scaffolding:

- Should the demo language be Chinese-only or bilingual?
- Which Hugging Face Space name should be used?
- Should we reuse any previous `build-small-relics` assets, or keep Dream Customs separate?
- Which ASR adapter is acceptable for the hackathon submission?
