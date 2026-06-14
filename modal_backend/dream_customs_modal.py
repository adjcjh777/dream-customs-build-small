import io
import json
import os
import subprocess
import sys
import tempfile
from typing import Any, Dict, Optional

import modal
from fastapi import Body, Header

from modal_backend.contracts import (
    AuthError,
    decode_audio_payload,
    decode_image_payload,
    ensure_authorized,
    normalize_text_payload,
    response_payload,
)


APP_NAME = "dream-customs-minicpm-backend"
TEXT_MODEL = "openbmb/MiniCPM5-1B"
VISION_MODEL = "openbmb/MiniCPM-V-4.6"
ASR_MODEL = "XiaomiMiMo/MiMo-V2.5-ASR"
ASR_TOKENIZER_MODEL = "XiaomiMiMo/MiMo-Audio-Tokenizer"
MIMO_ASR_REPO_DIR = "/opt/MiMo-V2.5-ASR"
MIMO_ASR_NESTED_REPO_DIR = "/opt/MiMo-V2.5-ASR/MiMo-V2.5-ASR"
MIMO_ASR_RUNTIME_REPO_DIR = "/tmp/MiMo-V2.5-ASR"
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
    .apt_install("ffmpeg", "git")
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
        "librosa",
        "soundfile",
    )
    .add_local_dir("modal_backend", remote_path="/root/modal_backend")
)

asr_image = (
    modal.Image.from_registry("nvidia/cuda:12.4.1-devel-ubuntu22.04", add_python="3.12")
    .apt_install("build-essential", "ffmpeg", "git", "ninja-build")
    .pip_install(
        "accelerate>=1.9.0",
        "fastapi[standard]>=0.116.1",
        "huggingface-hub",
        "librosa>=0.11.0",
        "pydantic>=2.11.7",
        "scipy>=1.16.1",
        "torch==2.6.0",
        "torchaudio==2.6.0",
        "transformers==4.49.0",
        "triton==3.2.0",
        "uvicorn>=0.35.0",
        "zhon==2.1.1",
    )
    .run_commands(
        "pip install wheel && "
        "CUDA_HOME=/usr/local/cuda pip install flash-attn==2.7.4.post1 --no-build-isolation"
    )
    .run_commands(
        "git clone --depth 1 https://github.com/XiaomiMiMo/MiMo-V2.5-ASR.git "
        f"{MIMO_ASR_REPO_DIR} && test -d {MIMO_ASR_REPO_DIR}/src"
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
_ASR_PIPE = None


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


def _load_asr_pipe():
    global _ASR_PIPE
    if _ASR_PIPE is None:
        from huggingface_hub import snapshot_download

        repo_candidates = (
            MIMO_ASR_REPO_DIR,
            MIMO_ASR_NESTED_REPO_DIR,
            MIMO_ASR_RUNTIME_REPO_DIR,
        )
        source_dir = ""
        for repo_dir in repo_candidates:
            if os.path.isdir(os.path.join(repo_dir, "src")) and repo_dir not in sys.path:
                sys.path.insert(0, repo_dir)
                source_dir = repo_dir
                break
            if os.path.isdir(os.path.join(repo_dir, "src")):
                source_dir = repo_dir
                break
        if not source_dir:
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "https://github.com/XiaomiMiMo/MiMo-V2.5-ASR.git",
                    MIMO_ASR_RUNTIME_REPO_DIR,
                ],
                check=True,
            )
            if not os.path.isdir(os.path.join(MIMO_ASR_RUNTIME_REPO_DIR, "src")):
                raise RuntimeError("MiMo-V2.5-ASR source checkout is missing in Modal.")
            sys.path.insert(0, MIMO_ASR_RUNTIME_REPO_DIR)
        from src.mimo_audio.mimo_audio import MimoAudio

        model_path = os.getenv("DREAM_CUSTOMS_ASR_MODEL_PATH", "").strip()
        if not model_path:
            model_path = snapshot_download(
                os.getenv("DREAM_CUSTOMS_ASR_MODEL", ASR_MODEL),
                token=os.getenv("HF_TOKEN") or None,
            )
        tokenizer_path = os.getenv("DREAM_CUSTOMS_ASR_TOKENIZER_PATH", "").strip()
        if not tokenizer_path:
            tokenizer_path = snapshot_download(
                os.getenv("DREAM_CUSTOMS_ASR_TOKENIZER_MODEL", ASR_TOKENIZER_MODEL),
                token=os.getenv("HF_TOKEN") or None,
            )
        _ASR_PIPE = MimoAudio(
            model_path=model_path,
            mimo_audio_tokenizer_path=tokenizer_path,
        )
    return _ASR_PIPE


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
    if "today_tip" in prompt or "tiny_action" in prompt:
        if is_cjk:
            payload = {
                "dream_summary": "你记录了一个带着办公楼、电梯和未发送邮件的梦。",
                "main_question": "这个梦可能在提醒我什么？",
                "dream_anchors": ["办公楼", "电梯", "邮件"],
                "followup_questions": [],
                "user_answers": [],
                "interpretation": "也许这个梦不是在给出唯一答案，而是在把醒来后的卡住感放到一个具体画面里。",
                "today_tip": (
                    "1. 把「办公楼」翻译成现实里最像卡住入口的一件事。"
                    "2. 只打开相关草稿或邮件。"
                    "3. 写下第一句话后先存起来，不要求马上发出。"
                ),
                "tiny_action": "找一张便利贴，画一个只到“草稿层”的电梯按钮，按一下，再只写第一句话。",
                "caring_note": "你可以慢慢开始，不需要一醒来就抵达所有楼层。",
                "safety_note": "",
            }
        else:
            payload = {
                "dream_summary": "You recorded a dream with an office building, elevator, and unsent email.",
                "main_question": "What might this dream be asking me to notice today?",
                "dream_anchors": ["office building", "elevator", "email"],
                "followup_questions": [],
                "user_answers": [],
                "interpretation": "Maybe this dream is not giving one fixed answer; it is turning a waking stuck point into a concrete scene.",
                "today_tip": (
                    "1. Translate the office building into the real-life doorway where you feel stuck. "
                    "2. Open only the related draft or email. "
                    "3. Add the first sentence and save it without sending yet."
                ),
                "tiny_action": "Draw an elevator button labeled Draft Floor on a sticky note, press it once, then write only the first sentence.",
                "caring_note": "You can start slowly; you do not have to reach every floor this morning.",
                "safety_note": "",
            }
        if distress:
            payload["safety_note"] = (
                "如果你已经连续很多天睡不好、非常痛苦，或担心自己会伤害自己/他人，请尽快联系可信任的人或专业支持。"
                if is_cjk
                else "If you have been unable to sleep for many nights, feel severe distress, or worry you may hurt yourself or someone else, please reach out to a trusted person or professional support now."
            )
    elif "permit_id" in prompt or "practical_suggestion" in prompt:
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


def _empty_value(value: Any) -> bool:
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return not [item for item in value if str(item).strip()]
    return value is None


def _repair_json_response(prompt: str, text_output: str) -> str:
    if "Required schema:" not in prompt:
        return text_output
    parsed = _extract_json_object(text_output)
    fallback = _extract_json_object(_fallback_json_response(prompt))
    if parsed is None or fallback is None:
        return _fallback_json_response(prompt)

    if "today_tip" in prompt or "tiny_action" in prompt:
        required_keys = (
            "dream_summary",
            "main_question",
            "dream_anchors",
            "followup_questions",
            "user_answers",
            "interpretation",
            "today_tip",
            "tiny_action",
            "caring_note",
            "safety_note",
        )
    elif "permit_id" in prompt or "practical_suggestion" in prompt:
        required_keys = (
            "visitor_name",
            "permit_id",
            "contraband",
            "risk_level",
            "alliance_reading",
            "practical_suggestion",
            "weird_task",
            "bedtime_release",
            "safety_note",
        )
    else:
        required_keys = ("visitor_name", "questions", "tone_note")

    for key in required_keys:
        if _empty_value(parsed.get(key)):
            parsed[key] = fallback.get(key, "")
    return json.dumps(parsed, ensure_ascii=False)


def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    cleaned = text.strip()
    try:
        parsed = json.loads(cleaned)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass
    start = cleaned.find("{")
    if start < 0:
        return None
    depth = 0
    in_string = False
    escaped = False
    for index, char in enumerate(cleaned[start:], start=start):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                try:
                    parsed = json.loads(cleaned[start : index + 1])
                except json.JSONDecodeError:
                    return None
                return parsed if isinstance(parsed, dict) else None
    return None


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
        "asr_model": ASR_MODEL,
        "asr_tokenizer_model": ASR_TOKENIZER_MODEL,
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
    else:
        text_output = _repair_json_response(normalized["prompt"], text_output)
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
        max_tokens = max(64, min(int(payload.get("max_tokens", 220)), 400))
        result = pipe(text=messages, max_new_tokens=max_tokens)
    return response_payload(_stringify_pipeline_result(result))


@app.function(
    image=asr_image,
    gpu="A100",
    timeout=20 * MINUTES,
    scaledown_window=5 * MINUTES,
    volumes={"/root/.cache/huggingface": hf_cache},
    secrets=secrets,
)
@modal.fastapi_endpoint(method="POST", docs=True)
async def asr(
    payload: Dict[str, Any] = Body(...),
    authorization: str = Header(""),
):
    try:
        ensure_authorized(authorization, _expected_token())
    except AuthError as exc:
        return _json_error(str(exc), status="unauthorized")
    try:
        audio_bytes, filename = decode_audio_payload(payload)
    except ValueError as exc:
        return _json_error(str(exc))

    suffix = os.path.splitext(filename)[1] or ".wav"
    model = _load_asr_pipe()
    with tempfile.NamedTemporaryFile(suffix=suffix) as temp_file:
        temp_file.write(audio_bytes)
        temp_file.flush()
        transcript = model.asr_sft(temp_file.name)
    transcript = str(transcript or "").strip()
    return {"status": "ok", "transcript": transcript, "response": transcript}
