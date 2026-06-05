# Dream Customs UI/UX V2 Execution Plan

> **For agentic workers:** Use `$impeccable craft Dream Customs UI/UX V2` or combine `superpowers:executing-plans` with the references named in `docs/design/2026-06-05-uiux-v2-brief.md`. Track progress by updating these checkboxes.

**Goal:** Replace the current one-shot Gradio form with a mobile-first, Codex-style Dream Customs workbench that supports multimodal evidence, iterative negotiation, draft revision, and final pact sealing.

**Current problem:** The deployed app works, but it looks like a basic form. The main button is not placed where the user expects, the color system is flat, the output card feels like a paper certificate, and the flow ends too quickly.

**Design north star:** Night Desk: a dream customs desk with disciplined product controls, dark atmospheric surfaces, cobalt actions, aurora evidence light, and coral stamp ink.

---

## Task 1: Lock Design Context

- [x] Add `PRODUCT.md`.
- [x] Add target `DESIGN.md`.
- [x] Add `.impeccable/design.json`.
- [x] Generate and store three visual probes in `docs/design/assets/`.
- [x] Add `docs/design/2026-06-05-uiux-v2-brief.md`.

## Task 2: Refactor Product State

Files:

- `dream_customs/schema.py`
- `dream_customs/pipeline.py`
- `dream_customs/app_logic.py`
- `tests/`

Steps:

- [x] Add session state schema for phases: `empty`, `declaring`, `negotiating`, `drafting`, `sealed`, `error`.
- [x] Add `EvidenceItem` schema with `type`, `label`, `status`, `content`, `source_path`, and `error`.
- [x] Add `CustomsSession` schema that stores `DreamIntake`, evidence items, question history, answer history, draft pact, sealed pact, and safety flags.
- [x] Add tests for adding text, image, audio, mood, answer, skip, revise, and seal actions.
- [x] Keep text-only path working even if image/audio/model routes fail.

## Task 3: Build Iterative Pipeline

Files:

- `dream_customs/pipeline.py`
- `dream_customs/models.py`
- `dream_customs/prompts.py`
- `dream_customs/app_logic.py`

Steps:

- [x] Split the one-shot `run_customs_once` into actions: `add_evidence`, `ask_questions`, `answer_question`, `draft_pact`, `revise_pact`, `seal_pact`.
- [x] Make each action return structured state plus render-ready view models.
- [x] Add prompt templates for continuing negotiation and revising pact tone.
- [x] Add buttons for `Add material`, `Ask another question`, `Draft pact`, `Revise pact`, and `Seal today's pact`.
- [x] Add a deterministic demo path for all actions.

## Task 4: Add Hosted Model Path

Files:

- `dream_customs/models.py`
- `requirements.txt`
- deployment docs or secrets docs

Steps:

- [x] Keep `demo` as fallback.
- [x] Add `model` backend option that can call hosted MiniCPM text and vision endpoints.
- [x] Use Modal credits for MiniCPM experiments if local or HF Space loading is too slow.
- [x] Use HF credits for Space hardware only if needed for stable public demo.
- [x] Do not store tokens in repo, logs, docs, or examples.
- [x] Add short smoke command for hosted text generation and hosted image clue extraction.

## Task 5: Rebuild Gradio UI

Files:

- `app.py`
- possible new `dream_customs/ui.py`
- `dream_customs/render.py`

Steps:

- [x] Replace two-column form with app shell: header, timeline, pact inspector, bottom composer.
- [x] Composer contains multiline dream input, image upload, audio upload/record, mood chip, backend menu, and primary action.
- [x] Timeline renders user evidence, model questions, answers, extraction statuses, and pact drafts.
- [x] Pact inspector renders live draft and final sealed card.
- [x] Primary actions are visible above the fold on mobile.
- [x] Debug JSON moves into a collapsed diagnostics panel.

## Task 6: Apply Visual System

Files:

- `app.py`
- `dream_customs/render.py`
- optional static assets

Steps:

- [x] Implement the OKLCH tokens from `DESIGN.md`.
- [x] Use generated probe imagery as header or empty-state atmosphere.
- [x] Replace parchment card styling with dark inspector plus sealed pact treatment.
- [x] Add focus, hover, disabled, loading, and error states.
- [x] Add reduced-motion fallback.
- [x] Verify contrast for body, labels, placeholders, chips, and disabled controls.

## Task 7: Verify Locally And On Space

Commands:

```bash
python -m pytest -q
python app.py
```

Checks:

- [x] Text-only declaration can reach sealed pact.
- [x] User can add material after receiving questions.
- [x] User can ask another question before sealing.
- [x] User can revise pact before sealing.
- [x] Image and audio failure keep text path alive.
- [x] Mobile width is readable.
- [ ] V2 Space deployment builds and remote queue prediction works.

2026-06-05 verification notes:

- [x] Local tests passed with `.venv/bin/python -m pytest -q`: 31 passed.
- [x] Local V2 Gradio smoke passed on `127.0.0.1:7861` because `7860` was already occupied by another Python listener.
- [x] Local V2 browser flow reached sealed pact: `Send to customs -> Ask another question -> Add material -> Draft pact -> Revise pact -> Seal today's pact`.
- [x] Local mobile viewport `390x844` remained readable; pact inspector showed `DC-DEMO-014`, `Sealed`, 3 evidence items, 4 questions, suggestion, weird task, contraband, and bedtime release.
- [x] Local diagnostics panel opened and showed `status: sealed`, `text_backend: demo`, `vision_backend: demo`, empty `safety_flags`, and empty ordinary-case `safety_note`; the header safety copy stayed visible as playful reflection, not medical advice.
- [x] Existing public Space opened and the currently deployed old one-shot app completed a text-only demo queue prediction through `run_customs_once`.
- [ ] Current V2 workbench was not deployed to public Space because `git push` to `https://huggingface.co/spaces/build-small-hackathon/dream-customs` was rejected by HF authorization (`You are not authorized to push to this repo`).
- [ ] Hosted MiniCPM route smoke was not run because `DREAM_CUSTOMS_TEXT_ENDPOINT`, `DREAM_CUSTOMS_VISION_ENDPOINT`, and `DREAM_CUSTOMS_HOSTED_TOKEN` were missing from the runtime environment.

Detailed record: `docs/smoke/2026-06-05-space-deployment-smoke.md`.

## Task 8: Commit And Deploy

- [x] Commit implementation to `feature/dream-customs-mvp` or a new `feature/uiux-v2` branch.
- [x] Push GitHub branch.
- [ ] Upload/merge Space update. Blocked on HF push permission as of 2026-06-05.
- [ ] Re-run public Space V2 smoke test after the Space update is accepted.
- [x] Re-run existing public Space smoke test for the currently deployed old one-shot app.
- [x] Update README screenshots or demo instructions.
