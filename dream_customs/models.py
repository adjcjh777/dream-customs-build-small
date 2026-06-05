import base64
import json
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from dream_customs.prompts import visual_clue_prompt
from dream_customs.schema import PactCard


def _contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


class FakeVisionClient:
    def extract_clues(self, image_path: Optional[str]) -> List[str]:
        if not image_path:
            return []
        return ["blue hallway", "melted elevator buttons", "number 14"]


class FakeASRClient:
    def transcribe(self, audio_path: Optional[str]) -> str:
        if not audio_path:
            return ""
        return "The buttons melted and I could not catch the elevator."


class FakeTextClient:
    def generate_negotiation(self, prompt: str) -> Dict[str, Any]:
        if _contains_cjk(prompt):
            return {
                "visitor_name": "迟到的电梯",
                "questions": [
                    "这部电梯是在阻止你，还是在替你争取一点慢下来的时间？",
                    "如果它今天只允许你带走一件东西，你会选择哪件未完成的小事？",
                    "你愿意用一个 5 分钟动作和它交换放行章吗？",
                ],
                "tone_note": "这个来访者也许不是敌人，而是在提醒你把开始和完成分开。",
            }
        return {
            "visitor_name": "Late Elevator",
            "questions": [
                "Was the elevator blocking you, or buying you a slower morning?",
                "If it lets you carry one unfinished thing into today, which one is smallest?",
                "Would you trade it a five-minute action for a release stamp?",
            ],
            "tone_note": "This visitor may be asking you to separate starting from finishing.",
        }

    def generate_pact(self, prompt: str) -> PactCard:
        if _contains_cjk(prompt):
            return PactCard(
                visitor_name="迟到的电梯",
                permit_id="DC-DEMO-014",
                contraband=["未申报的焦虑", "融化的按钮", "一小袋没来得及开始的事"],
                risk_level="橙色：需要被安置，但不需要被害怕",
                alliance_reading="这个梦也许在提醒你，今天先把启动一件事和完成一件事分开。",
                practical_suggestion="提前 10 分钟打开一个最小任务，只要求开始，不要求完成。",
                weird_task="给电梯写一句道歉信：抱歉总让你替我背迟到的锅。",
                bedtime_release="今日电梯已停靠，未完成事项明日再报关。",
            )
        return PactCard(
            visitor_name="Late Elevator",
            permit_id="DC-DEMO-014",
            contraband=["unfiled anxiety", "melted buttons", "one pouch of unstarted tasks"],
            risk_level="orange: needs placement, not fear",
            alliance_reading="This visitor asks you to separate starting from finishing.",
            practical_suggestion="Open one small task ten minutes early. You only need to start it.",
            weird_task="Write the elevator a one-sentence apology note.",
            bedtime_release="Today the elevator has docked; unfinished floors report tomorrow.",
        )


def _strip_markdown_and_thinking(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL).strip()
    cleaned = cleaned.replace("<think>", "").replace("</think>", "").strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned.strip(), flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    return cleaned


def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    cleaned = _strip_markdown_and_thinking(text)
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


def _as_string_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [part.strip() for part in re.split(r"[,，\n]", value) if part.strip()]
    return []


class OllamaTextClient:
    def __init__(
        self,
        model_name: str = "hf.co/openbmb/MiniCPM5-1B-GGUF:Q8_0",
        base_url: str = "http://localhost:11434",
        timeout: float = 45.0,
        fallback: Optional[FakeTextClient] = None,
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.fallback = fallback or FakeTextClient()

    def _post_generate(self, prompt: str, num_predict: int = 512) -> Dict[str, Any]:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": num_predict},
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def _generate_json(self, prompt: str, schema_hint: str, num_predict: int = 512) -> Optional[Dict[str, Any]]:
        strict_prompt = (
            f"{prompt}\n\n"
            "Return only a single valid JSON object. No markdown, no code fences, no hidden reasoning.\n"
            f"Required schema: {schema_hint}"
        )
        try:
            response = self._post_generate(strict_prompt, num_predict=num_predict)
        except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError):
            return None
        return _extract_json_object(str(response.get("response", "")))

    def generate_negotiation(self, prompt: str) -> Dict[str, Any]:
        parsed = self._generate_json(
            prompt,
            '{"visitor_name":"string","questions":["string","string"],"tone_note":"string"}',
            num_predict=320,
        )
        if not parsed:
            return self.fallback.generate_negotiation(prompt)
        questions = _as_string_list(parsed.get("questions"))
        if not parsed.get("visitor_name") or not questions:
            return self.fallback.generate_negotiation(prompt)
        return {
            "visitor_name": str(parsed.get("visitor_name", "")).strip(),
            "questions": questions[:3],
            "tone_note": str(parsed.get("tone_note", "")).strip(),
        }

    def generate_pact(self, prompt: str) -> PactCard:
        parsed = self._generate_json(
            prompt,
            (
                '{"visitor_name":"string","permit_id":"string","contraband":["string"],'
                '"risk_level":"string","alliance_reading":"string","practical_suggestion":"string",'
                '"weird_task":"string","bedtime_release":"string","safety_note":"string"}'
            ),
            num_predict=700,
        )
        if not parsed:
            return self.fallback.generate_pact(prompt)
        try:
            return PactCard(
                visitor_name=str(parsed["visitor_name"]).strip(),
                permit_id=str(parsed["permit_id"]).strip(),
                contraband=_as_string_list(parsed["contraband"]) or ["unfiled dream fragment"],
                risk_level=str(parsed["risk_level"]).strip(),
                alliance_reading=str(parsed["alliance_reading"]).strip(),
                practical_suggestion=str(parsed["practical_suggestion"]).strip(),
                weird_task=str(parsed["weird_task"]).strip(),
                bedtime_release=str(parsed["bedtime_release"]).strip(),
                safety_note=str(parsed.get("safety_note", "")).strip(),
            )
        except (KeyError, TypeError, ValueError):
            return self.fallback.generate_pact(prompt)


class OllamaVisionClient:
    def __init__(
        self,
        model_name: str = "openbmb/minicpm-v4.6",
        base_url: str = "http://localhost:11434",
        timeout: float = 60.0,
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _post_generate(self, prompt: str, image_b64: str, num_predict: int = 256) -> Dict[str, Any]:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": num_predict},
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def extract_clues(self, image_path: Optional[str]) -> List[str]:
        if not image_path:
            return []
        try:
            with open(image_path, "rb") as image_file:
                image_b64 = base64.b64encode(image_file.read()).decode("ascii")
            response = self._post_generate(visual_clue_prompt(), image_b64)
        except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError):
            return []

        text = str(response.get("response", ""))
        parsed = _extract_json_object(text)
        if parsed:
            clues: List[str] = []
            for key in ("objects", "places", "visible_text", "colors", "mood_cues", "uncertain_details"):
                clues.extend(_as_string_list(parsed.get(key)))
            return clues[:8]
        return [part.strip() for part in re.split(r"[,，\n]", _strip_markdown_and_thinking(text)) if part.strip()][:8]


class MiniCPMVisionClient:
    def __init__(self, model_name: str = "openbmb/MiniCPM-V-4.6"):
        self.model_name = model_name
        self._pipe = None

    def _load(self):
        if self._pipe is None:
            from transformers import pipeline

            self._pipe = pipeline("image-text-to-text", model=self.model_name)
        return self._pipe

    def extract_clues(self, image_path: Optional[str]) -> List[str]:
        if not image_path:
            return []
        pipe = self._load()
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "path": image_path},
                    {
                        "type": "text",
                        "text": (
                            "Extract concise dream-like visual clues from this image. "
                            "Return a comma-separated list. Do not diagnose."
                        ),
                    },
                ],
            }
        ]
        result = pipe(text=messages)
        text = str(result)
        return [part.strip() for part in text.replace("\n", ",").split(",") if part.strip()][:8]
