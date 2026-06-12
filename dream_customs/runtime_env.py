import json
import os
from pathlib import Path


SPACE_ID = "build-small-hackathon/dream-customs"
DEFAULT_RUNTIME_ENV_JSON = Path("/tmp/dream-customs-runtime.json")
RUNTIME_ENV_KEYS = {
    "DREAM_CUSTOMS_TEXT_ENDPOINT",
    "DREAM_CUSTOMS_VISION_ENDPOINT",
    "DREAM_CUSTOMS_ASR_ENDPOINT",
    "DREAM_CUSTOMS_HOSTED_TOKEN",
}


def runtime_env_json_path() -> Path:
    return Path(os.getenv("DREAM_CUSTOMS_RUNTIME_ENV_JSON", str(DEFAULT_RUNTIME_ENV_JSON)))


def _runtime_env_autoload_enabled() -> bool:
    value = os.getenv("DREAM_CUSTOMS_DISABLE_RUNTIME_ENV_JSON", "").strip().lower()
    return value not in {"1", "true", "yes", "on"}


def load_runtime_env_json(path: Path) -> dict:
    if not path.exists():
        return {"loaded": False, "path": str(path), "reason": "missing"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"loaded": False, "path": str(path), "reason": exc.__class__.__name__}

    loaded_keys = []
    for key in sorted(RUNTIME_ENV_KEYS):
        value = str(data.get(key, "")).strip()
        if value:
            os.environ[key] = value
            loaded_keys.append(key)
    return {
        "loaded": bool(loaded_keys),
        "path": str(path),
        "configured_keys": loaded_keys,
    }


def auto_load_runtime_env_json() -> dict:
    if not _runtime_env_autoload_enabled():
        return {"loaded": False, "reason": "disabled"}
    if os.getenv("PYTEST_CURRENT_TEST") and not os.getenv("DREAM_CUSTOMS_RUNTIME_ENV_JSON"):
        return {"loaded": False, "reason": "pytest"}
    return load_runtime_env_json(runtime_env_json_path())


def configured_env(space_id: str = SPACE_ID) -> dict:
    return {
        "space_id": os.getenv("SPACE_ID", space_id),
        "text_endpoint_configured": bool(os.getenv("DREAM_CUSTOMS_TEXT_ENDPOINT", "").strip()),
        "vision_endpoint_configured": bool(os.getenv("DREAM_CUSTOMS_VISION_ENDPOINT", "").strip()),
        "asr_endpoint_configured": bool(os.getenv("DREAM_CUSTOMS_ASR_ENDPOINT", "").strip()),
        "hosted_token_configured": bool(os.getenv("DREAM_CUSTOMS_HOSTED_TOKEN", "").strip()),
    }
