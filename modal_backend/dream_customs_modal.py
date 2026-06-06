import io
import json
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


def _contains_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def _fallback_json_response(prompt: str) -> str:
    is_cjk = _contains_cjk(prompt)
    distress = any(
        term in prompt.lower()
        for term in ("hurt myself", "self-harm", "unsafe", "撑不住", "很多天睡不着", "痛苦")
    )
    if "permit_id" in prompt or "practical_suggestion" in prompt:
        if is_cjk:
            payload: Dict[str, Any] = {
                "visitor_name": "蓝色放行章",
                "permit_id": "DC-MODAL-001",
                "contraband": ["未申报的焦虑", "一枚需要被看见的印章"],
                "risk_level": "橙色：需要被安置，但不需要被害怕",
                "alliance_reading": "这个梦也许在提醒你，今天先把不安放进一个更小、更可处理的动作里。",
                "practical_suggestion": "先打开一件最小任务，只做五分钟，然后停下来喝水。",
                "weird_task": "给梦里的海关写一句放行批注：今日只检查一件小事。",
                "bedtime_release": "今日梦境已盖章，未完成事项明日再报关。",
                "safety_note": "",
            }
        else:
            payload = {
                "visitor_name": "Blue Release Stamp",
                "permit_id": "DC-MODAL-001",
                "contraband": ["unfiled worry", "one stamp asking to be noticed"],
                "risk_level": "orange: needs placement, not fear",
                "alliance_reading": "This dream may be asking you to place the worry inside one smaller action today.",
                "practical_suggestion": "Open one tiny task for five minutes, then stop and drink water.",
                "weird_task": "Write one customs note for the dream: today only one small thing is inspected.",
                "bedtime_release": "Today's dream has been stamped; unfinished items report tomorrow.",
                "safety_note": "",
            }
        if distress:
            payload["safety_note"] = (
                "This dream sounds heavier than a playful customs ritual should handle. "
                "If you feel unsafe, cannot sleep for many nights, or worry you may hurt yourself or someone else, "
                "please reach out to a trusted person or professional support now."
            )
    else:
        payload = {
            "visitor_name": "蓝色放行章" if is_cjk else "Blue Release Stamp",
            "questions": (
                [
                    "这枚印章今天想替你放行哪一件小事？",
                    "如果只做五分钟，哪一步已经足够？",
                ]
                if is_cjk
                else [
                    "What small thing does this stamp want to release today?",
                    "If five minutes is enough, which first step counts?",
                ]
            ),
            "tone_note": (
                "这个来访者也许是在帮你把梦里的紧张变成一个更小的动作。"
                if is_cjk
                else "This visitor may be turning dream tension into one smaller action."
            ),
        }
    return json.dumps(payload, ensure_ascii=False)


def _generate_text(
    tokenizer: Any,
    model: Any,
    messages: list[Dict[str, str]],
    max_tokens: int,
) -> str:
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
        max_new_tokens=max_tokens,
        do_sample=False,
    )
    generated = outputs[0][inputs["input_ids"].shape[-1] :]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()


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
    text_output = _generate_text(tokenizer, model, messages, normalized["max_tokens"])
    if not text_output:
        retry_messages = [
            {
                "role": "user",
                "content": (
                    "Return one compact valid JSON object only. "
                    "Use the exact schema requested in this task and do not add markdown.\n\n"
                    f"Task:\n{normalized['prompt']}"
                ),
            }
        ]
        text_output = _generate_text(tokenizer, model, retry_messages, normalized["max_tokens"])
    if not text_output:
        text_output = _fallback_json_response(normalized["prompt"])
    return response_payload(text_output)


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
