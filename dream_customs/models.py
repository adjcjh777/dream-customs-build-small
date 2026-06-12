import base64
import ast
import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from dream_customs.prompts import visual_clue_prompt, visual_witness_prompt
from dream_customs.schema import DreamBrief, DreamQAState, PactCard, PactCritique, TodayTipCard, VisionWitness


class FakeVisionClient:
    def extract_clues(self, image_path: Optional[str]) -> List[str]:
        if not image_path:
            return []
        return ["blue hallway", "melted elevator buttons", "number 14"]

    def extract_witness(self, image_path: Optional[str]) -> VisionWitness:
        if not image_path:
            return VisionWitness()
        return VisionWitness(
            scene_summary="A blue hallway with a melted elevator button.",
            objects=["elevator button", "blue hallway"],
            visible_text=["14"],
            spatial_relations=["button near the frozen floor number"],
            mood_cues=["stuck", "uncertain"],
            uncertain_details=[],
            surprising_detail="The button looks soft, almost waxy.",
        )


class FakeASRClient:
    def transcribe(self, audio_path: Optional[str]) -> str:
        if not audio_path:
            return ""
        return "The buttons melted and I could not catch the elevator."


class FakeTextClient:
    def _wants_zh(self, prompt: str) -> bool:
        return "自然中文" in prompt or "所有面向用户的字段都用自然中文" in prompt

    def generate_brief(self, prompt: str) -> DreamBrief:
        return DreamBrief(
            anchors=["elevator", "melted buttons", "floor 14"],
            emotional_hypothesis="The dream may be protecting the user from freezing at the start of a task.",
            today_bridge="Choose one stalled task and name the next small movement.",
            visual_evidence=["Visible text: 14"],
            safety_flags=[],
            language="en",
        )

    def generate_negotiation(self, prompt: str) -> Dict[str, Any]:
        if not self._wants_zh(prompt):
            return {
                "visitor_name": "Late elevator",
                "questions": [
                    "When you think about the elevator and the melted button, what real thing today feels hard to start?",
                    "Was the strongest feeling urgency, tiredness, curiosity, or something else?",
                    "Would a practical suggestion, a tiny action, or a caring sentence help most today?",
                ],
                "tone_note": "The dream may be asking you to make the first step smaller, not to finish everything at once.",
            }
        return {
            "visitor_name": "迟到的电梯",
            "questions": [
                "醒来时最强烈的感受是什么：着急、疲惫、好奇，还是别的？",
                "最近有没有一件真实的小事，让你还没开始就觉得有点来不及？",
                "你更想得到一个认真建议、一个没试过的小行动，还是一句被照顾到的话？",
            ],
            "tone_note": "这个梦也许是在提醒你先把开始变小，而不是马上要求完成。",
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

    def generate_today_tip(self, prompt: str) -> TodayTipCard:
        if not self._wants_zh(prompt):
            return TodayTipCard(
                dream_summary="You dreamed that an elevator would not arrive, its button melted like wax, and floor 14 stayed frozen.",
                main_question="Could this dream connect to feeling stuck before starting?",
                dream_anchors=["elevator", "melted button", "floor 14"],
                followup_questions=[
                    "Was the strongest feeling urgency, fear, or absurdity?",
                    "Is there one real task that feels late before it has even started?",
                ],
                user_answers=[],
                interpretation=(
                    "Maybe this dream is not predicting lateness. It turns the feeling of being stuck before "
                    "starting into an elevator paused at floor 14."
                ),
                today_tip=(
                    "1. Translate the elevator into the real-life doorway where you feel stuck. "
                    "2. Open only the draft or email connected to that doorway. "
                    "3. Add the first sentence and save it without sending yet."
                ),
                tiny_action=(
                    "Draw an elevator button labeled Draft Floor on a sticky note, press it once with your finger, "
                    "then write only the first sentence."
                ),
                caring_note="You can move one floor at a time; the whole building does not need to be solved this morning.",
            )
        return TodayTipCard(
            dream_summary="你梦见电梯迟迟不到，按钮像蜡一样融化，楼层数字停在 14。",
            main_question="这个梦是否和最近卡在开始之前有关？",
            dream_anchors=["电梯", "融化的按钮", "数字 14"],
            followup_questions=[
                "梦里最强烈的是着急、害怕，还是荒诞？",
                "最近有没有一件事让你还没开始就觉得迟到？",
            ],
            user_answers=[],
            interpretation=(
                "也许这个梦不是在预言你会迟到，而是在把“还没开始就担心来不及”的感觉，"
                "演成了一部停在 14 层的电梯。"
            ),
            today_tip=(
                "1. 把「电梯」翻译成现实里最像卡在入口的一件事。"
                "2. 只打开和它有关的草稿或邮件。"
                "3. 写下第一句话后先存起来，不要求马上发出。"
            ),
            tiny_action="找一张便利贴，画一个只到“草稿层”的电梯按钮，按一下，再只写第一句话。",
            caring_note="你可以慢慢前进，不需要一醒来就解决所有楼层。",
        )

    def generate_pact_draft(self, prompt: str) -> PactCard:
        return self.generate_pact(prompt)

    def critique_pact(self, prompt: str) -> PactCritique:
        return PactCritique(passes=True, issues=[], rewrite_instruction="")

    def rewrite_pact(self, prompt: str) -> PactCard:
        return self.generate_pact(prompt)


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


def _as_bool(value: Any, default: bool = True) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"false", "no", "0"}:
            return False
        if normalized in {"true", "yes", "1"}:
            return True
    if value is None:
        return default
    return bool(value)


def _dream_brief_from_parsed(parsed: Dict[str, Any]) -> DreamBrief:
    return DreamBrief(
        anchors=_as_string_list(parsed.get("anchors")),
        emotional_hypothesis=str(parsed.get("emotional_hypothesis", "")).strip(),
        today_bridge=str(parsed.get("today_bridge", "")).strip(),
        visual_evidence=_as_string_list(parsed.get("visual_evidence")),
        safety_flags=_as_string_list(parsed.get("safety_flags")),
        language=str(parsed.get("language", "en")).strip() or "en",
    )


def _pact_critique_from_parsed(parsed: Dict[str, Any]) -> PactCritique:
    return PactCritique(
        passes=_as_bool(parsed.get("passes"), default=True),
        issues=_as_string_list(parsed.get("issues")),
        rewrite_instruction=str(parsed.get("rewrite_instruction", "")).strip(),
    )


def _today_tip_from_parsed(parsed: Dict[str, Any], fallback_state: Optional[DreamQAState] = None) -> TodayTipCard:
    fallback_state = fallback_state or DreamQAState()
    return TodayTipCard(
        dream_summary=str(parsed.get("dream_summary") or fallback_state.dream_summary or "").strip(),
        main_question=str(parsed.get("main_question") or fallback_state.main_question or "").strip(),
        dream_anchors=_as_string_list(parsed.get("dream_anchors")) or list(fallback_state.dream_anchors),
        followup_questions=_as_string_list(parsed.get("followup_questions")) or list(fallback_state.followup_questions),
        user_answers=_as_string_list(parsed.get("user_answers")) or list(fallback_state.user_answers),
        interpretation=str(parsed["interpretation"]).strip(),
        today_tip=str(parsed["today_tip"]).strip(),
        tiny_action=str(parsed.get("tiny_action", "")).strip(),
        caring_note=str(parsed.get("caring_note", "")).strip(),
        safety_note=str(parsed.get("safety_note", "")).strip(),
    )


def _has_witness_report_fields(parsed: Dict[str, Any]) -> bool:
    return bool(
        str(parsed.get("scene_summary", "")).strip()
        or _as_string_list(parsed.get("objects"))
        or _as_string_list(parsed.get("visible_text"))
        or _as_string_list(parsed.get("spatial_relations"))
        or _as_string_list(parsed.get("mood_cues"))
        or _as_string_list(parsed.get("uncertain_details"))
        or str(parsed.get("surprising_detail", "")).strip()
    )


def _has_legacy_flat_clue_fields(parsed: Dict[str, Any]) -> bool:
    return bool(_as_string_list(parsed.get("places")) or _as_string_list(parsed.get("colors")))


def _vision_witness_from_parsed(parsed: Dict[str, Any]) -> VisionWitness:
    return VisionWitness(
        scene_summary=str(parsed.get("scene_summary", "")).strip(),
        objects=_as_string_list(parsed.get("objects")),
        visible_text=_as_string_list(parsed.get("visible_text")),
        spatial_relations=_as_string_list(parsed.get("spatial_relations")),
        mood_cues=_as_string_list(parsed.get("mood_cues")),
        uncertain_details=_as_string_list(parsed.get("uncertain_details")),
        surprising_detail=str(parsed.get("surprising_detail", "")).strip(),
    )


def _flat_visual_clues_from_parsed(parsed: Dict[str, Any]) -> List[str]:
    clues: List[str] = []
    for key in ("objects", "places", "visible_text", "colors", "mood_cues", "uncertain_details"):
        clues.extend(_as_string_list(parsed.get(key)))
    return clues[:8]


def _flat_visual_clues_from_text(text: str) -> List[str]:
    return [part.strip() for part in re.split(r"[,，\n]", _strip_markdown_and_thinking(text)) if part.strip()][:8]


def _simple_witness_from_text(text: str) -> VisionWitness:
    clues = _flat_visual_clues_from_text(text)
    if not clues:
        return VisionWitness()
    return VisionWitness(scene_summary="; ".join(clues[:2]), objects=clues[2:6])


def _visual_clues_from_model_text(text: str) -> List[str]:
    parsed = _extract_json_object(text)
    if parsed:
        if _has_witness_report_fields(parsed) and not _has_legacy_flat_clue_fields(parsed):
            return _vision_witness_from_parsed(parsed).to_visual_clues()
        return _flat_visual_clues_from_parsed(parsed)
    return _flat_visual_clues_from_text(text)


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

    def generate_today_tip(self, prompt: str) -> TodayTipCard:
        parsed = self._generate_json(
            prompt,
            (
                '{"dream_summary":"string","main_question":"string","dream_anchors":["string"],'
                '"followup_questions":["string"],"user_answers":["string"],"interpretation":"string",'
                '"today_tip":"string","tiny_action":"string","caring_note":"string","safety_note":"string"}'
            ),
            num_predict=780,
        )
        if not parsed:
            return self.fallback.generate_today_tip(prompt)
        try:
            return _today_tip_from_parsed(parsed)
        except (KeyError, TypeError, ValueError):
            return self.fallback.generate_today_tip(prompt)
    def generate_brief(self, prompt: str) -> DreamBrief:
        parsed = self._generate_json(
            prompt,
            (
                '{"anchors":["string"],"emotional_hypothesis":"string",'
                '"today_bridge":"string","visual_evidence":["string"],'
                '"safety_flags":["string"],"language":"en"}'
            ),
            num_predict=520,
        )
        if not parsed:
            return self.fallback.generate_brief(prompt)
        try:
            return _dream_brief_from_parsed(parsed)
        except (TypeError, ValueError):
            return self.fallback.generate_brief(prompt)

    def generate_pact_draft(self, prompt: str) -> PactCard:
        return self.generate_pact(prompt)

    def critique_pact(self, prompt: str) -> PactCritique:
        parsed = self._generate_json(
            prompt,
            '{"passes":true,"issues":["string"],"rewrite_instruction":"string"}',
            num_predict=360,
        )
        if not parsed:
            return self.fallback.critique_pact(prompt)
        try:
            return _pact_critique_from_parsed(parsed)
        except (TypeError, ValueError):
            return self.fallback.critique_pact(prompt)

    def rewrite_pact(self, prompt: str) -> PactCard:
        return self.generate_pact(prompt)


class OllamaVisionClient:
    def __init__(
        self,
        model_name: str = "openbmb/minicpm-v4.6",
        base_url: str = "http://localhost:11434",
        timeout: float = 60.0,
        fallback: Optional[FakeVisionClient] = None,
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.fallback = fallback or FakeVisionClient()

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

    def extract_witness(self, image_path: Optional[str]) -> VisionWitness:
        if not image_path:
            return VisionWitness()
        try:
            with open(image_path, "rb") as image_file:
                image_b64 = base64.b64encode(image_file.read()).decode("ascii")
            response = self._post_generate(visual_witness_prompt(), image_b64, num_predict=320)
        except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError):
            return self.fallback.extract_witness(image_path)

        text = str(response.get("response", ""))
        parsed = _extract_json_object(text)
        if parsed and _has_witness_report_fields(parsed) and not _has_legacy_flat_clue_fields(parsed):
            return _vision_witness_from_parsed(parsed)
        if not parsed:
            return _simple_witness_from_text(text)
        return VisionWitness()

    def extract_clues(self, image_path: Optional[str]) -> List[str]:
        if not image_path:
            return []
        try:
            with open(image_path, "rb") as image_file:
                image_b64 = base64.b64encode(image_file.read()).decode("ascii")
            response = self._post_generate(visual_witness_prompt(), image_b64, num_predict=320)
        except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError):
            return self.fallback.extract_clues(image_path)

        text = str(response.get("response", ""))
        clues = _visual_clues_from_model_text(text)
        if clues:
            return clues

        try:
            response = self._post_generate(visual_clue_prompt(), image_b64)
        except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError):
            return self.fallback.extract_clues(image_path)

        clues = _visual_clues_from_model_text(str(response.get("response", "")))
        return clues or self.fallback.extract_clues(image_path)


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
            parsed = _python_literal_dict(value)
            if parsed:
                nested = _hosted_text_from_response(parsed)
                if nested:
                    return nested
            return value
        if isinstance(value, list):
            nested = _content_from_messages(value)
            if nested:
                return nested
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


def _python_literal_dict(text: str) -> Optional[Dict[str, Any]]:
    try:
        parsed = ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _content_from_messages(messages: List[Any]) -> str:
    for item in reversed(messages):
        if not isinstance(item, dict):
            continue
        content = item.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
        if isinstance(content, list):
            text_parts = [
                str(part.get("text", "")).strip()
                for part in content
                if isinstance(part, dict) and str(part.get("text", "")).strip()
            ]
            if text_parts:
                return "\n".join(text_parts)
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

    def generate_today_tip(self, prompt: str) -> TodayTipCard:
        parsed = self._generate_json(
            prompt,
            (
                '{"dream_summary":"string","main_question":"string","dream_anchors":["string"],'
                '"followup_questions":["string"],"user_answers":["string"],"interpretation":"string",'
                '"today_tip":"string","tiny_action":"string","caring_note":"string","safety_note":"string"}'
            ),
            max_tokens=780,
        )
        if not parsed:
            return self.fallback.generate_today_tip(prompt)
        try:
            return _today_tip_from_parsed(parsed)
        except (KeyError, TypeError, ValueError):
            return self.fallback.generate_today_tip(prompt)
    def generate_brief(self, prompt: str) -> DreamBrief:
        parsed = self._generate_json(
            prompt,
            (
                '{"anchors":["string"],"emotional_hypothesis":"string",'
                '"today_bridge":"string","visual_evidence":["string"],'
                '"safety_flags":["string"],"language":"en"}'
            ),
            max_tokens=520,
        )
        if not parsed:
            return self.fallback.generate_brief(prompt)
        try:
            return _dream_brief_from_parsed(parsed)
        except (TypeError, ValueError):
            return self.fallback.generate_brief(prompt)

    def generate_pact_draft(self, prompt: str) -> PactCard:
        return self.generate_pact(prompt)

    def critique_pact(self, prompt: str) -> PactCritique:
        parsed = self._generate_json(
            prompt,
            '{"passes":true,"issues":["string"],"rewrite_instruction":"string"}',
            max_tokens=360,
        )
        if not parsed:
            return self.fallback.critique_pact(prompt)
        try:
            return _pact_critique_from_parsed(parsed)
        except (TypeError, ValueError):
            return self.fallback.critique_pact(prompt)

    def rewrite_pact(self, prompt: str) -> PactCard:
        return self.generate_pact(prompt)


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

    def _post_image(self, image_path: str, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self.endpoint:
            return None
        try:
            with open(image_path, "rb") as image_file:
                image_b64 = base64.b64encode(image_file.read()).decode("ascii")
        except OSError:
            return None
        payload = {
            "prompt": prompt or visual_clue_prompt(),
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

    def extract_witness(self, image_path: Optional[str]) -> VisionWitness:
        if not image_path:
            return VisionWitness()
        try:
            payload = self._post_image(image_path, visual_witness_prompt())
        except TypeError:
            payload = self._post_image(image_path)
        if not payload:
            return self.fallback.extract_witness(image_path)
        text = _hosted_text_from_response(payload)
        parsed = _extract_json_object(text)
        if parsed and _has_witness_report_fields(parsed) and not _has_legacy_flat_clue_fields(parsed):
            return _vision_witness_from_parsed(parsed)
        if not parsed:
            return _simple_witness_from_text(text)
        return VisionWitness()

    def extract_clues(self, image_path: Optional[str]) -> List[str]:
        if not image_path:
            return []
        try:
            payload = self._post_image(image_path, visual_witness_prompt())
        except TypeError:
            payload = self._post_image(image_path)
        if not payload:
            return self.fallback.extract_clues(image_path)
        text = _hosted_text_from_response(payload)
        clues = _visual_clues_from_model_text(text)
        if clues:
            return clues

        try:
            payload = self._post_image(image_path, visual_clue_prompt())
        except TypeError:
            payload = self._post_image(image_path)
        if not payload:
            return self.fallback.extract_clues(image_path)
        clues = _visual_clues_from_model_text(_hosted_text_from_response(payload))
        return clues or self.fallback.extract_clues(image_path)


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
