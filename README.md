# Dream Customs / 梦境海关

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

## Test

```bash
python -m pytest -q
```

## Safety

This is not a therapy or diagnosis product. It gives playful reflection, small actions, and escalation copy for severe distress.
