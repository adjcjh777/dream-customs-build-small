# Dream QA / 梦境问答台 Handoff

Last updated: 2026-06-08

## Current Product Direction

The project is pivoting from a customs/pact-centered ritual into a step-by-step dream Q&A Gradio app.

The repo and Space still use the `Dream Customs` name for continuity, but future product work should use the `Dream QA / 梦境问答台` direction:

> 输入梦境，回答或跳过几个温和追问，最后得到一个和梦境细节相关的今日小 Tips。

The public hackathon experience is English-first. Keep the visible `English / 中文` toggle so Chinese remains a first-class path, but do not make judges land on a Chinese-only first screen.

## Deprecated Context

Earlier implementation and smoke docs mention:

- dream visitor
- customs negotiation
- permit ID
- contraband
- sealed pact
- bedtime release

Those are historical context, not the new target. Do not build new work around permit/contraband/sealed-pact unless the user explicitly reverses this pivot.

## Current Source Documents

Read in this order:

1. `AGENTS.md`
2. `docs/spec.md`
3. `docs/prd.md`
4. `PRODUCT.md`
5. `DESIGN.md`
6. `docs/superpowers/plans/2026-06-08-dream-qa-refactor.md`
7. `docs/superpowers/plans/2026-06-08-dream-qa-refactor-doc-plan.md`

Prototype references:

- `docs/prototypes/2026-06-08-dream-qa-mobile-flow.png`
- `docs/prototypes/2026-06-08-dream-qa-desktop-workbench.png`
- `docs/prototypes/2026-06-08-dream-qa-tips-card.png`

## Product Decision

Build a guided dream interpretation app, not a diagnosis app, not a fortune-telling app, and not a one-shot pact generator.

Final positioning:

> Dream QA helps you record a dream, answer or skip one gentle question, and leave with one grounded Today Tip.

## Model Decision

Use:

- `openbmb/MiniCPM-V-4.6` for image/sketch/note understanding.
- `openbmb/MiniCPM5-1B` for text reasoning, follow-up questions, interpretation, and final Today Tip.

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
4. App builds a `DreamQuestionIntake`.
5. MiniCPM5-1B creates a short dream summary and identifies the user's likely main question.
6. MiniCPM5-1B asks 1-3 gentle follow-up questions.
7. User answers, skips, adds detail, or asks for another angle.
8. MiniCPM5-1B drafts a grounded interpretation.
9. MiniCPM5-1B generates a final `TodayTipCard`.
10. Gradio renders a mobile-readable result card and plain text.

Language behavior:

- Default: English.
- Toggle: `中文`.
- The same intake/state/card pipeline serves both languages.
- MiniCPM prompts should instruct the selected output language instead of duplicating the product flow.

## Required Output Fields

- `dream_summary`
- `main_question`
- `dream_anchors`
- `followup_questions`
- `user_answers`
- `interpretation`
- `today_tip`
- `tiny_action`
- `caring_note`
- `safety_note`

The final `today_tip` must reference at least one concrete dream anchor. Generic wellness advice is a regression.

## Safety Boundary

The product must never present itself as therapy, medical advice, or diagnosis. It should use playful, non-certain language. Severe distress should trigger a professional-help suggestion.

## Recommended Implementation Scope

The existing package should be refactored rather than replaced from scratch:

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
  ui/
tests/
```

Likely code files to change:

- `dream_customs/schema.py`
- `dream_customs/prompts.py`
- `dream_customs/pipeline.py`
- `dream_customs/render.py`
- `dream_customs/ui/actions.py`
- `dream_customs/ui/app.py`
- `dream_customs/ui/copy.py`
- `dream_customs/ui/styles.py`
- tests covering schema, prompts, pipeline, render, UI actions, and safety

## Implementation Priorities

1. Preserve text-only demo fallback.
2. Replace pact schema with Q&A state and Today Tip output.
3. Preserve image and voice as optional evidence in the same intake.
4. Make follow-up questions a first-class user action.
5. Render one clear final tip, not a multi-field customs certificate.
6. Keep mobile readability.
7. Run tests and local Gradio smoke before any Space sync.
8. Run `python scripts/evaluate_today_tip_quality.py` before deployment.

## Repository Status

This directory is a dedicated Dream Customs/Dream QA repository:

- Local path: `/Users/junhaocheng/working-dir/ai-competitions/build-small-hackthon`
- GitHub remote: `https://github.com/adjcjh777/dream-customs-build-small.git`
- Hugging Face Space remote: `https://huggingface.co/spaces/build-small-hackathon/dream-customs`

Continue to confirm `git remote -v` before pushing.

## Modal Backend Route

The intended production-quality route remains:

```text
Hugging Face Space Gradio UI
  -> HostedMiniCPMTextClient / HostedMiniCPMVisionClient
  -> private Modal endpoints
  -> MiniCPM5-1B text generation and MiniCPM-V-4.6 visual clue extraction
```

The Space defaults to `model` for both text and vision backends, so a configured Space calls Modal immediately. The `demo` backend remains available in developer settings as the deterministic fallback path.

The public Space can run on ZeroGPU after `dream_customs.zerogpu` registers the lightweight `@spaces.GPU` startup probe. Modal credits still pay for the hidden GPU backend; the ZeroGPU probe is only there to make the HF hardware setting valid for this Gradio frontend.

## Resolved Decisions

- Public UI name: `Dream QA`, with `Dream Customs` retained as project/Space continuity.
- Language: English-first for the international hackathon, with Chinese available through an in-app toggle.
- Recommendation quality: deterministic Today Tip eval is required before deployment.

## Open Questions For User

These do not block document alignment:

- Which ASR adapter is acceptable for the hackathon submission?
- Should `refs/pr/*` cleanup be done after HF Space merges, or left for auditability?
