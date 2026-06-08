# Dream Customs UI/UX V3 Rescue Plan

> **For agentic workers:** Use `superpowers:executing-plans` to execute this checklist. This plan fixes the public V2 workbench issues found from screenshots and live Space inspection.

**Goal:** Make the Gradio app feel clear, warm, and trustworthy enough that a tired user will actually type a dream. The primary declaration controls must be visible immediately, the phase rail must be actionable, and the page must not contain long empty scroll areas.

**Design north star:** Trust-first night desk. Keep the dream customs atmosphere, but make the input area calm, obvious, and inviting. The product should feel like a safe morning ritual, not a dark admin dashboard.

## Problems To Fix

- [x] The dream input and upload controls sit below the timeline and pact inspector, so the user must scroll before taking the core action.
- [x] The primary submit button is buried below image/audio/dropdown controls and a row of many equally weighted buttons.
- [x] The `Declare / Inspect / Draft / Seal` rail is rendered as static text, so it looks clickable but does nothing.
- [x] Large fixed panel heights create long empty space when the session has little content.
- [x] Gradio default controls leak white dropdown/input styling inside the dark app shell.
- [x] The interface feels cold and technical; it needs warmer trust cues without turning into therapy or parchment.

## Task 1: Update Product Design Contract

- [x] Update `DESIGN.md` with a first-screen trust rule.
- [x] Update `docs/handoff.md` so it reflects current deployed V2 state and this V3 rescue target.

## Task 2: Rebuild First Screen Layout

- [x] Move the composer above timeline on desktop and mobile.
- [x] Put `Send to customs`, `Draft pact`, and `Seal today's pact` beside or directly below the dream text field.
- [x] Keep image, voice, mood, text route, and vision route visible in the first composer panel.
- [x] Put timeline below the declaration/inspector focus area.
- [x] Keep diagnostics and examples collapsed below the main workflow.

## Task 3: Make Phase Rail Real

- [x] Add real Gradio buttons for `Declare`, `Inspect`, `Draft`, and `Seal`.
- [x] Wire them to material filing, question asking, draft generation, and pact sealing.
- [x] Keep the rendered status bar as status, not fake navigation.

## Task 4: Repair Visual System

- [x] Reduce cold one-note dark blue dominance with warm lamp and plum tones.
- [x] Strengthen focus, hover, dropdown, upload, and placeholder styling.
- [x] Remove unnecessary fixed min-heights and sticky composer behavior.
- [x] Improve mobile stacking and prevent button text overflow.

## Task 5: Verify

- [x] Run `.venv/bin/python -m pytest -q`.
- [x] Run the Gradio app locally.
- [x] Inspect desktop and mobile first screen.
- [x] Complete a text-only flow through send, question, draft, revise, and seal.
- [x] Confirm there is no long empty page below normal content.
- [x] Commit and push the branch after verification.

## Verification Notes

- Desktop Chrome extension verification reached sealed state through `Send to customs -> Inspect -> Draft pact -> Revise pact -> Seal today's pact`.
- Desktop state after seal showed `Current: Sealed`, `DC-DEMO-014`, and `Today's Pact`.
- Mobile Chrome CDP verification used a `390x844` viewport and returned `scrollWidth=390`, so there is no horizontal overflow.
- Mobile first screen shows the phase buttons, dream text field, `Send to customs`, and the image evidence entry beginning inside the first viewport.
- Final automated checks before commit: `.venv/bin/python -m pytest -q` and `git diff --check`.
