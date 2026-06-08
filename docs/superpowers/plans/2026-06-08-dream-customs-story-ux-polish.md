# Dream Customs Story UX Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the public Dream Customs flow feel like one complete dream-customs ritual by grounding generated cards in the submitted dream, hiding developer controls from ordinary users, and turning hosted-model wait time into story-aware status copy.

**Architecture:** Keep Hugging Face Space as the public Gradio frontend and Modal as the hidden hosted MiniCPM route. Add deterministic local grounding helpers in `dream_customs/pipeline.py` so weak hosted output is repaired before rendering. Keep the UI thin and mobile-first by moving backend controls behind a collapsed developer accordion and adding user-facing processing copy without adding new backend dependencies.

**Tech Stack:** Python, Pydantic, Gradio Blocks, pytest, Hugging Face Space, Modal hosted endpoints.

---

## File Structure

- Modify `dream_customs/pipeline.py`: extract concrete dream details, detect generic model output, and repair pact fields with dream-specific visitor/action/release copy.
- Modify `dream_customs/prompts.py`: tighten MiniCPM text prompts so generated questions and pact cards must reuse concrete dream details.
- Modify `dream_customs/ui/app.py`: collapse developer settings by default and add story-aware loading/status text near the main action.
- Modify `dream_customs/ui/copy.py`: add public-facing processing copy.
- Modify `dream_customs/ui/styles.py`: style the processing note and make the collapsed developer panel quieter on desktop and mobile.
- Modify `tests/test_pipeline.py`: add regression tests for dream-grounded hosted output repair.
- Modify `tests/test_ui_actions.py`: add regression tests for public UI defaults and processing copy.

## Task 0: Baseline And Branch Hygiene

**Files:**
- Read: `AGENTS.md`
- Read: `PRODUCT.md`
- Read: `docs/spec.md`
- Read: `dream_customs/pipeline.py`
- Read: `dream_customs/ui/app.py`

- [x] **Step 1: Confirm repository and remotes**

Run:

```bash
pwd
git status --short --branch
git remote -v
```

Expected:

```text
/Users/junhaocheng/working-dir/ai-competitions/build-small-hackthon
## feature/dream-customs-ui-voice-settings...origin/feature/dream-customs-ui-voice-settings
origin https://github.com/adjcjh777/dream-customs-build-small.git
space https://huggingface.co/spaces/build-small-hackathon/dream-customs
```

- [x] **Step 2: Sync latest code**

Run:

```bash
git pull
```

Expected:

```text
Already up to date.
```

## Task 1: Ground Weak Pact Output In Dream Details

**Files:**
- Modify: `tests/test_pipeline.py`
- Modify: `dream_customs/pipeline.py`

- [x] **Step 1: Add failing regression test for generic hosted output**

Add a test in `tests/test_pipeline.py` that uses a weak text client returning a generic visitor, generic health tip, generic odd task, and bare time release for this input:

```text
I dreamed I was at a customs window carrying a suitcase full of wet paper. The clerk asked me to declare every unfinished promise before sunrise.
```

Expected repaired card:

- `visitor_name` contains either `Wet Paper` or `Unfinished Promise`.
- `alliance_reading` mentions at least one of `wet paper`, `customs window`, or `unfinished promise`.
- `practical_suggestion` mentions a first step or promise, not generic hydration.
- `weird_task` mentions paper, promise, suitcase, or customs.
- `bedtime_release` is not a bare time such as `7:00 PM`.

- [x] **Step 2: Run focused failing test**

Run:

```bash
.venv/bin/python -m pytest tests/test_pipeline.py::test_generate_pact_repairs_generic_hosted_output_with_dream_details -q
```

Expected: FAIL because current polishing does not repair all generic-but-valid hosted output.

- [x] **Step 3: Implement dream-detail extraction and repair**

In `dream_customs/pipeline.py`:

- Add `_extract_dream_anchors(intake)` returning up to three concrete lower-case noun phrases from dream text, voice transcript, and visual clues.
- Add `_is_generic_daily_tip(text)` for generic health/productivity suggestions that do not reference the dream.
- Add `_is_bare_time_or_generic_release(text)`.
- Extend `_polish_card_for_daily_use()` so weak visitor names, alliance readings, practical suggestions, weird tasks, and bedtime releases are repaired with the anchors.
- Keep existing safety behavior and dated permit stamping unchanged.

- [x] **Step 4: Run focused test until green**

Run:

```bash
.venv/bin/python -m pytest tests/test_pipeline.py::test_generate_pact_repairs_generic_hosted_output_with_dream_details -q
```

Expected: PASS.

## Task 2: Tighten MiniCPM Prompt Contracts

**Files:**
- Modify: `tests/test_pipeline.py`
- Modify: `dream_customs/prompts.py`

- [x] **Step 1: Add prompt contract test**

Add a test proving `pact_prompt()` includes explicit grounding constraints:

- reuse at least two concrete dream details;
- avoid generic wellness filler;
- `bedtime_release` must be a sentence, not a time;
- `visitor_name` must be an object/event from the dream, not a human name unless a person appeared.

- [x] **Step 2: Run focused failing test**

Run:

```bash
.venv/bin/python -m pytest tests/test_pipeline.py::test_pact_prompt_requires_dream_grounded_card -q
```

Expected: FAIL until prompt copy is tightened.

- [x] **Step 3: Update prompts**

In `dream_customs/prompts.py`, add concrete instructions to `negotiation_prompt()`, `followup_question_prompt()`, `pact_prompt()`, and `pact_revision_prompt()` that keep the model plain, non-clinical, and dream-specific.

- [x] **Step 4: Run prompt contract test**

Run:

```bash
.venv/bin/python -m pytest tests/test_pipeline.py::test_pact_prompt_requires_dream_grounded_card -q
```

Expected: PASS.

## Task 3: Hide Developer Settings From Ordinary Users

**Files:**
- Modify: `tests/test_ui_actions.py`
- Modify: `dream_customs/ui/app.py`
- Modify: `dream_customs/ui/styles.py`

- [x] **Step 1: Add UI source regression test**

Add a test that inspects `dream_customs.ui.app` source and asserts `Runtime settings` accordion is created with `open=False`.

- [x] **Step 2: Run focused failing test**

Run:

```bash
.venv/bin/python -m pytest tests/test_ui_actions.py::test_runtime_settings_are_collapsed_for_public_flow -q
```

Expected: FAIL while the accordion is still `open=True`.

- [x] **Step 3: Collapse and quiet the developer panel**

Change `with gr.Accordion("Runtime settings", open=True, elem_classes=["dc-dev"]):` to `open=False`, and update CSS so collapsed runtime settings look like a quiet secondary control rather than the next stage of the user flow.

- [x] **Step 4: Run focused UI test**

Run:

```bash
.venv/bin/python -m pytest tests/test_ui_actions.py::test_runtime_settings_are_collapsed_for_public_flow -q
```

Expected: PASS.

## Task 4: Add Story-Aware Processing Copy

**Files:**
- Modify: `tests/test_ui_actions.py`
- Modify: `dream_customs/ui/copy.py`
- Modify: `dream_customs/ui/app.py`
- Modify: `dream_customs/ui/styles.py`

- [x] **Step 1: Add copy regression test**

Add a test that imports `PROCESSING_NOTE` and asserts it mentions the clerk/model route without using secret/backend jargon such as `token`, `endpoint`, or `debug`.

- [x] **Step 2: Run focused failing test**

Run:

```bash
.venv/bin/python -m pytest tests/test_ui_actions.py::test_processing_note_is_story_copy_not_backend_jargon -q
```

Expected: FAIL until `PROCESSING_NOTE` exists.

- [x] **Step 3: Add and render processing note**

Add `PROCESSING_NOTE` to `dream_customs/ui/copy.py` and render it near the submit buttons in `dream_customs/ui/app.py`.

Recommended copy:

```text
When you file a dream, the clerk reads the fragment and drafts a pass. Model-backed routes may take a few seconds; text-only fallback stays ready.
```

- [x] **Step 4: Style processing note**

Add `.dc-processing-note` styles in `dream_customs/ui/styles.py` with small, readable text and no layout shift on mobile.

- [x] **Step 5: Run focused copy test**

Run:

```bash
.venv/bin/python -m pytest tests/test_ui_actions.py::test_processing_note_is_story_copy_not_backend_jargon -q
```

Expected: PASS.

## Task 5: Full Verification And Deployment

**Files:**
- Verify: all modified files

- [x] **Step 1: Run full test suite**

Run:

```bash
.venv/bin/python -m pytest -q
```

Expected: all tests pass.

- [x] **Step 2: Run whitespace check**

Run:

```bash
git diff --check
```

Expected: no output.

- [x] **Step 3: Run local Gradio smoke**

Run:

```bash
GRADIO_SERVER_PORT=7862 .venv/bin/python app.py
```

Open `http://127.0.0.1:7862`, submit the customs-window wet-paper dream, skip optional question, and verify:

- runtime settings are collapsed by default;
- the processing note is visible before submit;
- the final pass references wet paper/customs/unfinished promises;
- mobile width has no obvious overflow.

- [x] **Step 4: Commit and push GitHub branch**

Run:

```bash
git add docs/superpowers/plans/2026-06-08-dream-customs-story-ux-polish.md dream_customs/pipeline.py dream_customs/prompts.py dream_customs/ui/app.py dream_customs/ui/copy.py dream_customs/ui/styles.py tests/test_pipeline.py tests/test_ui_actions.py
git commit -m "fix: ground dream customs story flow"
git push origin feature/dream-customs-ui-voice-settings
```

- [x] **Step 5: Sync Hugging Face Space and verify live app**

Push or create a Space PR to `space/main` according to the current auth state. Then verify the live Space `/config` and public app page show the updated runtime settings behavior and pass generation flow.

Stop and report if HF auth, forced public `main` overwrite, or PR merge permissions block completion.
