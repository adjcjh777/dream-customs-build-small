import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
