# Dream QA Refactor Implementation Plan

Last updated: 2026-06-08

## Goal

Refactor the current Dream Customs Gradio app into Dream QA / 梦境问答台: a step-by-step dream interpretation app that records a dream, asks gentle follow-up questions, drafts a grounded interpretation, and ends with one Today Tip.

## Source Of Truth

Read before implementation:

1. `AGENTS.md`
2. `docs/handoff.md`
3. `docs/spec.md`
4. `docs/prd.md`
5. `PRODUCT.md`
6. `DESIGN.md`
7. `docs/superpowers/plans/2026-06-08-dream-qa-refactor-doc-plan.md`

Prototype references:

- `docs/prototypes/2026-06-08-dream-qa-mobile-flow.png`
- `docs/prototypes/2026-06-08-dream-qa-desktop-workbench.png`
- `docs/prototypes/2026-06-08-dream-qa-tips-card.png`

## Non-Goals

- Do not rebuild the whole repo from scratch.
- Do not change model family away from MiniCPM.
- Do not implement voice output.
- Do not build account, history, therapy plan, or diagnosis flows.
- Do not preserve permit/contraband/sealed pact as required user-facing fields.

## Task 1: Schema And State

Files:

- `dream_customs/schema.py`
- `tests/test_schema.py`

Steps:

- Add or rename models for `DreamQuestionIntake`, `DreamQAState`, and `TodayTipCard`.
- Keep compatibility wrappers only if needed to avoid breaking intermediate UI code.
- Ensure final output has `dream_summary`, `main_question`, `dream_anchors`, `interpretation`, `today_tip`, `tiny_action`, `caring_note`, and `safety_note`.
- Add tests for missing modalities, skipped answers, and required dream anchors.

Verification:

```bash
python -m pytest tests/test_schema.py -q
```

## Task 2: Prompts And Safety

Files:

- `dream_customs/prompts.py`
- `dream_customs/safety.py`
- relevant prompt/safety tests

Steps:

- Replace pact/permit prompt language with Q&A language.
- Add prompts for dream summary, main-question detection, follow-up questions, interpretation draft, and Today Tip.
- Require non-certain language: "maybe", "could treat it as", "for today, try".
- Require at least one dream anchor in final tips.
- Preserve severe distress support copy.

Verification:

```bash
python -m pytest tests/test_safety.py tests/test_pipeline.py -q
```

## Task 3: Pipeline Refactor

Files:

- `dream_customs/pipeline.py`
- `dream_customs/models.py`
- pipeline/model tests

Steps:

- Route all modalities into `DreamQuestionIntake`.
- Add actions for record, answer, skip, ask another angle, interpret, and finish.
- Keep deterministic fake clients as the default fallback path.
- Repair generic model output so final tips cite dream anchors.
- Ensure hosted Modal/Ollama route failures fall back safely.

Verification:

```bash
python -m pytest tests/test_pipeline.py tests/test_ollama_models.py -q
```

## Task 4: Rendering And UI Copy

Files:

- `dream_customs/render.py`
- `dream_customs/ui/copy.py`
- render/copy tests

Steps:

- Render Today Tip cards instead of pact cards.
- Prioritize one primary `today_tip`.
- Include optional tiny action and caring note.
- Keep safety note visible only when needed.
- Remove visible permit/contraband/seal copy from current UI copy.

Verification:

```bash
python -m pytest tests/test_render.py tests/test_ui_actions.py -q
```

## Task 5: Gradio UI

Files:

- `dream_customs/ui/app.py`
- `dream_customs/ui/actions.py`
- `dream_customs/ui/styles.py`
- `app.py` only if needed

Steps:

- Build the visible flow around Record -> Ask -> Interpret -> Tip.
- Keep text, image, voice, mood, and primary action in one composer.
- Make follow-up questions answerable and skippable.
- Keep developer/model routes collapsed by default.
- Ensure 390px mobile readability.

Verification:

```bash
python -m pytest tests/test_ui_actions.py -q
python app.py
```

Manual smoke:

- Submit a text-only dream.
- Answer or skip one follow-up.
- Reach a Today Tip card.
- Confirm the tip references dream details.
- Confirm no diagnosis, prophecy, or frightening certainty appears.

## Task 6: Docs And Deployment

Files:

- `README.md`
- `docs/handoff.md`
- `docs/smoke/<new-smoke-file>.md`

Steps:

- Update any implementation-specific docs after code lands.
- Record local pytest and Gradio smoke.
- Commit and push the feature branch.
- Sync to Hugging Face Space through the safest available path.

Verification:

```bash
python -m pytest -q
git diff --check
git remote -v
```

HF Space sync rules:

- Confirm `space` remote is `https://huggingface.co/spaces/build-small-hackathon/dream-customs`.
- Do not print or save any token.
- If direct push or API merge returns 403, create/leave a Space PR and report the exact blocker.
- Do not force overwrite public `main` without explicit user confirmation.

## Acceptance Criteria

- Text-only path works with no image/audio.
- Image upload contributes visual clues to the Q&A.
- Voice transcript, when available, contributes to the same state.
- User can answer or skip follow-up questions.
- Final output has exactly one primary today tip.
- Final output includes a concrete dream anchor.
- Ordinary output avoids diagnosis, therapy claims, prophecy, and fear.
- Severe distress triggers support guidance.
- Mobile width remains readable.
- `python -m pytest -q` passes.
- Local Gradio smoke passes before Space sync.
