# Dream QA Post-Refactor Polish Smoke - 2026-06-08

## Scope

Follow-up polish after the Dream QA refactor:

- English-first public hackathon experience.
- Visible `English / 中文` language toggle.
- Chinese mode remains available.
- Deterministic Today Tip quality gate.
- Follow-up questions and Today Tips remain grounded in dream anchors.

## Local Runtime

Command:

```bash
GRADIO_SERVER_PORT=7862 .venv/bin/python app.py
```

Observed:

```text
Running on local URL:  http://0.0.0.0:7862
```

## Local Config Check

Command:

```bash
.venv/bin/python - <<'PY'
import json
from urllib.request import urlopen
with urlopen("http://127.0.0.1:7862/config", timeout=30) as response:
    cfg = json.load(response)
print({"title": cfg.get("title"), "version": cfg.get("version"), "mode": cfg.get("mode"), "component_count": len(cfg.get("components", []))})
PY
```

Observed config included:

```text
title=Dream QA
version=4.44.1
mode=blocks
component_count=72
```

The config also showed English default UI copy including `Dream QA`, `Record`, `Question`, `Interpret`, `Today Tip`, `Dream note`, `Try example`, `Continue`, `Language`, and choices `English` / `中文`.

## Automated Checks

Command:

```bash
.venv/bin/python -m pytest -q
```

Observed:

```text
94 passed, 2 warnings
```

Command:

```bash
.venv/bin/python scripts/evaluate_today_tip_quality.py
```

Observed:

```json
{
  "case_count": 10,
  "failures": {},
  "passes": true
}
```

Command:

```bash
git diff --check
```

Observed: no output.

## Action Smoke

English default input:

```text
I dreamed I was in an old apartment building. The elevator button melted like wax, and the floor number stayed on 14. I woke up anxious.
```

Observed action payload:

```text
submit_status=ask
language=en
question=When you think about the elevator and the melted button, what real thing today feels hard to start?
tip_status=tip
title=Today Tip
has_elevator=True
has_old_words=False
```

Chinese toggle input:

```text
我梦到电梯按钮融化，楼层数字停在 14。
```

Observed action payload:

```text
zh_status=tip
zh_title=今日小 Tips
has_zh_anchor=True
```

## Browser Notes

- In-app Browser reached `http://127.0.0.1:7862/` and saw title `Dream QA`, but the DOM snapshot stayed at Gradio's `加载中...` placeholder during this run.
- Chrome extension control returned a closed native pipe while opening the same local URL.
- Because both browser automation surfaces were unstable, no visual screenshot claim is made here. The local Gradio `/config`, app build check, action flow, full pytest suite, and deterministic quality evaluator passed.

## Deployment Status

Not yet deployed in this smoke file. After commit and GitHub/HF sync, update this file or add a follow-up remote smoke section with:

- GitHub PR URL and merge commit.
- HF Space PR discussion URL and Space `main` SHA.
- Public Space `/config` result.
- Public app flow check.
