# Dream QA Agent Guide

This file is the agent-facing entry point for the Dream QA / Dream Customs Space.

```bash
curl https://huggingface.co/spaces/build-small-hackathon/dream-customs/agents.md
```

## App

- Public Space: https://huggingface.co/spaces/build-small-hackathon/dream-customs
- Runtime URL: https://build-small-hackathon-dream-customs.hf.space
- Product name: Dream QA
- Task: turn a dream fragment into one grounded follow-up question and one gentle Today Tip.

Dream QA is not a diagnosis, therapy, prophecy, or emergency tool. Treat every result as a soft reflection.

## Recommended Agent API

Use the text-only Gradio API endpoint:

```python
from gradio_client import Client

client = Client("https://build-small-hackathon-dream-customs.hf.space")
result = client.predict(
    "I dreamed the elevator button melted and the number stayed on 14.",
    "Uneasy",
    "It felt like being late before I had even started.",
    "en",
    api_name="/agent_dream_qa",
)
print(result["card_text"])
```

Input order:

1. `dream_text`: required dream fragment.
2. `mood`: optional waking mood, for example `Neutral`, `Uneasy`, `Foggy`, `Curious`, `Tired`, `A little amused`.
3. `answer`: optional answer to the follow-up question. Leave it empty to let Dream QA skip and generate a tip from the dream clues.
4. `language`: `en` or `zh`.

Expected output is a JSON object with:

- `status`: usually `tip` after a complete API call.
- `question`: the grounded follow-up question generated from the dream.
- `card_title`: `Today Tip` or `今日小 Tips`.
- `card_text`: copyable result text.
- `card_html`: rendered result card.
- `debug`: backend route and session state without secrets.

## Evaluation Checklist

An agent should consider the app healthy when all of these pass:

- `curl https://huggingface.co/spaces/build-small-hackathon/dream-customs/agents.md` returns this guide, not `Entry not found`.
- `/config` title is `Dream QA`.
- Text generation, image understanding, and voice input default to `modal`.
- `/config` exposes `agent_dream_qa` and does not require image/audio inputs for the public agent API.
- A sample dream reaches `status == "tip"`.
- The Today Tip mentions at least one concrete dream anchor.
- The result avoids diagnosis, prophecy, fate claims, and frightening certainty.

## Good Smoke Prompt

```text
Dream: I dreamed I was in an old apartment building. The elevator button melted like wax, and the floor number stayed on 14.
Mood: Uneasy
Answer: It felt like being late before I had even started.
```

The result should mention the elevator, button, or 14, and should suggest one small first step rather than a hard command.
