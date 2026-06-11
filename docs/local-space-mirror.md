# Local Space Mirror

Use this when you want to review Dream QA changes before they are merged into the Hugging Face Space.

The mirror does not copy the app into a second implementation. It imports the same `app.py` entrypoint and therefore uses the same `dream_customs.ui.app.build_demo()` path as the Space. Missing Modal endpoint secrets fall back to deterministic demo behavior, just like the public app.

## Start

```bash
.venv/bin/python scripts/local_space_mirror.py
```

Open:

```text
http://127.0.0.1:7862
```

The script prints a small manifest before starting Gradio:

- `app_file` should be `app.py`.
- default text, vision, and voice backends should be `modal`.
- endpoint/token fields are only reported as configured or not configured; values are not printed.

## Verify

In another terminal:

```bash
.venv/bin/python scripts/smoke_local_space_mirror.py
```

The smoke checks `/config` for the current Dream QA app title, composer CSS markers, debug panel marker, and modal backend defaults.

## Optional Runtime Secrets

If you want the local mirror to call the same private Modal routes as the configured Space, export these in your shell before starting the mirror:

```bash
export DREAM_CUSTOMS_TEXT_ENDPOINT=...
export DREAM_CUSTOMS_VISION_ENDPOINT=...
export DREAM_CUSTOMS_ASR_ENDPOINT=...
export DREAM_CUSTOMS_HOSTED_TOKEN=...
```

Do not commit these values, paste them into docs, or include them in screenshots. Without them, the app remains usable through the deterministic fallback route.

## When To Use

Run this before creating or merging a Hugging Face Space PR whenever a change affects:

- Gradio UI layout or CSS.
- Stepper state.
- Image, voice, or text input behavior.
- Debug/runtime panels.
- Default backend behavior.
