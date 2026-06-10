# Smoke: OpenDesign UI/UX Refinement

Date: 2026-06-10
Branch: feature/dream-qa-opendesign-ui
Commit: 43e611e

## Changes

Based on OpenDesign analysis, implement desktop-first UI refinements:

- 3-column → 2-column layout (main flow + context rail)
- Remove left sidebar step cards, replace with inline step pill bar
- Simplified top bar (title + language toggle + reset)
- Narrowed max-width from 1520px to 1080px
- Image upload always visible (not in accordion)
- Warmer, more conversational copy in English and Chinese

## Test Results

- `python -m pytest -q`: 193 passed
- Manual smoke: input dream → question → skip → result card with Today Tip referencing dream details
- UI renders correctly on desktop (1280px width)

## Screenshots

- dream-qa-smoke-01-record.png: Initial input state with greeting and chip shortcuts
- dream-qa-smoke-02-ask.png: Follow-up question in chat-bubble style
- dream-qa-smoke-03-result.png: Final result card with dream summary, interpretation, and Today Tip
- dream-qa-smoke-04-full.png: Full page view

## HF Space Sync

Not yet synced. Remote main has diverged from local branch.
