# Post-Refactor Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the highest-value Dream QA follow-up after the refactor: align GitHub/HF state, verify the deployed flow, make English the default hackathon experience with a Chinese toggle, and improve recommendation/follow-up quality.

**Architecture:** Keep the current Dream QA state machine. Add a lightweight language layer around UI copy, prompt language, card rendering, and fake/model fallbacks rather than cloning the app into separate English and Chinese flows. Add quality gates as deterministic tests and a small evaluator script so product quality does not regress after deployment.

**Tech Stack:** Python 3.9, Gradio 4.44.1, Pydantic, MiniCPM5-1B text route, MiniCPM-V-4.6 vision witness route, Hugging Face Space, GitHub PR workflow.

---

## Current Evidence

- Current branch: `feature/dream-customs-ui-voice-settings`.
- Current latest commit: `122266f feat: refactor dream qa flow`.
- GitHub `main` previously merged only through `ff796db`; this branch has post-merge commits that still need a GitHub PR/merge.
- HF Space PR #16 has already merged this branch to Space `main` at `19c54925bbb525405bc2540391a434ddaeba4139`.
- Public `/config` returns title `梦境问答台`, Gradio `4.44.1`, and 70 components.
- Local checks before this plan: `91 passed, 2 warnings`; `git diff --check` clean.

## Task 1: GitHub Main Alignment

**Files:**
- No source edits required.
- Record result in `docs/smoke/2026-06-08-post-refactor-polish-smoke.md`.

- [x] **Step 1: Verify branch relationship**

Run:

```bash
git fetch origin
git log --oneline origin/main..HEAD
```

Expected: shows the post-merge Dream QA commits that are on `feature/dream-customs-ui-voice-settings` but not `origin/main`.

- [x] **Step 2: Create or update GitHub PR**

Run:

```bash
gh pr list --head feature/dream-customs-ui-voice-settings --base main --json number,url,state,title
```

If no open PR exists, create one:

```bash
gh pr create \
  --base main \
  --head feature/dream-customs-ui-voice-settings \
  --title "Dream QA post-refactor polish" \
  --body-file /tmp/dream-qa-post-refactor-pr.md
```

- [x] **Step 3: Merge GitHub PR**

Use the authenticated browser/CLI path available in the session. Verify with:

```bash
gh pr view <number> --json state,mergedAt,mergeCommit,url
```

Expected: `state` is `MERGED`.

## Task 2: Deployed Space Smoke

**Files:**
- Create or update: `docs/smoke/2026-06-08-post-refactor-polish-smoke.md`
- Test: no new unit test required for this task.

- [x] **Step 1: Verify deployed config**

Run:

```bash
.venv/bin/python - <<'PY'
import json
from urllib.request import urlopen
with urlopen("https://build-small-hackathon-dream-customs.hf.space/config", timeout=30) as response:
    cfg = json.load(response)
print({"title": cfg.get("title"), "version": cfg.get("version"), "mode": cfg.get("mode"), "component_count": len(cfg.get("components", []))})
PY
```

Expected: public app config responds with Dream QA metadata.

- [ ] **Step 2: Run a browser smoke on the public app**

Use Chrome or in-app browser to open:

```text
https://build-small-hackathon-dream-customs.hf.space/?v=<space-main-sha>
```

Submit an English dream, answer or skip one follow-up, and verify the result:

```text
I dreamed I was in an old apartment building. The elevator button melted like wax, and the floor number stayed on 14. I woke up anxious.
```

Expected: the app reaches a Today Tip card, references elevator/button/floor 14, and does not show old permit/contraband/seal language.

## Task 3: English-First Bilingual Experience

**Files:**
- Modify: `dream_customs/ui/copy.py`
- Modify: `dream_customs/ui/app.py`
- Modify: `dream_customs/ui/actions.py`
- Modify: `dream_customs/render.py`
- Modify: `dream_customs/prompts.py`
- Modify: `dream_customs/pipeline.py`
- Modify: `dream_customs/models.py`
- Test: `tests/test_dream_qa_refactor.py`
- Test: `tests/test_ui_actions.py`
- Test: `tests/test_render.py`

- [x] **Step 1: Add language copy contract**

Add a `LANGUAGE_OPTIONS`, `DEFAULT_LANGUAGE = "en"`, and copy helpers in `dream_customs/ui/copy.py`. English copy must be the default; Chinese copy must remain available through a visible control.

- [x] **Step 2: Thread language through actions**

Add `language` to `initial_mobile_state`, `submit_dream_action`, `answer_to_card_action`, `skip_to_card_action`, `revise_card_action`, `reset_mobile_action`, `_view_payload`, and `_seal_view`.

- [x] **Step 3: Localize prompts and fallbacks**

Pass `language` into `dream_qa_state_prompt`, `today_tip_prompt`, `generate_today_tip`, and fallback Today Tip helpers. English output must avoid Chinese labels by default; Chinese mode must keep the current gentle Chinese tone.

- [x] **Step 4: Add visible UI language toggle**

Add a top-level `gr.Radio` or segmented-style control with English selected by default and Chinese as the second option. The visible first screen should read as English for hackathon judges, while the Chinese option remains one click away.

- [x] **Step 5: Add tests**

Add tests proving:

```python
assert DEFAULT_LANGUAGE == "en"
assert "Dream QA" in APP_COPY["en"]["title"]
assert "梦境问答台" in APP_COPY["zh"]["title"]
```

Also test that a default `submit_dream_action(..., text_backend="demo") -> skip_to_card_action(...)` returns English labels and English card text, while `language="zh"` keeps Chinese output.

## Task 4: Today Tip Quality Gate

**Files:**
- Create: `tests/fixtures/today_tip_eval_cases.json`
- Create: `scripts/evaluate_today_tip_quality.py`
- Test: `tests/test_today_tip_quality_eval.py`

- [x] **Step 1: Add 10 representative cases**

Cover elevator, exam, train, phone full of water, missing shoes, locked room, rain note, abstract image clue, voice fragment, and severe distress.

- [x] **Step 2: Implement deterministic evaluator**

The evaluator must fail when:

- `today_tip` does not reference at least one required anchor.
- final text contains old customs words: `permit`, `contraband`, `clearance`, `sealed`, `pact`.
- ordinary cases include diagnosis, prophecy, or frightening certainty.
- English default output contains Chinese UI labels.

- [x] **Step 3: Wire test coverage**

Run:

```bash
.venv/bin/python scripts/evaluate_today_tip_quality.py
.venv/bin/python -m pytest tests/test_today_tip_quality_eval.py -q
```

Expected: evaluator prints zero failures and pytest passes.

## Task 5: MiniCPM Follow-Up Quality

**Files:**
- Modify: `dream_customs/prompts.py`
- Modify: `dream_customs/pipeline.py`
- Modify: `dream_customs/models.py`
- Test: `tests/test_pipeline.py`
- Test: `tests/test_dream_qa_refactor.py`

- [x] **Step 1: Strengthen follow-up prompt**

Update the question prompt to ask exactly one useful follow-up in the selected language, grounded in dream anchors and user mood.

- [x] **Step 2: Add fallback question quality guard**

Ensure fallback questions cite an anchor and avoid generic "how do you feel" unless tied to a detail.

- [x] **Step 3: Add tests**

Add tests proving an English elevator dream gets an English question mentioning elevator/button/floor 14, and a Chinese dream in `language="zh"` gets a Chinese question with the same anchors.

## Task 6: Documentation And Deployment

**Files:**
- Modify: `README.md`
- Modify: `PRODUCT.md`
- Modify: `docs/spec.md`
- Modify: `docs/prd.md`
- Modify: `docs/handoff.md`
- Modify: `docs/superpowers/plans/2026-06-08-post-refactor-polish.md`
- Create/update: `docs/smoke/2026-06-08-post-refactor-polish-smoke.md`

- [x] **Step 1: Update docs**

Docs must state:

- English is the default public hackathon experience.
- Chinese is available through an in-app language toggle.
- MiniCPM5 handles follow-up and Today Tip drafting.
- MiniCPM-V handles visual witness reports.
- The app remains non-diagnostic and not therapy.

- [x] **Step 2: Verify locally**

Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/evaluate_today_tip_quality.py
git diff --check
```

- [x] **Step 3: Commit and push**

Run:

```bash
git add <changed files>
git commit -m "feat: polish dream qa post-refactor flow"
git push origin feature/dream-customs-ui-voice-settings
```

- [ ] **Step 4: Sync HF Space**

Use `huggingface_hub.upload_folder(..., create_pr=True)` if direct push is not appropriate. Merge the Space PR in Chrome and verify:

```bash
git ls-remote space refs/heads/main
```

Expected: Space `main` advances to the deployment commit.

## Self-Review

- Spec coverage: covers GitHub main alignment, deployed smoke, English-first toggle, quality evaluation, MiniCPM follow-up quality, docs, tests, commit, push, and HF Space sync.
- Placeholder scan: no TBD/TODO placeholders remain.
- Type consistency: language values use `"en"` and `"zh"` across UI, actions, prompts, pipeline, tests, and docs.
