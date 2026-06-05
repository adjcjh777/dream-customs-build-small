# Dream Customs / 梦境海关

A Build Small Hackathon Gradio app that helps users form a playful alliance with last night's dream.

## Concept

Dream Customs accepts dream declarations by text, image, or voice. It turns the dream into a gentle "customs negotiation" and returns a Today's Pact card: one practical suggestion, one weird 5-minute task, and one bedtime release phrase.

## Models

- `openbmb/MiniCPM-V-4.6` for image/sketch/note understanding.
- `openbmb/MiniCPM5-1B` for dream negotiation and pact generation.
- A small ASR adapter may be used only for voice transcription.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Test

```bash
python -m pytest -q
```

## Safety

This is not a therapy or diagnosis product. It gives playful reflection, small actions, and escalation copy for severe distress.
