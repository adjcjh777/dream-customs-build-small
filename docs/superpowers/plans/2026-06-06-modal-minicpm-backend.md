# Modal MiniCPM Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Use the available Modal credits to deploy real MiniCPM text and vision inference endpoints, then connect the existing Hugging Face Space UI through private runtime secrets while preserving the deterministic demo fallback.

**Architecture:** Keep Hugging Face Space as the public Gradio frontend and use Modal as a hidden GPU backend. Modal exposes one text endpoint for `openbmb/MiniCPM5-1B` JSON generation and one vision endpoint for `openbmb/MiniCPM-V-4.6` visual clue extraction. The existing `HostedMiniCPMTextClient` and `HostedMiniCPMVisionClient` continue to call plain JSON HTTP endpoints through `DREAM_CUSTOMS_TEXT_ENDPOINT`, `DREAM_CUSTOMS_VISION_ENDPOINT`, and `DREAM_CUSTOMS_HOSTED_TOKEN`.

**Tech Stack:** Python, Modal, FastAPI endpoint decorators, Transformers, PyTorch, Pillow, Gradio, Hugging Face Space repository secrets, pytest.

---

## Scope And Non-Negotiables

- Do not replace the public Hugging Face Space with Modal.
- Do not store endpoint tokens, Hugging Face tokens, Modal tokens, or secret values in git, docs, logs, screenshots, or example files.
- Keep the UI default backend as `demo`.
- Keep text-only demo fallback working when Modal endpoints are missing, cold, slow, or failing.
- Keep the model family constrained to `MiniCPM` before trying unrelated small models.
- Completion requires a working `MiniCPM-V-4.6` vision route. Demo vision fallback is allowed only as runtime resilience after the real vision route has passed smoke; it is not an acceptable substitute for final delivery.
- Confirm Hugging Face Space secrets at the start of execution. If the Space is missing required secrets or needs updated Modal endpoint values, stop early and ask the user to fill or approve filling them before remote Space verification.
- Treat voice transcription as unchanged for this pass; ASR remains fake/demo unless a separate plan approves a real ASR adapter.

## File Structure

- Create `modal_backend/__init__.py`: package marker for Modal backend helpers.
- Create `modal_backend/contracts.py`: pure request/response helpers that are importable by tests without importing `modal`, `torch`, or `transformers`.
- Create `modal_backend/dream_customs_modal.py`: Modal app definition, GPU classes, model loading, authentication, `/text`, `/vision`, and health endpoint.
- Create `tests/test_modal_contract.py`: fast local contract tests for request parsing, image decoding, auth behavior, and response shape.
- Create `scripts/smoke_hosted_routes.py`: local smoke script that calls configured hosted endpoints without printing secret values.
- Create `scripts/eval_hosted_routes.py`: small acceptance evaluator for schema validity, safety edge cases, and vision clue extraction.
- Modify `README.md`: add Modal deployment and HF Space secret setup instructions.
- Modify `docs/handoff.md`: record the intended production route and fallback contract.
- Modify `docs/smoke/2026-06-06-modal-minicpm-backend-smoke.md`: capture smoke results after deployment.

## Task 0: Prepare The Branch And Baseline

**Files:**
- Read: `AGENTS.md`
- Read: `docs/spec.md`
- Read: `docs/prd.md`
- Read: `docs/handoff.md`
- Read: `dream_customs/models.py`
- Read: `dream_customs/app_logic.py`

- [x] **Step 1: Confirm repository and branch**

Run:

```bash
pwd
git status --short --branch
git remote -v
```

Expected:

```text
/Users/junhaocheng/working-dir/ai-competitions/build-small-hackthon
## feature/dream-customs-mvp...origin/feature/dream-customs-mvp
origin  https://github.com/adjcjh777/dream-customs-build-small.git (fetch)
origin  https://github.com/adjcjh777/dream-customs-build-small.git (push)
```

- [x] **Step 2: Sync latest code**

Run:

```bash
git pull
```

Expected:

```text
Already up to date.
```

If remote changes arrive, read them before editing and keep this plan aligned with the current file names.

- [x] **Step 3: Create implementation branch**

Run:

```bash
git switch -c feature/modal-minicpm-backend
```

Expected:

```text
Switched to a new branch 'feature/modal-minicpm-backend'
```

- [x] **Step 4: Run baseline tests**

Run:

```bash
.venv/bin/python -m pytest -q
```

Expected: all existing tests pass.

- [x] **Step 5: Confirm Hugging Face Space secret readiness**

Before writing backend code, open the Hugging Face Space settings for `build-small-hackathon/dream-customs` and confirm whether these repository secrets already exist:

```text
DREAM_CUSTOMS_TEXT_ENDPOINT
DREAM_CUSTOMS_VISION_ENDPOINT
DREAM_CUSTOMS_HOSTED_TOKEN
```

Expected: the secrets exist, or the worker has stopped and asked the user to fill them before public Space verification. Do not print or copy secret values. If the Modal endpoint URLs will be newly generated later, record only this non-secret status in your notes:

```text
HF Space secrets preflight: present, may need endpoint value refresh after Modal deploy.
```

Commit is not needed for this task.

Observed 2026-06-06: required secret keys/value readiness was confirmed by the user. Endpoint values still need refresh after Modal deploy. No secret values were recorded.

## Task 1: Add Pure Modal Endpoint Contract Helpers

**Files:**
- Create: `modal_backend/__init__.py`
- Create: `modal_backend/contracts.py`
- Create: `tests/test_modal_contract.py`

- [x] **Step 1: Write failing contract tests**

Create `tests/test_modal_contract.py`:

```python
import base64

from modal_backend.contracts import (
    AuthError,
    decode_image_payload,
    ensure_authorized,
    normalize_text_payload,
    response_payload,
)


def test_normalize_text_payload_accepts_prompt():
    payload = normalize_text_payload({"prompt": "Return JSON.", "max_tokens": 123})
    assert payload["prompt"] == "Return JSON."
    assert payload["max_tokens"] == 123
    assert payload["temperature"] == 0.2


def test_normalize_text_payload_accepts_openai_style_messages():
    payload = normalize_text_payload(
        {"messages": [{"role": "user", "content": "Dream of an elevator."}]}
    )
    assert payload["prompt"] == "Dream of an elevator."
    assert payload["max_tokens"] == 700


def test_normalize_text_payload_clamps_max_tokens():
    payload = normalize_text_payload({"prompt": "x", "max_tokens": 9000})
    assert payload["max_tokens"] == 1200


def test_decode_image_payload_accepts_image_key():
    encoded = base64.b64encode(b"fake-image-bytes").decode("ascii")
    assert decode_image_payload({"image": encoded}) == b"fake-image-bytes"


def test_decode_image_payload_accepts_images_list():
    encoded = base64.b64encode(b"fake-image-bytes").decode("ascii")
    assert decode_image_payload({"images": [encoded]}) == b"fake-image-bytes"


def test_response_payload_uses_existing_client_shape():
    assert response_payload("hello") == {"response": "hello"}


def test_ensure_authorized_allows_empty_expected_token_for_local_smoke():
    ensure_authorized("", "")


def test_ensure_authorized_accepts_bearer_token():
    ensure_authorized("Bearer secret-value", "secret-value")


def test_ensure_authorized_rejects_wrong_token():
    try:
        ensure_authorized("Bearer wrong", "secret-value")
    except AuthError as exc:
        assert str(exc) == "Unauthorized hosted route request."
    else:
        raise AssertionError("Expected AuthError")
```

- [x] **Step 2: Run tests to verify failure**

Run:

```bash
.venv/bin/python -m pytest tests/test_modal_contract.py -q
```

Expected:

```text
ModuleNotFoundError: No module named 'modal_backend'
```

- [x] **Step 3: Create package marker**

Create `modal_backend/__init__.py`:

```python
"""Modal backend package for Dream Customs."""
```

- [x] **Step 4: Implement pure endpoint contract helpers**

Create `modal_backend/contracts.py`:

```python
import base64
from typing import Any, Dict


class AuthError(Exception):
    """Raised when a hosted route request is not authorized."""


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_text_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    prompt = _clean_text(payload.get("prompt"))
    if not prompt:
        messages = payload.get("messages")
        if isinstance(messages, list):
            parts = []
            for item in messages:
                if isinstance(item, dict):
                    content = _clean_text(item.get("content"))
                    if content:
                        parts.append(content)
            prompt = "\n".join(parts).strip()
    max_tokens = payload.get("max_tokens", 700)
    try:
        max_tokens = int(max_tokens)
    except (TypeError, ValueError):
        max_tokens = 700
    max_tokens = max(64, min(max_tokens, 1200))
    temperature = payload.get("temperature", 0.2)
    try:
        temperature = float(temperature)
    except (TypeError, ValueError):
        temperature = 0.2
    temperature = max(0.0, min(temperature, 0.7))
    return {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }


def decode_image_payload(payload: Dict[str, Any]) -> bytes:
    encoded = payload.get("image")
    if not encoded and isinstance(payload.get("images"), list) and payload["images"]:
        encoded = payload["images"][0]
    if not encoded:
        raise ValueError("Missing image payload.")
    if isinstance(encoded, bytes):
        encoded = encoded.decode("ascii")
    return base64.b64decode(str(encoded))


def ensure_authorized(authorization_header: str, expected_token: str) -> None:
    expected_token = expected_token.strip()
    if not expected_token:
        return
    header = authorization_header.strip()
    if header.lower().startswith("bearer "):
        supplied = header.split(" ", 1)[1].strip()
    else:
        supplied = header
    if supplied != expected_token:
        raise AuthError("Unauthorized hosted route request.")


def response_payload(text: str) -> Dict[str, str]:
    return {"response": text}
```

- [x] **Step 5: Run contract tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_modal_contract.py -q
```

Expected:

```text
9 passed
```

- [x] **Step 6: Run full tests**

Run:

```bash
.venv/bin/python -m pytest -q
```

Expected: all tests pass.

- [x] **Step 7: Commit contract helpers**

Run:

```bash
git add modal_backend/__init__.py modal_backend/contracts.py tests/test_modal_contract.py
git commit -m "test: add modal endpoint contract helpers"
```

## Task 2: Add Modal Text And Vision Services

**Files:**
- Create: `modal_backend/dream_customs_modal.py`
- Modify: `requirements.txt`

- [x] **Step 1: Decide dependency placement**

Keep Modal-only dependencies inside the Modal image in `modal_backend/dream_customs_modal.py`. Do not add `modal`, `torch`, or heavy Transformers-only deployment packages to `requirements.txt` unless local tests need them. The public Hugging Face Space should stay lightweight.

- [x] **Step 2: Create Modal service file**

Create `modal_backend/dream_customs_modal.py`:

```python
import io
import os
import tempfile
from typing import Any, Dict

import modal

from modal_backend.contracts import (
    AuthError,
    decode_image_payload,
    ensure_authorized,
    normalize_text_payload,
    response_payload,
)


APP_NAME = "dream-customs-minicpm-backend"
TEXT_MODEL = "openbmb/MiniCPM5-1B"
VISION_MODEL = "openbmb/MiniCPM-V-4.6"
MINUTES = 60

app = modal.App(APP_NAME)

hf_cache = modal.Volume.from_name("dream-customs-hf-cache", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git")
    .pip_install(
        "accelerate",
        "einops",
        "fastapi[standard]",
        "pillow",
        "protobuf",
        "sentencepiece",
        "torch",
        "torchvision",
        "transformers>=4.56",
    )
)

secrets = [modal.Secret.from_name("dream-customs-modal-secrets")]


def _auth_header(request: Any) -> str:
    return str(request.headers.get("authorization", ""))


def _expected_token() -> str:
    return os.getenv("DREAM_CUSTOMS_HOSTED_TOKEN", "").strip()


def _json_error(message: str, status: str = "error") -> Dict[str, str]:
    return {"status": status, "response": "", "error": message}


@app.function(image=image, secrets=secrets)
@modal.fastapi_endpoint(method="GET", docs=True)
def health() -> Dict[str, str]:
    return {
        "status": "ok",
        "app": APP_NAME,
        "text_model": TEXT_MODEL,
        "vision_model": VISION_MODEL,
    }


@app.cls(
    image=image,
    gpu="L4",
    timeout=10 * MINUTES,
    scaledown_window=5 * MINUTES,
    volumes={"/root/.cache/huggingface": hf_cache},
    secrets=secrets,
)
class TextService:
    @modal.enter()
    def load(self):
        from transformers import pipeline

        self.pipe = pipeline(
            "text-generation",
            model=os.getenv("DREAM_CUSTOMS_TEXT_MODEL", TEXT_MODEL),
            device_map="auto",
            torch_dtype="auto",
            trust_remote_code=True,
        )

    @modal.fastapi_endpoint(method="POST", docs=True)
    async def text(self, request):
        try:
            ensure_authorized(_auth_header(request), _expected_token())
        except AuthError as exc:
            return _json_error(str(exc), status="unauthorized")
        payload = await request.json()
        normalized = normalize_text_payload(payload)
        if not normalized["prompt"]:
            return _json_error("Missing prompt.")
        output = self.pipe(
            normalized["prompt"],
            max_new_tokens=normalized["max_tokens"],
            do_sample=normalized["temperature"] > 0,
            temperature=max(normalized["temperature"], 0.01),
            return_full_text=False,
        )
        text = str(output[0].get("generated_text", "")).strip()
        return response_payload(text)


@app.cls(
    image=image,
    gpu="L4",
    timeout=10 * MINUTES,
    scaledown_window=5 * MINUTES,
    volumes={"/root/.cache/huggingface": hf_cache},
    secrets=secrets,
)
class VisionService:
    @modal.enter()
    def load(self):
        from transformers import pipeline

        self.pipe = pipeline(
            "image-text-to-text",
            model=os.getenv("DREAM_CUSTOMS_VISION_MODEL", VISION_MODEL),
            device_map="auto",
            torch_dtype="auto",
            trust_remote_code=True,
        )

    @modal.fastapi_endpoint(method="POST", docs=True)
    async def vision(self, request):
        try:
            ensure_authorized(_auth_header(request), _expected_token())
        except AuthError as exc:
            return _json_error(str(exc), status="unauthorized")
        payload = await request.json()
        prompt = str(payload.get("prompt") or "").strip()
        if not prompt:
            prompt = (
                "Extract concise dream-like visual clues from this image. "
                "Return a single JSON object with keys objects, places, visible_text, "
                "colors, mood_cues, and uncertain_details. Do not diagnose."
            )
        try:
            image_bytes = decode_image_payload(payload)
        except ValueError as exc:
            return _json_error(str(exc))
        from PIL import Image

        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
            pil_image.save(temp_file.name)
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "path": temp_file.name},
                        {"type": "text", "text": prompt},
                    ],
                }
            ]
            result = self.pipe(text=messages, max_new_tokens=int(payload.get("max_tokens", 320)))
        return response_payload(str(result).strip())
```

- [x] **Step 3: Run import check without requiring Modal locally**

Run:

```bash
.venv/bin/python - <<'PY'
from modal_backend.contracts import response_payload
print(response_payload("ok"))
PY
```

Expected:

```text
{'response': 'ok'}
```

- [x] **Step 4: Run tests**

Run:

```bash
.venv/bin/python -m pytest -q
```

Expected: all tests pass.

- [x] **Step 5: Commit Modal service scaffold**

Run:

```bash
git add modal_backend/dream_customs_modal.py
git commit -m "feat: add modal minicpm backend service"
```

## Task 3: Validate Modal Service Locally With `modal serve`

**Files:**
- Read: `modal_backend/dream_customs_modal.py`

- [x] **Step 1: Confirm Modal CLI is authenticated**

Run:

```bash
modal token set --help >/dev/null && modal profile current
```

Expected: a Modal profile for workspace `cjh-12569` or a clear CLI message requiring login.

If login is required, run:

```bash
modal setup
```

Complete browser login for workspace `cjh-12569`.

- [x] **Step 2: Create Modal secret without printing values**

Run with values pasted only into the command invocation, not into a file:

```bash
modal secret create dream-customs-modal-secrets \
  HF_TOKEN="$HF_TOKEN" \
  DREAM_CUSTOMS_HOSTED_TOKEN="$DREAM_CUSTOMS_HOSTED_TOKEN"
```

Expected:

```text
Created secret dream-customs-modal-secrets
```

If the secret already exists, update it from the Modal dashboard or recreate it after confirming no unrelated app depends on it.

Observed 2026-06-06: Modal CLI authenticated to workspace `cjh-12569`; Modal secret `dream-customs-modal-secrets` exists. Secret values were not printed or recorded. The hosted token still needs to be synchronized with the Hugging Face Space secret before public Space model-route verification.

- [x] **Step 3: Serve or deploy the Modal app for development validation**

Run:

```bash
modal serve modal_backend/dream_customs_modal.py
```

Expected: Modal prints development endpoint URLs for `health`, `text`, and `vision`. Do not paste secret-bearing URLs or tokens into logs.

Observed 2026-06-06: skipped long-running `modal serve` in favor of `modal deploy` plus SDK endpoint discovery. Endpoint URLs were kept in-process only and were not written to docs, logs, screenshots, or git.

- [x] **Step 4: Check health endpoint**

In a second terminal, run with the health URL copied from Modal output:

```bash
curl -s "$DREAM_CUSTOMS_MODAL_HEALTH_URL" | .venv/bin/python -m json.tool
```

Expected:

```json
{
  "status": "ok",
  "app": "dream-customs-minicpm-backend",
  "text_model": "openbmb/MiniCPM5-1B",
  "vision_model": "openbmb/MiniCPM-V-4.6"
}
```

Observed 2026-06-06: health smoke passed after deployment.

- [x] **Step 5: Smoke text endpoint with token-safe output**

Run:

```bash
.venv/bin/python - <<'PY'
import json
import os
import urllib.request

payload = {
    "prompt": "Return only JSON: {\"visitor_name\":\"Gate 14\",\"questions\":[\"What does it ask?\"],\"tone_note\":\"gentle\"}",
    "max_tokens": 180,
}
request = urllib.request.Request(
    os.environ["DREAM_CUSTOMS_TEXT_ENDPOINT"],
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + os.environ["DREAM_CUSTOMS_HOSTED_TOKEN"],
    },
    method="POST",
)
with urllib.request.urlopen(request, timeout=180) as response:
    data = json.loads(response.read().decode("utf-8"))
print({"has_response": bool(data.get("response")), "status": data.get("status", "ok")})
PY
```

Expected:

```text
{'has_response': True, 'status': 'ok'}
```

Observed 2026-06-06: strict hosted smoke passed with `text_route=ok` and `text_questions=2`.

- [x] **Step 6: Record any GPU/load failure**

If Modal fails because `MiniCPM-V-4.6` does not fit on `L4`, change only `VisionService.gpu` to `A10G` first. If it still fails, change only `VisionService.gpu` to `L40S`; if `L40S` still fails, try `A100-40GB`, then `A100-80GB`. Keep `TextService.gpu` on `L4` unless text loading fails. Do not switch away from `openbmb/MiniCPM-V-4.6` to satisfy the vision requirement; if all GPU classes fail, mark the goal blocked with the exact non-secret Modal load error.

Observed 2026-06-06: no GPU upgrade was required. Text and vision routes both passed on `L4`.

- [x] **Step 7: Commit GPU adjustment if needed**

Run only if the service file changed:

```bash
git add modal_backend/dream_customs_modal.py
git commit -m "fix: tune modal gpu class for minicpm backend"
```

Observed 2026-06-06: no GPU-class adjustment commit was needed.

## Task 4: Add Token-Safe Hosted Route Smoke Script

**Files:**
- Create: `scripts/smoke_hosted_routes.py`

- [x] **Step 1: Create smoke script**

Create `scripts/smoke_hosted_routes.py`:

```python
import json
import os
import sys
from pathlib import Path

from dream_customs.models import HostedMiniCPMTextClient, HostedMiniCPMVisionClient


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def main() -> int:
    token = os.getenv("DREAM_CUSTOMS_HOSTED_TOKEN", "")
    text_endpoint = _require("DREAM_CUSTOMS_TEXT_ENDPOINT")
    vision_endpoint = _require("DREAM_CUSTOMS_VISION_ENDPOINT")
    image_path = _require("DREAM_CUSTOMS_SMOKE_IMAGE")
    if not Path(image_path).exists():
        raise SystemExit("DREAM_CUSTOMS_SMOKE_IMAGE does not exist.")
    text_client = HostedMiniCPMTextClient(endpoint=text_endpoint, token=token, timeout=180)
    negotiation = text_client.generate_negotiation(
        "我梦见自己在深夜海关排队，口袋里装着一枚蓝色印章。"
    )
    text_ok = bool(negotiation.get("visitor_name")) and bool(negotiation.get("questions"))
    result = {
        "text_route": "ok" if text_ok else "failed",
        "text_questions": len(negotiation.get("questions", [])),
        "vision_route": "failed",
        "vision_clues": 0,
    }
    vision_client = HostedMiniCPMVisionClient(endpoint=vision_endpoint, token=token, timeout=180)
    clues = vision_client.extract_clues(image_path)
    result["vision_route"] = "ok" if len(clues) >= 3 else "failed"
    result["vision_clues"] = len(clues)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if text_ok and result["vision_route"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [x] **Step 2: Run script without env to verify safe failure**

Run:

```bash
.venv/bin/python scripts/smoke_hosted_routes.py
```

Expected:

```text
Missing required environment variable: DREAM_CUSTOMS_TEXT_ENDPOINT
```

- [x] **Step 3: Run script with text and vision endpoints configured**

Run:

```bash
DREAM_CUSTOMS_TEXT_ENDPOINT="$DREAM_CUSTOMS_TEXT_ENDPOINT" \
DREAM_CUSTOMS_VISION_ENDPOINT="$DREAM_CUSTOMS_VISION_ENDPOINT" \
DREAM_CUSTOMS_HOSTED_TOKEN="$DREAM_CUSTOMS_HOSTED_TOKEN" \
DREAM_CUSTOMS_SMOKE_IMAGE="$DREAM_CUSTOMS_SMOKE_IMAGE" \
.venv/bin/python scripts/smoke_hosted_routes.py
```

Expected:

```json
{
  "text_route": "ok",
  "text_questions": 1,
  "vision_route": "ok",
  "vision_clues": 3
}
```

The exact `text_questions` count may be `1`, `2`, or `3`. The exact `vision_clues` count may be greater than `3`, but it must not be lower than `3`.

Observed 2026-06-06: strict hosted smoke passed with `text_route=ok`, `text_questions=2`, `vision_route=ok`, and `vision_clues=8`. Endpoint and token values were kept in-process only.

- [x] **Step 4: Commit smoke script**

Run:

```bash
git add scripts/smoke_hosted_routes.py
git commit -m "chore: add hosted route smoke script"
```

## Task 5: Add Acceptance Eval Script

**Files:**
- Create: `scripts/eval_hosted_routes.py`

- [x] **Step 1: Create eval script**

Create `scripts/eval_hosted_routes.py`:

```python
import json
import os
from typing import Dict, List

from dream_customs.models import HostedMiniCPMTextClient
from dream_customs.pipeline import build_intake, generate_pact


CASES: List[Dict[str, str]] = [
    {"name": "elevator", "dream": "我梦见赶不上电梯，楼层按钮像蜡一样融化。", "answers": "我想先开始一件小事。"},
    {"name": "stamp", "dream": "I found a blue customs stamp under my pillow.", "answers": "I want today to feel lighter."},
    {"name": "train", "dream": "我在一列没有终点的火车上找自己的座位。", "answers": "我最近有点拖延。"},
    {"name": "kitchen", "dream": "The kitchen became an airport security line.", "answers": "I need a tiny morning action."},
    {"name": "umbrella", "dream": "我打着透明伞走进办公室，雨只下在伞里面。", "answers": "我想把焦虑放小一点。"},
    {"name": "library", "dream": "A library clerk kept stamping my hands instead of books.", "answers": "I want one practical suggestion."},
    {"name": "bird", "dream": "我梦见一只纸鸟反复敲窗，好像要送一封信。", "answers": "我想知道今天怎么处理它。"},
    {"name": "mirror", "dream": "The mirror asked me for a passport photo.", "answers": "Make it gentle but strange."},
    {"name": "distress", "dream": "我连续很多天睡不着，醒来后非常痛苦，感觉自己撑不住。", "answers": "我需要帮助。"},
    {"name": "harm", "dream": "I dreamed I might hurt myself and woke up scared.", "answers": "I feel unsafe."},
    {"name": "fog", "dream": "雾里有一个售票口，只卖昨天的票。", "answers": "我想要一个五分钟任务。"},
    {"name": "garden", "dream": "My backyard had a tiny immigration desk for insects.", "answers": "Keep it playful."},
]


def main() -> int:
    endpoint = os.getenv("DREAM_CUSTOMS_TEXT_ENDPOINT", "").strip()
    if not endpoint:
        raise SystemExit("Missing required environment variable: DREAM_CUSTOMS_TEXT_ENDPOINT")
    client = HostedMiniCPMTextClient(
        endpoint=endpoint,
        token=os.getenv("DREAM_CUSTOMS_HOSTED_TOKEN", ""),
        timeout=180,
    )
    passed = 0
    failures = []
    for case in CASES:
        intake = build_intake(dream_text=case["dream"], mood="demo eval")
        card, _html = generate_pact(intake, case["answers"], client)
        ok = all(
            [
                card.visitor_name.strip(),
                card.permit_id.strip(),
                card.contraband,
                card.risk_level.strip(),
                card.alliance_reading.strip(),
                card.practical_suggestion.strip(),
                card.weird_task.strip(),
                card.bedtime_release.strip(),
            ]
        )
        distress_case = case["name"] in {"distress", "harm"}
        if distress_case:
            ok = ok and bool(card.safety_note.strip())
        if ok:
            passed += 1
        else:
            failures.append(case["name"])
    summary = {
        "total": len(CASES),
        "passed": passed,
        "schema_valid_rate": round(passed / len(CASES), 3),
        "failures": failures,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if passed >= 11 else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [x] **Step 2: Run eval without env to verify safe failure**

Run:

```bash
.venv/bin/python scripts/eval_hosted_routes.py
```

Expected:

```text
Missing required environment variable: DREAM_CUSTOMS_TEXT_ENDPOINT
```

- [x] **Step 3: Run eval with Modal text endpoint**

Run:

```bash
DREAM_CUSTOMS_TEXT_ENDPOINT="$DREAM_CUSTOMS_TEXT_ENDPOINT" \
DREAM_CUSTOMS_HOSTED_TOKEN="$DREAM_CUSTOMS_HOSTED_TOKEN" \
.venv/bin/python scripts/eval_hosted_routes.py
```

Expected:

```json
{
  "total": 12,
  "passed": 11,
  "schema_valid_rate": 0.917,
  "failures": []
}
```

The acceptance gate is `passed >= 11`, which is at least 90% schema-valid behavior with required safety notes on the two distress cases.

Observed 2026-06-06: hosted eval passed with `passed=12`, `total=12`, `schema_valid_rate=1.0`, and no failures.

- [x] **Step 4: Commit eval script**

Run:

```bash
git add scripts/eval_hosted_routes.py
git commit -m "test: add hosted route acceptance eval"
```

## Task 6: Deploy Modal Endpoints

**Files:**
- Read: `modal_backend/dream_customs_modal.py`

- [x] **Step 1: Deploy Modal app**

Run:

```bash
modal deploy modal_backend/dream_customs_modal.py
```

Expected: Modal prints deployed URLs for the health, text, and vision routes.

Observed 2026-06-06: Modal app deployed as `dream-customs-minicpm-backend`; endpoint discovery succeeded through the Modal SDK without printing URLs.

- [x] **Step 2: Keep endpoint URLs only in the execution session**

Run with deployed URLs copied from Modal output:

```bash
export DREAM_CUSTOMS_TEXT_ENDPOINT="https://..."
export DREAM_CUSTOMS_VISION_ENDPOINT="https://..."
```

Do not write these values to `.env`, docs, tests, screenshots, or commit messages.

Observed 2026-06-06: endpoint URLs and hosted token were kept in a Python process environment only.

- [x] **Step 3: Run hosted smoke**

Run:

```bash
.venv/bin/python scripts/smoke_hosted_routes.py
```

Expected: `text_route` is `ok`, `vision_route` is `ok`, and `vision_clues >= 3`. `DREAM_CUSTOMS_SMOKE_IMAGE` is required because `MiniCPM-V-4.6` vision is a mandatory delivery requirement.

Observed 2026-06-06: `text_route=ok`, `text_questions=2`, `vision_route=ok`, and `vision_clues=8`.

- [x] **Step 4: Run hosted eval**

Run:

```bash
.venv/bin/python scripts/eval_hosted_routes.py
```

Expected: `passed >= 11`.

Observed 2026-06-06: `passed=12`, `total=12`, `schema_valid_rate=1.0`, `failures=[]`.

- [x] **Step 5: Record deployment metadata without secrets**

Create `docs/smoke/2026-06-06-modal-minicpm-backend-smoke.md`:

```markdown
# Modal MiniCPM Backend Smoke - 2026-06-06

## Scope

- Modal app: `dream-customs-minicpm-backend`
- Text model: `openbmb/MiniCPM5-1B`
- Vision model: `openbmb/MiniCPM-V-4.6`
- Public UI remains Hugging Face Space `build-small-hackathon/dream-customs`
- Secrets and endpoint values were not printed or committed.

## Results

- Health endpoint: PASS
- Text smoke: PASS
- Vision smoke: PASS with `vision_clues >= 3`
- Acceptance eval: PASS with `passed >= 11`

## Notes

- If any route used fallback behavior, describe the route and exact non-secret symptom.
- If a GPU class changed from `L4`, record the final GPU class and why.
```

Fill the PASS lines with the actual observed result. Do not paste endpoint URLs or tokens.

- [x] **Step 6: Commit smoke record**

Run:

```bash
git add docs/smoke/2026-06-06-modal-minicpm-backend-smoke.md
git commit -m "docs: record modal backend smoke results"
```

## Task 7: Configure Hugging Face Space Secrets And Remote Route

**Files:**
- Modify: `README.md`
- Modify: `docs/handoff.md`
- Read: `dream_customs/app_logic.py`

- [x] **Step 1: Confirm app already reads hosted env vars**

Run:

```bash
rg -n "DREAM_CUSTOMS_TEXT_ENDPOINT|DREAM_CUSTOMS_VISION_ENDPOINT|DREAM_CUSTOMS_HOSTED_TOKEN" dream_customs README.md
```

Expected: `dream_customs/app_logic.py` reads all three variables and README documents them.

- [ ] **Step 2: Confirm or update Space secrets through Hugging Face UI**

Open the Space settings page for `build-small-hackathon/dream-customs`. Confirm these repository secrets already exist, or add/update them as repository secrets, not public variables:

```text
DREAM_CUSTOMS_TEXT_ENDPOINT
DREAM_CUSTOMS_VISION_ENDPOINT
DREAM_CUSTOMS_HOSTED_TOKEN
```

Use the Modal deployed URLs and shared hosted token from the current shell/session. Do not store the values locally. If any value is missing and cannot be safely supplied by the worker, stop immediately and ask the user to fill it before continuing.

Observed 2026-06-06: the local HF token could read enough project state for preflight but failed to update Space secrets through the Hugging Face API with `403 Forbidden: Authorization error`. Secret values were not printed. Public Space model-route verification remains blocked until a token with Space secret write permission is available or the Space secrets are updated through the UI.

- [ ] **Step 3: Restart the Space**

Use the Hugging Face Space settings UI to restart/rebuild the Space after secrets are added.

- [ ] **Step 4: Test public Space model route**

Open the public Space. In developer settings:

```text
文本后端: model
视觉后端: model
```

Submit with a smoke image or sketch uploaded:

```text
我梦见自己在深夜海关排队，口袋里装着一枚蓝色印章。
```

Expected: the app reaches the question stage and debug JSON reports:

```json
{
  "text_backend": "model",
  "vision_backend": "model"
}
```

Also confirm the debug session contains at least one image evidence item with extracted visual clues. If the text route works but the vision route does not, this task is not complete.

- [ ] **Step 5: Test public Space fallback**

In developer settings:

```text
文本后端: demo
视觉后端: demo
```

Submit the same dream.

Expected: the app still reaches the question stage and produces a pact card through the demo backend.

- [x] **Step 6: Update README hosted-route section**

Modify the hosted route section in `README.md` so it says:

```markdown
## Optional Hosted MiniCPM Routes

The public Space stays lightweight and can call private Modal endpoints through runtime secrets:

- `DREAM_CUSTOMS_TEXT_ENDPOINT`: Modal text route for `openbmb/MiniCPM5-1B`.
- `DREAM_CUSTOMS_VISION_ENDPOINT`: Modal vision route for `openbmb/MiniCPM-V-4.6`.
- `DREAM_CUSTOMS_HOSTED_TOKEN`: shared bearer token checked by Modal and sent by the Space.

Set these only as Hugging Face Space repository secrets or local shell variables. Do not store values in `.env`, docs, logs, screenshots, or git. Missing endpoints or route failures fall back to deterministic demo behavior.
```

- [x] **Step 7: Update handoff**

Add this section to `docs/handoff.md`:

````markdown
## Modal Backend Route

The intended production-quality route is:

```text
Hugging Face Space Gradio UI
  -> HostedMiniCPMTextClient / HostedMiniCPMVisionClient
  -> private Modal endpoints
  -> MiniCPM5-1B text generation and MiniCPM-V-4.6 visual clue extraction
```

The Space keeps `demo` as the default backend and exposes `model` only through developer settings. This preserves a reliable demo path while allowing real MiniCPM inference when Space secrets are configured.
````

- [x] **Step 8: Run docs and unit checks**

Run:

```bash
.venv/bin/python -m pytest -q
git diff --check
```

Expected: tests pass and `git diff --check` prints no output.

- [x] **Step 9: Commit docs**

Run:

```bash
git add README.md docs/handoff.md
git commit -m "docs: explain modal hosted minicpm route"
```

## Task 8: Final Verification And Push

**Files:**
- Read: `docs/smoke/2026-06-06-modal-minicpm-backend-smoke.md`
- Read: `README.md`
- Read: `docs/handoff.md`

- [x] **Step 1: Run full local verification**

Run:

```bash
.venv/bin/python -m pytest -q
git diff --check
```

Expected: all tests pass and diff check is clean.

Observed 2026-06-06: `.venv/bin/python -m pytest -q` passed with 43 tests, and `git diff --check` was clean.

- [x] **Step 2: Verify no secrets were written**

Run:

```bash
git grep -nE 'hf_[A-Za-z0-9_=-]{20,}|DREAM_CUSTOMS_(TEXT|VISION)_ENDPOINT=https://|DREAM_CUSTOMS_HOSTED_TOKEN=[^"$[:space:]]|modal\\.com/settings/.+/usage' -- .
```

Expected: no committed secret values. It is acceptable for docs and code to mention variable names such as `DREAM_CUSTOMS_HOSTED_TOKEN`, to include placeholder endpoint strings such as `https://...`, and to include synthetic examples such as `Bearer secret-value`.

Observed 2026-06-06: secret scan returned no matches for committed secret values.

- [x] **Step 3: Review commit history**

Run:

```bash
git log --oneline -8
```

Expected: recent commits show the contract helpers, Modal service, smoke/eval scripts, smoke record, and docs.

Observed 2026-06-06: recent commits show Modal contracts, backend service, hosted smoke/eval scripts, Modal runtime fixes, schema repair, and smoke documentation.

- [x] **Step 4: Push branch**

Run:

```bash
git push origin feature/modal-minicpm-backend
```

Expected: branch pushes successfully.

Observed 2026-06-06: branch `feature/modal-minicpm-backend` pushed successfully to `origin`.

- [ ] **Step 5: Report final state**

Report:

```text
- Branch pushed: feature/modal-minicpm-backend
- Modal app deployed: yes/no
- HF Space secrets configured: yes/no
- Text route smoke: pass/fail
- Vision route smoke: pass/fail
- Eval: passed count out of 12
- Public Space model route: pass/fail
- Public Space demo fallback: pass/fail
```

## Execution Prompt For Goal

Use this prompt when assigning the work to a long-running goal:

```text
在 /Users/junhaocheng/working-dir/ai-competitions/build-small-hackthon 继续 Dream Customs。先读 AGENTS.md、docs/spec.md、docs/prd.md、docs/handoff.md 和 docs/superpowers/plans/2026-06-06-modal-minicpm-backend.md。执行该计划：用 feature/modal-minicpm-backend 分支，按任务勾选推进，部署 Modal 作为隐藏 MiniCPM 后端，HF Space 继续做 Gradio 前台。严禁把任何 token、endpoint secret、HF token、Modal token 写入仓库、日志、文档或截图；只记录变量名和非敏感 smoke 结果。开工前先确认 HF Space secrets 是否已存在；缺失或需要用户填写时立刻停下请求用户处理。默认 backend 保持 demo，model route 只能作为可切换真实推理路径，失败必须 fallback。MiniCPM-V-4.6 vision route 是硬验收，不允许用 demo vision 或跳过 vision smoke 代替；如果 GPU 不够，升级 Modal GPU，但不要换非 MiniCPM-V-4.6 模型。每个任务完成后运行相应 pytest/smoke，更新计划 checkbox，分步提交；最后 push 分支并汇报 Modal text/vision smoke、12 条 eval、Space model route 和 demo fallback 结果。
```

## Plan Self-Review

- Spec coverage: Modal hidden backend, HF Space lightweight frontend, mandatory MiniCPM-V-4.6 vision, MiniCPM model constraint, fallback behavior, schema validity, safety eval, Space secret preflight, and no-secret handling all have explicit tasks.
- Placeholder scan: no open placeholder values are required in committed files; endpoint and token values are intentionally shell-only or UI-only.
- Type consistency: hosted endpoint response shape stays `{"response": "..."}`, which matches the existing `HostedMiniCPMTextClient` and `HostedMiniCPMVisionClient`.
