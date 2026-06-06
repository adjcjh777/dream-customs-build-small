import io
import os
import tempfile
from typing import Any, Dict

import modal
from fastapi import Body, Header

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

health_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("fastapi[standard]")
    .add_local_dir("modal_backend", remote_path="/root/modal_backend")
)

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
    .add_local_dir("modal_backend", remote_path="/root/modal_backend")
)

secrets = [
    modal.Secret.from_name(
        "dream-customs-modal-secrets",
        required_keys=["HF_TOKEN", "DREAM_CUSTOMS_HOSTED_TOKEN"],
    )
]

_TEXT_PIPE = None
_VISION_PIPE = None


def _expected_token() -> str:
    return os.getenv("DREAM_CUSTOMS_HOSTED_TOKEN", "").strip()


def _json_error(message: str, status: str = "error") -> Dict[str, str]:
    return {"status": status, "response": "", "error": message}


def _stringify_pipeline_result(result: Any) -> str:
    if isinstance(result, str):
        return result.strip()
    if isinstance(result, list) and result:
        return _stringify_pipeline_result(result[0])
    if isinstance(result, dict):
        for key in ("generated_text", "text", "output", "response"):
            value = result.get(key)
            if isinstance(value, str):
                return value.strip()
        return str(result).strip()
    return str(result).strip()


def _load_text_pipe():
    global _TEXT_PIPE
    if _TEXT_PIPE is None:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        model_id = os.getenv("DREAM_CUSTOMS_TEXT_MODEL", TEXT_MODEL)
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            torch_dtype="auto",
            trust_remote_code=True,
        )
        _TEXT_PIPE = (tokenizer, model)
    return _TEXT_PIPE


def _load_vision_pipe():
    global _VISION_PIPE
    if _VISION_PIPE is None:
        from transformers import pipeline

        _VISION_PIPE = pipeline(
            "image-text-to-text",
            model=os.getenv("DREAM_CUSTOMS_VISION_MODEL", VISION_MODEL),
            device_map="auto",
            torch_dtype="auto",
            trust_remote_code=True,
        )
    return _VISION_PIPE


def _messages_from_payload(payload: Dict[str, Any], prompt: str) -> list[Dict[str, str]]:
    messages = payload.get("messages")
    if isinstance(messages, list) and messages:
        cleaned = []
        for item in messages:
            if isinstance(item, dict) and item.get("content"):
                cleaned.append(
                    {
                        "role": str(item.get("role") or "user"),
                        "content": str(item.get("content")),
                    }
                )
        if cleaned:
            return cleaned
    return [{"role": "user", "content": prompt}]


@app.function(image=health_image)
@modal.fastapi_endpoint(method="GET", docs=True)
def health() -> Dict[str, str]:
    return {
        "status": "ok",
        "app": APP_NAME,
        "text_model": TEXT_MODEL,
        "vision_model": VISION_MODEL,
    }


@app.function(
    image=image,
    gpu="L4",
    timeout=10 * MINUTES,
    scaledown_window=5 * MINUTES,
    volumes={"/root/.cache/huggingface": hf_cache},
    secrets=secrets,
)
@modal.fastapi_endpoint(method="POST", docs=True)
async def text(
    payload: Dict[str, Any] = Body(...),
    authorization: str = Header(""),
):
    try:
        ensure_authorized(authorization, _expected_token())
    except AuthError as exc:
        return _json_error(str(exc), status="unauthorized")
    normalized = normalize_text_payload(payload)
    if not normalized["prompt"]:
        return _json_error("Missing prompt.")
    tokenizer, model = _load_text_pipe()
    messages = _messages_from_payload(payload, normalized["prompt"])
    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        enable_thinking=False,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=normalized["max_tokens"],
        do_sample=normalized["temperature"] > 0,
        temperature=max(normalized["temperature"], 0.01),
    )
    generated = outputs[0][inputs["input_ids"].shape[-1] :]
    text_output = tokenizer.decode(generated, skip_special_tokens=True)
    return response_payload(text_output.strip())


@app.function(
    image=image,
    gpu="L4",
    timeout=10 * MINUTES,
    scaledown_window=5 * MINUTES,
    volumes={"/root/.cache/huggingface": hf_cache},
    secrets=secrets,
)
@modal.fastapi_endpoint(method="POST", docs=True)
async def vision(
    payload: Dict[str, Any] = Body(...),
    authorization: str = Header(""),
):
    try:
        ensure_authorized(authorization, _expected_token())
    except AuthError as exc:
        return _json_error(str(exc), status="unauthorized")
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

    pipe = _load_vision_pipe()
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
        result = pipe(text=messages, max_new_tokens=int(payload.get("max_tokens", 320)))
    return response_payload(_stringify_pipeline_result(result))
