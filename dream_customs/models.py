import base64
import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from dream_customs.prompts import visual_clue_prompt
from dream_customs.schema import PactCard


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
        return {
            "visitor_name": "Late Elevator",
            "questions": [
                "What feeling was strongest when you woke up: pressure, tiredness, curiosity, or something else?",
                "Is there one real-life thing you would like to make easier today?",
                "Would you rather receive a practical life tip, a tiny odd task, or both?",
            ],
            "tone_note": "This visitor may be asking for a smaller start, not a perfect finish.",
        }

    def generate_pact(self, prompt: str) -> PactCard:
        return PactCard(
            visitor_name="Late Elevator",
            permit_id="DC-DEMO-014",
            contraband=["unfiled pressure", "melted buttons", "a pocket of unstarted tasks"],
            risk_level="orange: worth placing gently, not fearing",
            alliance_reading="This dream may be pointing to the pressure of starting and finishing at the same time.",
            practical_suggestion="Choose one task and define only its first 10 minutes. Open it, then pause for water.",
            weird_task="Draw a tiny elevator button on paper, press it once, and work for five minutes.",
            bedtime_release="The elevator has docked for tonight. Unfinished floors can report tomorrow.",
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
        temperature: float = 0.2,
        max_tokens: int = 700,
        fallback: Optional[FakeTextClient] = None,
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.temperature = max(0.0, min(float(temperature), 0.7))
        self.max_tokens = max(64, min(int(max_tokens), 1200))
        self.fallback = fallback or FakeTextClient()

    def _post_generate(self, prompt: str, num_predict: int = 512) -> Dict[str, Any]:
        num_predict = max(64, min(int(num_predict), self.max_tokens))
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": self.temperature, "num_predict": num_predict},
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


def _hosted_text_from_response(payload: Dict[str, Any]) -> str:
    for key in ("response", "text", "generated_text", "output"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                return message["content"]
            if isinstance(first.get("text"), str):
                return first["text"]
    data = payload.get("data")
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return _hosted_text_from_response(data[0])
    return ""


class HostedMiniCPMTextClient:
    def __init__(
        self,
        endpoint: str = "",
        token: str = "",
        timeout: float = 60.0,
        temperature: float = 0.2,
        max_tokens: int = 780,
        fallback: Optional[FakeTextClient] = None,
    ):
        self.endpoint = endpoint.strip()
        self.token = token.strip()
        self.timeout = timeout
        self.temperature = max(0.0, min(float(temperature), 0.7))
        self.max_tokens = max(64, min(int(max_tokens), 1200))
        self.fallback = fallback or FakeTextClient()

    def _post_json(self, prompt: str, max_tokens: int = 700) -> Optional[Dict[str, Any]]:
        if not self.endpoint:
            return None
        max_tokens = max(64, min(int(max_tokens), self.max_tokens))
        payload = {
            "prompt": prompt,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": max_tokens,
        }
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError):
            return None

    def _generate_json(self, prompt: str, schema_hint: str, max_tokens: int = 700) -> Optional[Dict[str, Any]]:
        strict_prompt = (
            f"{prompt}\n\n"
            "Return only a single valid JSON object. No markdown, no code fences, no hidden reasoning.\n"
            f"Required schema: {schema_hint}"
        )
        payload = self._post_json(strict_prompt, max_tokens=max_tokens)
        if not payload:
            return None
        return _extract_json_object(_hosted_text_from_response(payload))

    def generate_negotiation(self, prompt: str) -> Dict[str, Any]:
        parsed = self._generate_json(
            prompt,
            '{"visitor_name":"string","questions":["string"],"tone_note":"string"}',
            max_tokens=360,
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
            max_tokens=780,
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


class HostedMiniCPMVisionClient:
    def __init__(
        self,
        endpoint: str = "",
        token: str = "",
        timeout: float = 60.0,
        temperature: float = 0.1,
        max_tokens: int = 320,
        fallback: Optional[FakeVisionClient] = None,
    ):
        self.endpoint = endpoint.strip()
        self.token = token.strip()
        self.timeout = timeout
        self.temperature = max(0.0, min(float(temperature), 0.7))
        self.max_tokens = max(64, min(int(max_tokens), 800))
        self.fallback = fallback or FakeVisionClient()

    def _post_image(self, image_path: str) -> Optional[Dict[str, Any]]:
        if not self.endpoint:
            return None
        try:
            with open(image_path, "rb") as image_file:
                image_b64 = base64.b64encode(image_file.read()).decode("ascii")
        except OSError:
            return None
        payload = {
            "prompt": visual_clue_prompt(),
            "image": image_b64,
            "images": [image_b64],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError):
            return None

    def extract_clues(self, image_path: Optional[str]) -> List[str]:
        if not image_path:
            return []
        payload = self._post_image(image_path)
        if not payload:
            return self.fallback.extract_clues(image_path)
        parsed = _extract_json_object(_hosted_text_from_response(payload))
        if parsed:
            clues: List[str] = []
            for key in ("objects", "places", "visible_text", "colors", "mood_cues", "uncertain_details"):
                clues.extend(_as_string_list(parsed.get(key)))
            if clues:
                return clues[:8]
        text = _hosted_text_from_response(payload)
        clues = [part.strip() for part in re.split(r"[,，\n]", _strip_markdown_and_thinking(text)) if part.strip()]
        return clues[:8] or self.fallback.extract_clues(image_path)


def _hosted_transcript_from_response(payload: Dict[str, Any]) -> str:
    for key in ("transcript", "text", "response", "generated_text", "output"):
        value = payload.get(key)
        if isinstance(value, str):
            return value.strip()
    data = payload.get("data")
    if isinstance(data, dict):
        return _hosted_transcript_from_response(data)
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return _hosted_transcript_from_response(data[0])
    return ""


class HostedASRClient:
    def __init__(
        self,
        endpoint: str = "",
        token: str = "",
        timeout: float = 45.0,
        fallback: Optional[FakeASRClient] = None,
    ):
        self.endpoint = endpoint.strip()
        self.token = token.strip()
        self.timeout = timeout
        self.fallback = fallback or FakeASRClient()

    def transcribe(self, audio_path: Optional[str]) -> str:
        if not audio_path:
            return ""
        if not self.endpoint:
            return self.fallback.transcribe(audio_path)
        try:
            with open(audio_path, "rb") as audio_file:
                audio_b64 = base64.b64encode(audio_file.read()).decode("ascii")
        except OSError:
            return ""
        payload = {
            "audio": audio_b64,
            "filename": os.path.basename(audio_path),
        }
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError):
            return self.fallback.transcribe(audio_path)
        return _hosted_transcript_from_response(payload) or self.fallback.transcribe(audio_path)
