# Modal MiniCPM Backend Smoke - 2026-06-06

## Scope

- Modal app: `dream-customs-minicpm-backend`
- Text model: `openbmb/MiniCPM5-1B`
- Vision model: `openbmb/MiniCPM-V-4.6`
- Public UI remains Hugging Face Space `build-small-hackathon/dream-customs`
- Secrets and endpoint values were not printed, documented, or committed.

## Results

- Health endpoint: PASS
- Text smoke: PASS with `text_route=ok` and `text_questions=2`
- Vision smoke: PASS with `vision_route=ok` and `vision_clues=8`
- Acceptance eval: PASS with `passed=12`, `total=12`, `schema_valid_rate=1.0`, and `failures=[]`
- Hugging Face Space model route: PASS with `status=negotiating`, `text_backend=model`, `vision_backend=model`, one extracted image evidence item, and `visual_clue_count=8`
- Hugging Face Space demo fallback: PASS with `status=negotiating`, `text_backend=demo`, `vision_backend=demo`, one extracted image evidence item, and `visual_clue_count=3`
- Hugging Face Space hardware recovery: PASS after switching the Space from ZeroGPU back to `CPU basic`; public model route and demo fallback were re-smoked successfully.
- ZeroGPU compatibility fix: pending remote rebuild verification after adding the `@spaces.GPU` startup probe and making `model` the default backend.

## Notes

- GPU class remained `L4`; no upgrade was required for `openbmb/MiniCPM-V-4.6`.
- Modal text output keeps the real MiniCPM route first and repairs missing JSON fields only when schema validation would otherwise fail.
- Hugging Face Space secret sync was first attempted through the local HF token, but the API returned a non-secret `403 Forbidden: Authorization error`.
- The three Space secrets were replaced through the logged-in Hugging Face UI, then the Space was restarted and verified through the public Gradio API.
- The public Gradio Space can run on ZeroGPU once the lightweight `@spaces.GPU` startup probe is present. Modal credits still cover the L4 GPU inference backend, and `model` is now the default text and vision backend.
