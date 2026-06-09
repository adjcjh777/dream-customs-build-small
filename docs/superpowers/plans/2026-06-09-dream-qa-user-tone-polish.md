# Dream QA User Tone Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the public Dream QA flow feel less technical, keep English mode fully English, and produce warmer, more specific Today Tips after the user's answer.

**Architecture:** Keep the existing Dream QA flow and Gradio structure. Tighten prompt contracts, normalize model-returned English cards against common Chinese anchor leakage, soften render/UI safety copy, and extend deterministic tests so the product polish is guarded before Space deployment.

**Tech Stack:** Python, Pydantic, Gradio, pytest, Hugging Face Space.

---

## File Map

- Modify `dream_customs/prompts.py`: strengthen English language instructions and final Today Tip behavior.
- Modify `dream_customs/pipeline.py`: add a small English-output cleanup for common Chinese anchor leakage.
- Modify `dream_customs/models.py`: improve deterministic demo output.
- Modify `dream_customs/render.py`: make non-crisis safety copy warmer and less defensive.
- Modify `dream_customs/ui/copy.py`: remove backend jargon from the public flow and rename runtime copy to advanced user language.
- Modify `dream_customs/ui/app.py`: rename the public settings accordion from `Runtime settings` to `Advanced`.
- Modify `tests/test_ui_actions.py`: update UI copy expectations and add English-language leakage checks.
- Modify `tests/fixtures/today_tip_eval_cases.json`: add an English case that previously exposed Chinese leakage.
- Modify `scripts/evaluate_today_tip_quality.py`: fail English outputs that contain common Chinese leakage or hard-command phrasing.
- Modify `docs/spec.md`, `docs/prd.md`, `docs/handoff.md`, `README.md`: align the product contract with the user-tone polish.
- Create `docs/smoke/2026-06-09-user-tone-polish-smoke.md`: record local, HF, and browser/user-view verification.

---

### Task 1: Guard English Product Quality

**Files:**
- Modify: `tests/test_ui_actions.py`
- Modify: `tests/fixtures/today_tip_eval_cases.json`
- Modify: `scripts/evaluate_today_tip_quality.py`

- [x] **Step 1: Add UI copy expectations**

Update `test_processing_note_is_story_copy_not_backend_jargon` so it expects public copy to mention the user flow and rejects `model routes`, `fallback`, `token`, `endpoint`, and `debug`.

- [x] **Step 2: Add English leakage checks**

Add a test that runs an English elevator dream through `submit_dream_action` and `answer_to_card_action`, then asserts the card text/html do not contain `数字`, `电梯`, `按钮`, `楼层`, or `融化`.

- [x] **Step 3: Extend deterministic evaluator**

Update `scripts/evaluate_today_tip_quality.py` so English cases fail on the same Chinese leakage terms and hard-command phrases such as `address it immediately`.

- [x] **Step 4: Add eval fixture**

Add or update an English elevator/email case in `tests/fixtures/today_tip_eval_cases.json` with required anchors `elevator`, `button`, and `14`.

- [x] **Step 5: Run focused failing tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_ui_actions.py -q
.venv/bin/python scripts/evaluate_today_tip_quality.py
```

Expected before implementation: at least one failure for changed expectations.

### Task 2: Polish Prompts, Fallbacks, and Rendering

**Files:**
- Modify: `dream_customs/prompts.py`
- Modify: `dream_customs/pipeline.py`
- Modify: `dream_customs/models.py`
- Modify: `dream_customs/render.py`
- Modify: `dream_customs/ui/copy.py`
- Modify: `dream_customs/ui/app.py`

- [x] **Step 1: Tighten English prompt contract**

Update `_language_instruction` so English mode says to translate or paraphrase non-English dream anchors into natural English, except short quoted fragments that the user explicitly wrote.

- [x] **Step 2: Make Today Tip instructions more product-like**

Update `today_tip_prompt` to ask for short, warm, specific output; the `tiny_action` should be a 5-minute first step and should avoid demanding words such as "immediately".

- [x] **Step 3: Add English cleanup**

In `dream_customs/pipeline.py`, normalize common Chinese anchor leakage in English `TodayTipCard` fields after parsing. Preserve Chinese mode unchanged.

- [x] **Step 4: Improve deterministic fallback**

Update the English fake Today Tip to demonstrate the desired behavior: small first step, no hard command, one dream-detail metaphor, and no Chinese terms.

- [x] **Step 5: Soften render copy**

Change default English safety copy to a warmer boundary sentence, without weakening crisis safety behavior.

- [x] **Step 6: Remove public backend jargon**

Change English and Chinese processing/runtime help copy so public users see product language, not model-route/fallback language.

- [x] **Step 7: Rename settings surface**

Change the visible `Runtime settings` accordion to `Advanced` while keeping advanced endpoint controls collapsed.

- [x] **Step 8: Run focused tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_ui_actions.py -q
.venv/bin/python scripts/evaluate_today_tip_quality.py
```

Expected: focused tests pass.

### Task 3: Align Docs and Smoke Evidence

**Files:**
- Modify: `README.md`
- Modify: `PRODUCT.md`
- Modify: `docs/spec.md`
- Modify: `docs/prd.md`
- Modify: `docs/handoff.md`
- Add: `docs/smoke/2026-06-09-user-tone-polish-smoke.md`
- Modify: this plan file checkbox state.

- [x] **Step 1: Update product docs**

Record that English mode should stay natural English, avoid mixed Chinese UI/model terms, and produce small optional actions rather than hard commands.

- [x] **Step 2: Run full verification**

Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/evaluate_today_tip_quality.py
git diff --check
```

Expected: all commands pass.

- [x] **Step 3: Run local app config/action smoke**

Start the local app on port `7862`, check `/config`, and run one action-level English elevator/email flow plus one Chinese flow.

- [x] **Step 4: Record smoke evidence**

Write non-secret results to `docs/smoke/2026-06-09-user-tone-polish-smoke.md`.

- [x] **Step 5: Commit and push**

Commit the plan, implementation, docs, and smoke evidence. Push `feature/dream-qa-user-tone-polish` to GitHub.

### Task 4: Sync HF Space, Browser Merge, and User-View Review

**Files:**
- Modify: `docs/smoke/2026-06-09-user-tone-polish-smoke.md`

- [x] **Step 1: Create HF Space PR**

Upload the current folder to `build-small-hackathon/dream-customs` with `create_pr=True`.

- [x] **Step 2: Merge with browser**

Open the HF discussion PR in Chrome, verify it is ready to merge, and click Merge from the logged-in browser session.

- [x] **Step 3: Restart and verify Space**

If the Space is paused, restart it. Verify runtime is `RUNNING` and public `/config` returns `title=Dream QA`.

- [x] **Step 4: Experience as a user**

Use the public Space in the browser with the elevator/email dream. Check that English mode stays English, the question feels grounded, and the Today Tip is warm and actionable.

- [x] **Step 5: Record final evidence**

Append HF PR number, merge SHA, runtime, public config, and user-view notes to the smoke document. Commit and push the final evidence.

---

## Self-Review

- Spec coverage: The plan covers the exact user feedback: English leakage, technical UI copy, hard Today Tip command, defensive safety wording, docs alignment, HF browser merge, and post-merge user-view review.
- Placeholder scan: No TBD/TODO/fill-later placeholders remain.
- Type consistency: Existing `TodayTipCard`, `submit_dream_action`, and `answer_to_card_action` APIs are reused without schema changes.
