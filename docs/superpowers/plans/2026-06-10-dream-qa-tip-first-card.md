# Dream QA Tip-First Card Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put the final Today Tip before interpretation and make the interpretation paragraph use the user's waking-life answer.

**Architecture:** Keep the existing `TodayTipCard` schema and Dream QA flow. Change HTML order in `render_today_tip_card`, add answer-aware interpretation polish in `pipeline.py`, and guard both with focused tests and a public Space smoke.

**Tech Stack:** Python, Pydantic, Gradio, pytest, Hugging Face Space.

---

## File Map

- Modify `dream_customs/render.py`: render the primary Today Tip before interpretation, with interpretation as a quieter details block.
- Modify `dream_customs/pipeline.py`: when answers mention a concrete waking-life task such as email/message, make interpretation bridge the dream anchor to that answer.
- Modify `tests/test_render.py`: assert the rendered HTML puts the primary Today Tip before the interpretation block.
- Modify `tests/test_ui_actions.py`: assert the final card's interpretation references the user's email/message answer.
- Modify `scripts/evaluate_today_tip_quality.py` and `tests/fixtures/today_tip_eval_cases.json`: add optional answer-term quality checks for cases where the user gives a concrete answer.
- Modify `README.md`, `PRODUCT.md`, `docs/spec.md`, `docs/prd.md`, `docs/handoff.md`: record the tip-first output hierarchy and answer-aware interpretation rule.
- Add `docs/smoke/2026-06-10-tip-first-card-smoke.md`: record local, HF, and browser user-view verification.

---

### Task 1: Tests First

**Files:**
- Modify: `tests/test_render.py`
- Modify: `tests/test_ui_actions.py`
- Modify: `scripts/evaluate_today_tip_quality.py`
- Modify: `tests/fixtures/today_tip_eval_cases.json`

- [x] **Step 1: Add render order test**

Add a test that renders a `TodayTipCard` and asserts `Today's small suggestion` appears before `Maybe this dream is pointing to`.

- [x] **Step 2: Add answer-aware interpretation test**

Add a UI action test using the elevator/email flow and assert the final card text contains `overdue email` in the interpretation or copyable card text before the Tiny action.

- [x] **Step 3: Add answer term eval**

Extend the deterministic evaluator so a fixture may include `required_answer_terms`, and fail if those terms are missing from English output.

- [x] **Step 4: Run focused red tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_render.py tests/test_ui_actions.py tests/test_today_tip_quality_eval.py -q
.venv/bin/python scripts/evaluate_today_tip_quality.py
```

Expected before implementation: at least one focused failure for card order or answer-aware interpretation.

### Task 2: Implement Tip-First Output

**Files:**
- Modify: `dream_customs/render.py`
- Modify: `dream_customs/pipeline.py`

- [x] **Step 1: Reorder result card HTML**

Move the primary Today Tip article before the interpretation article. Keep Tiny action after the main suggestion.

- [x] **Step 2: Quiet the interpretation block**

Keep interpretation visible, but label it as supporting reflection/details rather than the first thing a user sees.

- [x] **Step 3: Add answer-aware interpretation polish**

When the user's answer includes email/message language, set the English interpretation to bridge the dream anchor to starting that email/message gently.

- [x] **Step 4: Run focused green tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_render.py tests/test_ui_actions.py tests/test_today_tip_quality_eval.py -q
.venv/bin/python scripts/evaluate_today_tip_quality.py
```

Expected: focused tests pass.

### Task 3: Docs, Smoke, Deploy

**Files:**
- Modify: `README.md`
- Modify: `PRODUCT.md`
- Modify: `docs/spec.md`
- Modify: `docs/prd.md`
- Modify: `docs/handoff.md`
- Add: `docs/smoke/2026-06-10-tip-first-card-smoke.md`
- Modify: this plan file checkbox state.

- [x] **Step 1: Align product docs**

Record that the final screen prioritizes Today Tip first, then optional supporting interpretation.

- [x] **Step 2: Run full local verification**

Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/evaluate_today_tip_quality.py
git diff --check
```

Expected: all commands pass.

- [x] **Step 3: Run local config/action smoke**

Start the local app, check `/config`, and run the elevator/email action flow.

- [ ] **Step 4: Commit and push**

Commit implementation, docs, plan, and smoke evidence. Push `feature/dream-qa-tip-first-card`.

- [ ] **Step 5: Merge GitHub and HF Space**

Create/merge GitHub PR. Upload to HF Space with `create_pr=True`, use Chrome to click Merge, then verify public `/config`.

- [ ] **Step 6: Public user-view review**

Use the public Space in browser with the elevator/email dream. Confirm Today Tip appears before interpretation and interpretation references the email answer.

---

## Self-Review

- Spec coverage: Covers the exact requested next optimization: Today Tip first, interpretation as support, interpretation tied to user answer, docs and deployment.
- Placeholder scan: No TBD/TODO/fill-later placeholders remain.
- Type consistency: Reuses existing `TodayTipCard`, `render_today_tip_card`, and UI action APIs without schema changes.
