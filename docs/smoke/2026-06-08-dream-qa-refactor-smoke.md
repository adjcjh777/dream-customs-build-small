# Dream QA Refactor Smoke - 2026-06-08

## Scope

Refactor the public Dream Customs app experience into Dream QA / 梦境问答台:

- Record -> Ask -> Interpret -> Today Tip product flow.
- Text-only demo fallback remains available.
- Image clues still route through the MiniCPM-V-4.6 witness adapter.
- Voice input remains transcription-only through ASR/browser dictation.
- Final result is `TodayTipCard`, not a permit, pact, contraband list, or seal.

## Local Runtime

Command:

```bash
GRADIO_SERVER_PORT=7862 .venv/bin/python app.py
```

Observed:

```text
Running on local URL:  http://0.0.0.0:7862
```

HTTP check:

```bash
curl -sS -I http://127.0.0.1:7862
```

Observed:

```text
HTTP/1.1 200 OK
content-type: text/html; charset=utf-8
```

## Automated Checks

Command:

```bash
.venv/bin/python -m pytest -q
```

Observed:

```text
91 passed, 2 warnings in 1.26s
```

Command:

```bash
git diff --check
```

Observed: no output.

## Flow Smoke

Input:

```text
我梦到在一栋老楼里，电梯按钮融化了，楼层数字停在 14。醒来有点焦虑。
```

Answer:

```text
像是还没开始就觉得来不及。
```

Observed action payload:

```text
submit_status= ask
question= 当你想到「电梯按钮」和「按钮融化」时，今天有没有一件真实的小事，你希望它变得更容易开始？
tip_status= tip
has_anchor= True
old_words= False
```

The final text included concrete anchors: `电梯`, `融化的按钮`, and `数字 14`.

## Browser Note

The in-app Browser automation surface timed out while attaching to the local webview twice during this run. Because that layer did not attach, visual screenshot verification was not claimed. Local HTTP and Python action smoke were completed instead.
