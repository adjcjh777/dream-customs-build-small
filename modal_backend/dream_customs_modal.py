import io
import os
import tempfile
from typing import Any, Dict

import modal
from fastapi import Request

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


def _auth_header(request: Any) -> str:
    return str(request.headers.get("authorization", ""))


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


@app.function(image=health_image)
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
    async def text(self, request: Request):
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
        return response_payload(_stringify_pipeline_result(output))


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
    async def vision(self, request: Request):
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
        return response_payload(_stringify_pipeline_result(result))
