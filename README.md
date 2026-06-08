---
title: Dream Customs
emoji: ⚡
colorFrom: blue
colorTo: pink
sdk: gradio
sdk_version: 4.44.1
python_version: "3.10"
app_file: app.py
pinned: false
license: mit
short_description: Turn dream declarations into a playful next-day pact.
models:
  - openbmb/MiniCPM5-1B
  - openbmb/MiniCPM-V-4.6
tags:
  - gradio
  - minicpm
  - build-small-hackathon
  - dream-journal
---

# Dream Customs

A Build Small Hackathon Gradio app that helps users form a playful alliance with last night's dream.

## Concept

Dream Customs accepts dream declarations by text, image, or voice. It turns the dream into a gentle "customs negotiation" and returns a Today's Pact card: one practical suggestion, one weird 5-minute task, and one bedtime release phrase.

## Models

- `openbmb/MiniCPM-V-4.6` for image/sketch/note understanding.
- `openbmb/MiniCPM5-1B` for dream negotiation and pact generation.
- A small ASR adapter may be used only for voice transcription.
- The app defaults to a stable demo backend so the local Gradio flow always works.
- Optional Ollama adapters are included for local MiniCPM testing.

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
print(result["visitor_name"])
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

2026-06-05 local V2 verification passed: tests were green and the workbench flow reached a sealed pact through `Send to customs`, `Ask another question`, `Add material`, `Draft pact`, `Revise pact`, and `Seal today's pact`.

The public Space now serves the V2 workbench from Space `main` commit `8ad6f00628f800abc2dbefab05163aba94a5723f`. Public browser smoke, mobile readability, diagnostics, raw remote queue prediction, and a hosted text route smoke all reached a sealed pact on 2026-06-05. The current Modal backend pass requires a real `openbmb/MiniCPM-V-4.6` vision route smoke before delivery; demo vision fallback is runtime resilience, not a substitute for that smoke.

Current smoke details are tracked in `docs/smoke/2026-06-05-space-deployment-smoke.md`.

## Safety

This is not a therapy or diagnosis product. It gives playful reflection, small actions, and escalation copy for severe distress.
