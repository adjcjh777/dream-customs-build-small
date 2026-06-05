import json
import os
from typing import Any, Tuple

from dream_customs.models import (
    FakeASRClient,
    FakeTextClient,
    FakeVisionClient,
    OllamaTextClient,
    OllamaVisionClient,
)
from dream_customs.pipeline import generate_negotiation, generate_pact, intake_from_modalities


DEFAULT_TEXT_MODEL = "hf.co/openbmb/MiniCPM5-1B-GGUF:Q8_0"
DEFAULT_VISION_MODEL = "openbmb/minicpm-v4.6"


def _file_path(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return str(value.get("path") or value.get("name") or "")
    if isinstance(value, (list, tuple)) and value:
        return _file_path(value[0])
    return ""


def _clients(text_backend: str, vision_backend: str):
    text_backend = (text_backend or "demo").lower()
    vision_backend = (vision_backend or "demo").lower()
    if text_backend == "ollama":
        text_client = OllamaTextClient(
            model_name=os.getenv("DREAM_CUSTOMS_TEXT_MODEL", DEFAULT_TEXT_MODEL),
            base_url=os.getenv("DREAM_CUSTOMS_OLLAMA_URL", "http://localhost:11434"),
        )
    else:
        text_client = FakeTextClient()

    if vision_backend == "ollama":
        vision_client = OllamaVisionClient(
            model_name=os.getenv("DREAM_CUSTOMS_VISION_MODEL", DEFAULT_VISION_MODEL),
            base_url=os.getenv("DREAM_CUSTOMS_OLLAMA_URL", "http://localhost:11434"),
        )
    else:
        vision_client = FakeVisionClient()

    return text_client, vision_client, FakeASRClient()


def run_customs_once(
    dream_text: str,
    image_value: Any = None,
    audio_value: Any = None,
    mood: str = "",
    answers: str = "",
    text_backend: str = "demo",
    vision_backend: str = "demo",
) -> Tuple[str, str, str, str]:
    image_path = _file_path(image_value)
    audio_path = _file_path(audio_value)
    if not any([dream_text and dream_text.strip(), image_path, audio_path]):
        return (
            "No declaration received.",
            "Please add text, an image, or a voice note before requesting clearance.",
            "",
            json.dumps({"status": "empty"}, ensure_ascii=False, indent=2),
        )

    text_client, vision_client, asr_client = _clients(text_backend, vision_backend)
    intake = intake_from_modalities(
        dream_text=dream_text or "",
        image_path=image_path or None,
        audio_path=audio_path or None,
        mood=mood or "",
        vision_client=vision_client,
        asr_client=asr_client,
    )
    negotiation = generate_negotiation(intake, text_client)
    answer_text = answers or "The user has not answered yet; infer a gentle pact from the declaration."
    card, html = generate_pact(intake, answer_text, text_client)
    questions = "\n".join(f"{index}. {question}" for index, question in enumerate(negotiation["questions"], start=1))
    negotiation_text = "\n".join(
        part
        for part in [
            f"Visitor: {negotiation['visitor_name']}",
            questions,
            negotiation.get("tone_note", ""),
        ]
        if part
    )
    debug = {
        "status": "ok",
        "text_backend": text_backend,
        "vision_backend": vision_backend,
        "intake": intake.model_dump(),
        "negotiation": negotiation,
        "pact": card.model_dump(),
    }
    return negotiation_text, card.to_plain_text(), html, json.dumps(debug, ensure_ascii=False, indent=2)
