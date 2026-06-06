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

## Notes

- GPU class remained `L4`; no upgrade was required for `openbmb/MiniCPM-V-4.6`.
- Modal text output keeps the real MiniCPM route first and repairs missing JSON fields only when schema validation would otherwise fail.
- Hugging Face Space secret sync was attempted through the local HF token, but the API returned a non-secret `403 Forbidden: Authorization error`. Public Space model-route verification remains pending until the Space secrets are updated with the deployed Modal endpoint values and hosted token.
