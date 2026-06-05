# Dream Customs / 梦境海关 Handoff

Last updated: 2026-06-05

## Current State

The project has shipped a working Gradio MVP and a deployed V2 workbench on Hugging Face Space. The V2 backend/state loop works, but the public UI still needs a V3 rescue pass because the first screen does not match normal user habits.

Known V2 UX problems:

- The declaration composer appears below the timeline and pact inspector.
- The primary submit action is buried below many controls.
- The `Declare / Inspect / Draft / Seal` rail looks interactive but is static HTML.
- Empty timeline/inspector min-heights create long blank scroll space.
- Gradio default control styling leaks into the dark visual system.

The original visual HTML concept note remains useful background:

- `docs/dream-customs-concept/index.html`

Supporting images:

- `docs/dream-customs-concept/assets/dream-passport.svg`
- `docs/dream-customs-concept/assets/multimodal-intake.svg`
- `docs/dream-customs-concept/assets/alliance-card.svg`

Project context documents:

- `docs/spec.md`
- `docs/prd.md`
- `docs/handoff.md`
- `docs/superpowers/plans/2026-06-05-dream-customs-mvp.md`
- `docs/superpowers/plans/2026-06-05-dream-customs-uiux-v2.md`
- `docs/superpowers/plans/2026-06-05-dream-customs-uiux-v3.md`
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

The minimal Python package already exists:

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

The current implementation keeps deterministic demo clients as the default and exposes optional model routes. For V3, do not rebuild the pipeline from scratch. Fix the app shell, control hierarchy, phase actions, and visual polish while preserving the existing `CustomsSession` state flow.

## Implementation Priorities

1. First-screen trust and immediate declaration controls.
2. Clickable phase actions.
3. Mobile-readable composer and inspector.
4. Removal of long blank page regions.
5. Tests and local browser verification.
6. Branch commit/push and Space update when credentials allow.

## Repository Status

This directory is now a dedicated Dream Customs repository:

- Local path: `/Users/junhaocheng/working-dir/ai-competitions/build-small-hackthon`
- GitHub remote: `https://github.com/adjcjh777/dream-customs-build-small.git`
- Hugging Face Space remote: `https://huggingface.co/spaces/build-small-hackathon/dream-customs`

Continue to confirm `git remote -v` before pushing, but the earlier VLA remote warning is no longer the active state.

## Open Questions For User

These do not block initial scaffolding:

- Should the demo language be Chinese-only or bilingual?
- Which Hugging Face Space name should be used?
- Should we reuse any previous `build-small-relics` assets, or keep Dream Customs separate?
- Which ASR adapter is acceptable for the hackathon submission?
