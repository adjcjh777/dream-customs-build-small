---
title: Dream Customs
emoji: 🌤️
colorFrom: green
colorTo: yellow
sdk: gradio
sdk_version: 4.44.1
python_version: "3.10"
app_file: app.py
pinned: false
license: mit
short_description: Guided dream Q&A with one gentle today tip.
models:
  - openbmb/MiniCPM5-1B
  - openbmb/MiniCPM-V-4.6
tags:
  - gradio
  - minicpm
  - build-small-hackathon
  - dream-journal
---

# Dream QA / 梦境问答台

A Build Small Hackathon Gradio app that helps users unpack a dream step by step and leave with one grounded tip for today.

The Hugging Face Space may still be named `Dream Customs` for continuity, but the current product direction is Dream QA: record a dream, answer or skip gentle follow-up questions, read a grounded interpretation draft, and receive a `今日小 Tips`.

## Concept

Dream QA accepts dream fragments by text, image, or voice. It turns those fragments into a shared dream intake, asks a few gentle questions, and returns a Today Tip card: a short non-certain interpretation, one practical or caring suggestion for today, and an optional tiny action.

This is not a therapy, diagnosis, or prophecy product.

## Models

- `openbmb/MiniCPM-V-4.6` for image/sketch/note understanding.
- `openbmb/MiniCPM5-1B` for dream summary, follow-up questions, interpretation, and Today Tip generation.
- A small ASR adapter may be used only for voice transcription.
- The app defaults to a stable demo backend so the local Gradio flow always works.
- Optional Ollama adapters are included for local MiniCPM testing.

## User Flow

1. Enter a dream by text, image, voice, or a mix.
2. State or let the app infer the main question.
3. Answer or skip one or more follow-up questions.
4. Review a grounded interpretation.
5. Receive one Today Tip tied to concrete dream details.

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
- `DREAM_CUSTOMS_HOSTED_TOKEN`: shared bearer token checked by Modal and sent by the Space.

Set these only as Hugging Face Space repository secrets or local shell variables. Do not store values in `.env`, docs, logs, screenshots, or git. Missing endpoints or route failures fall back to deterministic demo behavior.

The Gradio UI defaults to `model` for both text and vision backends, so a configured Space calls Modal by default. The `demo` backend remains available in developer settings as the deterministic fallback path.

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
```

## Deployment Smoke Status

Historical smoke notes under `docs/smoke/` describe earlier pact/customs UI passes. They remain useful deployment history, but the current implementation target is the Dream QA flow documented in `docs/handoff.md`, `docs/spec.md`, and `docs/prd.md`.

## Safety

This is not a therapy or diagnosis product. It gives playful reflection, one small today tip, and escalation copy for severe distress.
