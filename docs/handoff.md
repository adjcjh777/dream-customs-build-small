# Dream Customs / 梦境海关 Handoff

Last updated: 2026-06-05

## Current State

The project has shipped a working Gradio MVP and a V4 local UI pass. The current interface centers a warm Codex-like multimodal composer: text, image upload, voice upload, mood, add-material, and send live inside one rounded input surface. Model routes, workflow shortcuts, diagnostics, and examples are collapsed by default.

Current V4 UX decisions:

- The first screen prioritizes the dream declaration composer and pact inspector.
- Image and voice use compact upload buttons to avoid large Gradio media drop zones in the main composer.
- `Draft pact` and `Seal today's pact` sit beside the live pact inspector.
- The timeline is a supporting "Story so far" section below the first-screen workflow.
- Technical model route controls are available but not first-level visual chrome.

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

## Modal Backend Route

The intended production-quality route is:

```text
Hugging Face Space Gradio UI
  -> HostedMiniCPMTextClient / HostedMiniCPMVisionClient
  -> private Modal endpoints
  -> MiniCPM5-1B text generation and MiniCPM-V-4.6 visual clue extraction
```

The Space defaults to `model` for both text and vision backends, so a configured Space calls Modal immediately. The `demo` backend remains available in developer settings as the deterministic fallback path.

The public Space can run on ZeroGPU after `dream_customs.zerogpu` registers the lightweight `@spaces.GPU` startup probe. Modal credits still pay for the hidden L4 GPU backend; the ZeroGPU probe is only there to make the HF hardware setting valid for this Gradio frontend.

## Open Questions For User

These do not block initial scaffolding:

- Should the demo language be Chinese-only or bilingual?
- Which Hugging Face Space name should be used?
- Should we reuse any previous `build-small-relics` assets, or keep Dream Customs separate?
- Which ASR adapter is acceptable for the hackathon submission?
