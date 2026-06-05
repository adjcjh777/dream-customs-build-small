# Dream Customs V4 Design QA

Date: 2026-06-05

Reference: user-provided Codex-style multimodal composer screenshot.

## Checks

- First screen uses one rounded multimodal composer instead of separate form blocks.
- Visible composer tools are limited to Image, Voice, Mood, Add, and Send.
- Technical Text/Vision routes are collapsed under Model routes.
- Pact inspector remains visible beside the composer on desktop.
- Timeline, diagnostics, examples, workflow shortcuts, and refinement controls are secondary.
- Text-only Chrome flow completed: Send -> Draft pact -> Seal today's pact.
- Sealed output renders a screenshot-friendly Today's Pact card.
- No desktop horizontal overflow in Chrome at the inspected viewport.

## Notes

- Image and voice use compact upload buttons to avoid large Gradio media drop zones in the first screen.
- Voice upload remains available as an input to the existing ASR adapter path.
- The UI keeps safety copy non-diagnostic.

final result: passed
