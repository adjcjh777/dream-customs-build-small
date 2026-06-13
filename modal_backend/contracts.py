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
    temperature = payload.get("temperature", 0.0)
    try:
        temperature = float(temperature)
    except (TypeError, ValueError):
        temperature = 0.0
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


def decode_audio_payload(payload: Dict[str, Any]) -> tuple[bytes, str]:
    encoded = payload.get("audio")
    if not encoded and isinstance(payload.get("audios"), list) and payload["audios"]:
        encoded = payload["audios"][0]
    if not encoded:
        raise ValueError("Missing audio payload.")
    if isinstance(encoded, bytes):
        encoded = encoded.decode("ascii")
    filename = _clean_text(payload.get("filename")) or "dream-voice.wav"
    return base64.b64decode(str(encoded)), filename


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
