---
title: Dream QA
emoji: 🌤️
colorFrom: green
colorTo: yellow
sdk: gradio
sdk_version: 4.44.1
python_version: "3.10"
app_file: app.py
pinned: false
license: mit
short_description: Morning dream Q&A with one grounded Today Tip.
models:
  - openbmb/MiniCPM5-1B
  - openbmb/MiniCPM-V-4.6
tags:
  - gradio
  - minicpm
  - build-small-hackathon
  - thousand-token-wood
  - backyard-ai
  - openbmb
  - modal
  - openai-codex
  - off-brand
  - best-demo
  - dream-journal
---

# Dream QA / The Morning Question Desk

A Build Small Hackathon Gradio app that turns a fresh dream into one grounded Morning Ticket.

The Hugging Face Space may still be named `Dream Customs` for continuity, but the current product direction is Dream QA / 清晨问讯室: record a dream, answer or skip one gentle question, and receive a screenshot-friendly ticket with one `Today Tip`.

The public hackathon demo is English-first for international judges. A visible in-app language toggle keeps the Chinese experience available as `中文`.

## Concept

Dream QA accepts dream fragments by text, image, or voice. It turns those fragments into a shared dream intake, extracts up to three concrete dream anchors, asks one grounded follow-up question, and returns a Morning Ticket: the Today Tip first, a tiny 5-minute action, and a short non-certain supporting reflection.

The fastest demo path is text or image first: choose a sample dream, or enter a short dream about a dead phone, a late elevator, or a misunderstood friend, then answer or skip one grounded question. Voice input is available as an ASR path, but the primary demo should not rely on live transcription.

This is not a therapy, diagnosis, or prophecy product.

## Submission Status

- Space: <https://huggingface.co/spaces/build-small-hackathon/dream-customs>
- Direct app: <https://build-small-hackathon-dream-customs.hf.space>
- GitHub: <https://github.com/adjcjh777/dream-customs-build-small>
- Primary track: Thousand Token Wood.
- Secondary track: Backyard AI.
- Demo assets in this repo: `videos/dreamqa_01_text_only.mp4`, `videos/dreamqa_02_image_only.mp4`, `videos/dreamqa_03_text_plus_image.mp4`.
- Final public demo video URL: to be added after the final upload.
- Final social post URL: to be added after publishing the X/Instagram post.
- Final submission prep notes: `docs/submission/2026-06-14-build-small-final-pack.md`.

## Models

- `openbmb/MiniCPM-V-4.6` for image/sketch/note understanding.
- `openbmb/MiniCPM5-1B` for dream summary, follow-up questions, interpretation, and Today Tip generation.
- A small ASR adapter may be used only for voice transcription.
- The app defaults to the Modal-hosted MiniCPM route when endpoint secrets are configured, with stable demo fallback when hosted routes are unavailable.
- Optional Ollama adapters are included for local MiniCPM testing.
- MiniCPM prompts are language-aware: English by default, Chinese when the user chooses `中文`.

## User Flow

1. Enter a dream by text, image, voice, or a mix.
2. Let the app surface the dream anchors.
3. Answer or skip one follow-up question.
4. Receive a Morning Ticket with one Today Tip tied to concrete dream details and the user's answer.
5. Open the small-model note if the judge wants to see how MiniCPM-V and MiniCPM5-1B split the work.

## Language

- Default public UI: English.
- Toggle: `English / 中文`.
- English mode translates or paraphrases non-English dream anchors into natural English, so an international judge does not see mixed UI/model language.
- Chinese mode keeps the warm `梦境问答台` wording.
- Today Tips should be small and optional: "write one honest line" beats "handle it immediately."

## Current Direction References

- Product spec: `docs/spec.md`
- PRD: `docs/prd.md`
- Handoff: `docs/handoff.md`
- Design system: `DESIGN.md`
- Prototype images:
  - `docs/prototypes/2026-06-08-dream-qa-mobile-flow.png`
  - `docs/prototypes/2026-06-08-dream-qa-desktop-workbench.png`
  - `docs/prototypes/2026-06-08-dream-qa-tips-card.png`

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:7860`.

## Local Space Mirror

For pre-merge UI review, run the same `app.py` entrypoint with the local Space mirror wrapper:

```bash
.venv/bin/python scripts/local_space_mirror.py
```

Open `http://127.0.0.1:7862`, then verify the Gradio config in another terminal:

```bash
.venv/bin/python scripts/smoke_local_space_mirror.py
```

Use this path before merging Hugging Face Space PRs so UI changes can be reviewed locally. Details: `docs/local-space-mirror.md`.

## Optional Ollama Models

```bash
ollama pull hf.co/openbmb/MiniCPM5-1B-GGUF:Q8_0
ollama pull openbmb/minicpm-v4.6
```

Then switch the UI engine controls from `demo` to `ollama`.

Local smoke notes from this Mac mini:

- Memory/size is fine: 16 GB RAM handled the local model downloads.
- `hf.co/openbmb/MiniCPM5-1B-GGUF:Q8_0` loads in Ollama, but current output was malformed for JSON prompts.
- `openbmb/minicpm-v4.6` pulled successfully, but current Ollama runner returned `unable to load model`.
- Because of that, the MVP keeps Ollama optional and falls back to deterministic demo behavior.

## Optional Hosted MiniCPM Routes

The public Space stays lightweight and can call private Modal endpoints through runtime secrets:

- `DREAM_CUSTOMS_TEXT_ENDPOINT`: Modal text route for `openbmb/MiniCPM5-1B`.
- `DREAM_CUSTOMS_VISION_ENDPOINT`: Modal vision route for `openbmb/MiniCPM-V-4.6`.
- `DREAM_CUSTOMS_ASR_ENDPOINT`: Modal ASR adapter route for voice-note transcription.
- `DREAM_CUSTOMS_HOSTED_TOKEN`: shared bearer token checked by Modal and sent by the Space.

Set these only as Hugging Face Space repository secrets or local shell variables. Do not store values in `.env`, docs, logs, screenshots, or git. Missing endpoints or route failures fall back to deterministic demo behavior.

The Gradio UI defaults to `modal` for text, vision, and voice transcription backends, so a configured Space enters the private Modal routes first. The `demo` backend remains available in developer settings and as the deterministic fallback path when hosted routes are missing or fail.

The Hugging Face Space may run on ZeroGPU for hackathon hardware eligibility. `dream_customs.zerogpu` registers a lightweight `@spaces.GPU` startup probe so ZeroGPU accepts the app, but real MiniCPM inference still happens on the private Modal backend.

Token-safe text smoke:

```bash
python - <<'PY'
import os
from dream_customs.models import HostedMiniCPMTextClient

client = HostedMiniCPMTextClient(
    endpoint=os.environ["DREAM_CUSTOMS_TEXT_ENDPOINT"],
    token=os.getenv("DREAM_CUSTOMS_HOSTED_TOKEN", ""),
)
result = client.generate_negotiation("I missed an elevator in a foggy dream.")
print(result)
PY
```

Token-safe vision smoke:

```bash
python - <<'PY'
import os
from dream_customs.models import HostedMiniCPMVisionClient

client = HostedMiniCPMVisionClient(
    endpoint=os.environ["DREAM_CUSTOMS_VISION_ENDPOINT"],
    token=os.getenv("DREAM_CUSTOMS_HOSTED_TOKEN", ""),
)
print(client.extract_clues(os.environ["DREAM_CUSTOMS_SMOKE_IMAGE"]))
PY
```

## Test

```bash
python -m pytest -q
python scripts/evaluate_today_tip_quality.py
```

## Deployment Smoke Status

Latest local Dream QA refactor smoke:

- `docs/smoke/2026-06-08-dream-qa-refactor-smoke.md`
- `docs/smoke/2026-06-08-post-refactor-polish-smoke.md`

Historical smoke notes and earlier pact/customs plans have been archived to `archive/dream-customs-legacy/`. The current implementation target is the Dream QA flow documented in `docs/handoff.md`, `docs/spec.md`, and `docs/prd.md`.

## Safety

This is not a therapy or diagnosis product. It gives playful reflection, one small today tip, and escalation copy for severe distress.
