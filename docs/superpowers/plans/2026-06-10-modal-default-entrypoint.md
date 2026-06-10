# Modal Default Entrypoint Plan - 2026-06-10

## Goal

Make the public Dream QA default backend route explicit: text and image understanding should enter through the Modal-hosted MiniCPM path by default, while deterministic demo behavior remains available as a user-selectable and failure fallback route.

## Guardrails

- Do not store or print endpoint URLs, tokens, HF tokens, Modal tokens, or secret values.
- Keep text-only and demo fallback behavior working when hosted endpoints are absent, cold, slow, or failing.
- Do not replace the Hugging Face Space Gradio frontend with Modal.
- Do not add non-MiniCPM default models.

## Tasks

- [x] Add a regression test that expects default text and vision backends to be `modal`.
- [x] Change the default text and vision backend constants to `modal`.
- [x] Make the Advanced backend labels show Modal as the intentional default entrypoint.
- [x] Update docs to describe Modal as the default configured route and demo as fallback.
- [x] Run focused tests, full pytest, eval, local smoke, and whitespace checks.
- [ ] Commit, push, sync to Hugging Face Space, merge, and re-check the public app.

## Progress

- Focused regression tests pass after changing defaults to `modal`.
- Local default action smoke passes without configured endpoint secrets; the app records `modal` in debug and falls back to a usable Q&A flow.
- Full pytest passes with 98 tests; Today Tip eval passes 11 cases; `git diff --check` passes.
