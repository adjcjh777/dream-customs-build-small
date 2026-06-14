import json
import os
import sys
import tempfile
import time
import wave
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dream_customs.models import HostedASRClient, HostedMiniCPMTextClient, HostedMiniCPMVisionClient
from dream_customs.prompts import negotiation_prompt, today_tip_prompt
from dream_customs.pipeline import build_intake, build_qa_state
from dream_customs.schema import TodayTipCard


class TextFallback:
    def generate_negotiation(self, _prompt: str) -> dict[str, Any]:
        return {"visitor_name": "fallback", "questions": ["fallback"], "tone_note": "fallback"}

    def generate_today_tip(self, _prompt: str) -> TodayTipCard:
        return TodayTipCard(
            dream_summary="fallback",
            main_question="fallback",
            dream_anchors=["fallback"],
            followup_questions=[],
            user_answers=[],
            interpretation="fallback",
            today_tip="fallback",
            tiny_action="fallback",
            caring_note="fallback",
            safety_note="",
        )


class VisionFallback:
    def extract_clues(self, _image_path: str) -> list[str]:
        return ["fallback"]

    def extract_witness(self, _image_path: str):
        raise RuntimeError("fallback witness should not be used in this benchmark")


class ASRFallback:
    def transcribe(self, _audio_path: str) -> str:
        return "fallback"


def _measure(name: str, fn: Callable[[], Any]) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        value = fn()
        ok = True
        error = ""
    except Exception as exc:  # pragma: no cover - benchmark safety net
        value = None
        ok = False
        error = exc.__class__.__name__
    elapsed = time.perf_counter() - start
    return {
        "name": name,
        "ok": ok,
        "elapsed_seconds": round(elapsed, 3),
        "fallback": _looks_like_fallback(value),
        "error": error,
    }


def _looks_like_fallback(value: Any) -> bool:
    if isinstance(value, dict):
        return value.get("visitor_name") == "fallback"
    if isinstance(value, TodayTipCard):
        return value.dream_summary == "fallback"
    if isinstance(value, list):
        return value == ["fallback"]
    return value == "fallback"


def _write_probe_wav() -> str:
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp.close()
    with wave.open(temp.name, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\x00\x00" * 1600)
    return temp.name


def main() -> int:
    token = os.getenv("DREAM_CUSTOMS_HOSTED_TOKEN", "")
    text_endpoint = os.getenv("DREAM_CUSTOMS_TEXT_ENDPOINT", "").strip()
    vision_endpoint = os.getenv("DREAM_CUSTOMS_VISION_ENDPOINT", "").strip()
    asr_endpoint = os.getenv("DREAM_CUSTOMS_ASR_ENDPOINT", "").strip()
    image_path = os.getenv("DREAM_CUSTOMS_SMOKE_IMAGE", "").strip()
    audio_path = os.getenv("DREAM_CUSTOMS_SMOKE_AUDIO", "").strip()

    text_timeout = float(os.getenv("DREAM_CUSTOMS_BENCH_TEXT_TIMEOUT", "9"))
    vision_timeout = float(os.getenv("DREAM_CUSTOMS_BENCH_VISION_TIMEOUT", "9"))
    asr_timeout = float(os.getenv("DREAM_CUSTOMS_BENCH_ASR_TIMEOUT", "9"))
    text_budget = int(float(os.getenv("DREAM_CUSTOMS_BENCH_TEXT_BUDGET_MS", "8000")))
    vision_budget = int(float(os.getenv("DREAM_CUSTOMS_BENCH_VISION_BUDGET_MS", "9000")))
    asr_budget = int(float(os.getenv("DREAM_CUSTOMS_BENCH_ASR_BUDGET_MS", "8000")))

    intake = build_intake(
        dream_text="I dreamed my phone died while I waited for an elevator.",
        mood="Anxious",
    )
    state = build_qa_state(intake, language="en")
    answers = "The dead phone felt closest to being behind before I even start."

    report: dict[str, Any] = {
        "configured": {
            "text_endpoint": bool(text_endpoint),
            "vision_endpoint": bool(vision_endpoint),
            "asr_endpoint": bool(asr_endpoint),
            "token": bool(token),
            "image_path": bool(image_path),
            "audio_path": bool(audio_path),
        },
        "budgets_ms": {"text": text_budget, "vision": vision_budget, "asr": asr_budget},
        "results": [],
    }

    if text_endpoint:
        text_client = HostedMiniCPMTextClient(
            endpoint=text_endpoint,
            token=token,
            timeout=text_timeout,
            max_tokens=560,
            latency_budget_ms=text_budget,
            fallback=TextFallback(),
        )
        report["results"].append(
            _measure(
                "text_negotiation",
                lambda: text_client.generate_negotiation(negotiation_prompt(intake, "en")),
            )
        )
        report["results"].append(
            _measure(
                "text_today_tip",
                lambda: text_client.generate_today_tip(today_tip_prompt(intake, state, answers, "en")),
            )
        )
    if vision_endpoint and image_path and Path(image_path).exists():
        vision_client = HostedMiniCPMVisionClient(
            endpoint=vision_endpoint,
            token=token,
            timeout=vision_timeout,
            max_tokens=220,
            latency_budget_ms=vision_budget,
            fallback=VisionFallback(),
        )
        report["results"].append(_measure("vision_clues", lambda: vision_client.extract_clues(image_path)))
    if asr_endpoint:
        probe_audio = ""
        try:
            probe_audio = audio_path if audio_path and Path(audio_path).exists() else _write_probe_wav()
            asr_client = HostedASRClient(
                endpoint=asr_endpoint,
                token=token,
                timeout=asr_timeout,
                latency_budget_ms=asr_budget,
                fallback=ASRFallback(),
            )
            report["results"].append(_measure("asr_transcribe", lambda: asr_client.transcribe(probe_audio)))
        finally:
            if probe_audio and probe_audio != audio_path:
                try:
                    os.unlink(probe_audio)
                except OSError:
                    pass

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
