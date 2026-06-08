# Dream QA Refactor Document Plan

Last updated: 2026-06-08

## Goal

Refactor Dream Customs from a customs/pact-centered ritual into a step-by-step dream Q&A Gradio app.

The new product should help the user gradually answer doubts about a dream, then end with one gentle "today tip". The tip can be a practical suggestion, a tiny thing the user has not tried before, or a short caring sentence. It must stay non-clinical and avoid claiming a single fixed dream meaning.

## Prototype Images

Use these generated mockups as discussion references before implementation:

- `docs/prototypes/2026-06-08-dream-qa-mobile-flow.png`
- `docs/prototypes/2026-06-08-dream-qa-desktop-workbench.png`
- `docs/prototypes/2026-06-08-dream-qa-tips-card.png`

## Product Shift

Current docs emphasize:

- Dream visitor.
- Customs negotiation.
- Permit ID.
- Contraband.
- Today's pact card.
- Seal/revise pact actions.

New direction should emphasize:

- Dream question intake.
- One clear uncertainty the user wants to understand.
- 2-4 progressive follow-up questions.
- A grounded interpretation draft that references specific dream details.
- One final "today tip" with optional tiny action.
- Safety note only when needed.

Keep the good parts:

- Text-only path must always work.
- Image and voice can enrich the same intake object.
- MiniCPM-V-4.6 remains the image clue extractor.
- MiniCPM5-1B remains the main reasoning and generation model.
- No diagnosis, prophecy, therapy framing, or fear-based copy.

## Document Modification Plan

### 1. `AGENTS.md`

Rewrite the project positioning and product boundary sections.

Change from:

- "和昨晚的梦结盟"
- "获得今日盟约卡"
- required output fields such as `permit_id`, `contraband`, `risk_level`, `bedtime_release`

Change to:

- "循序渐进帮用户理解梦境疑惑"
- final output is `today_tip` / `今日小 Tips`
- required output fields:
  - `dream_summary`
  - `main_question`
  - `followup_questions`
  - `user_answers`
  - `interpretation`
  - `today_tip`
  - `tiny_action`
  - `caring_note`
  - `safety_note`

Also update manual acceptance:

- Submit a dream.
- App asks at least one useful follow-up question.
- User can answer or skip.
- Final result references concrete dream details and gives one today tip.
- Output avoids diagnosis, prophecy, and medicalized advice.

### 2. `docs/spec.md`

Rewrite the product spec around a `DreamQuestionIntake -> DreamQAState -> TodayTipCard` flow.

Needed edits:

- Replace pact/card schema with Q&A schema.
- Replace "MVP User Flow" with progressive steps:
  1. User records dream.
  2. User picks or writes the doubt they want answered.
  3. Model asks a gentle follow-up.
  4. User answers, skips, or asks for a different angle.
  5. Model drafts an interpretation grounded in dream details.
  6. Model produces one today tip.
- Keep MiniCPM and multimodal constraints.
- Add a rule that final advice must cite at least one dream anchor.

### 3. `docs/prd.md`

Update user stories and success criteria.

New user stories:

- Text dream Q&A.
- Image-assisted dream clue extraction.
- Voice dream capture.
- Follow-up question flow.
- Final Today Tip card.

New success criteria:

- User can complete a text-only Q&A in <= 90 seconds.
- At least one follow-up question feels related to the dream.
- Final tip references concrete dream details.
- Ordinary cases never include diagnostic or frightening language.
- Distress cases show support guidance.

### 4. `PRODUCT.md`

Rewrite product purpose and anti-references.

Keep:

- Gentle, strange, lucid.
- Mobile-first morning use.
- Not therapy.

Change:

- Reduce customs clerk metaphor.
- Use "dream companion / question guide" framing.
- Keep playful language, but make the experience easier for ordinary users to understand.
- Anti-reference should include generic healing app output, not only plain Gradio/tarot/therapy.

### 5. `DESIGN.md`

Update the north star from "Morning Customs Desk" to a softer Q&A interface.

Needed design changes:

- Primary screen is a conversational Q&A flow with a visible stepper: record, ask, interpret, tip.
- Right-side desktop panel becomes "interpretation draft / today tip preview", not "pact inspector".
- Mobile final screen should prioritize Today Tip first, then optional explanation.
- Keep high contrast, 8-12px radii, readable controls, and no purple AI SaaS theme.

### 6. `docs/handoff.md`

Rewrite handoff as the source of truth for the refactor.

Needed edits:

- Mark current V4 customs flow as deprecated context.
- List the new Q&A flow and schema.
- Identify files likely to change:
  - `dream_customs/schema.py`
  - `dream_customs/prompts.py`
  - `dream_customs/pipeline.py`
  - `dream_customs/render.py`
  - `dream_customs/ui/app.py`
  - `dream_customs/ui/copy.py`
  - `dream_customs/ui/styles.py`
  - tests covering schema, prompts, pipeline, UI actions, and safety
- Preserve Modal/HF deployment constraints.

### 7. `README.md`

Update public-facing positioning after implementation is ready.

Needed edits:

- Short description should shift from "pact" to "guided dream Q&A".
- Usage section should show:
  - enter dream
  - answer follow-up
  - receive today tip
- Keep model and deployment details accurate.

### 8. Existing execution plans

Do not rewrite old completed plan files as if they never happened.

Add a new implementation plan instead:

- `docs/superpowers/plans/2026-06-08-dream-qa-refactor.md`

That plan should include code steps, tests, local Gradio verification, GitHub push, and HF Space sync/merge path.

## Implementation Acceptance Targets

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

