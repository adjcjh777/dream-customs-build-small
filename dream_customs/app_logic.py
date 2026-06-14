import json
import os
from typing import Any, Tuple
from urllib.parse import urlparse, urlunparse

from dream_customs.models import (
    FakeASRClient,
    FakeTextClient,
    FakeVisionClient,
    HostedASRClient,
    HostedMiniCPMTextClient,
    HostedMiniCPMVisionClient,
    OllamaTextClient,
    OllamaVisionClient,
)
from dream_customs.defaults import DEFAULT_ASR_BACKEND, DEFAULT_TEXT_BACKEND, DEFAULT_VISION_BACKEND
from dream_customs.pipeline import (
    add_evidence,
    answer_question,
    ask_questions,
    create_session,
    draft_pact,
    finish_today_tip,
    generate_negotiation,
    generate_pact,
    generate_today_tip,
    intake_from_modalities,
    revise_pact,
    seal_pact,
    skip_question,
)
from dream_customs.render import render_pact_card, render_pact_inspector, render_status_bar, render_timeline, render_today_tip_card
from dream_customs.schema import CustomsSession


DEFAULT_TEXT_MODEL = "hf.co/openbmb/MiniCPM5-1B-GGUF:Q8_0"
DEFAULT_VISION_MODEL = "openbmb/minicpm-v4.6"
DEFAULT_HOSTED_TIMEOUT_SECONDS = 9.0
DEFAULT_ASR_TIMEOUT_SECONDS = 9.0
DEFAULT_TEXT_TEMPERATURE = 0.0
DEFAULT_VISION_TEMPERATURE = 0.1
DEFAULT_TEXT_MAX_TOKENS = 480
DEFAULT_VISION_MAX_TOKENS = 220
DEFAULT_TEXT_LATENCY_BUDGET_MS = 8000
DEFAULT_VISION_LATENCY_BUDGET_MS = 9000
DEFAULT_ASR_LATENCY_BUDGET_MS = 8000


def _file_path(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return str(value.get("path") or value.get("name") or "")
    if hasattr(value, "path"):
        return str(getattr(value, "path") or "")
    if hasattr(value, "name"):
        return str(getattr(value, "name") or "")
    if isinstance(value, (list, tuple)) and value:
        return _file_path(value[0])
    return ""


def _as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _derive_modal_asr_endpoint(text_endpoint: str) -> str:
    if not text_endpoint:
        return ""
    parsed = urlparse(text_endpoint.strip())
    if parsed.netloc.endswith("-text.modal.run"):
        netloc = f"{parsed.netloc.removesuffix('-text.modal.run')}-asr.modal.run"
        return urlunparse(parsed._replace(netloc=netloc))
    if parsed.path.rstrip("/").endswith("/text"):
        path = f"{parsed.path.rstrip('/')[:-len('/text')]}/asr"
        return urlunparse(parsed._replace(path=path))
    return ""


def _client_settings(
    text_endpoint: str = "",
    vision_endpoint: str = "",
    hosted_token: str = "",
    ollama_url: str = "",
    text_model: str = "",
    vision_model: str = "",
    text_timeout_seconds: Any = DEFAULT_HOSTED_TIMEOUT_SECONDS,
    vision_timeout_seconds: Any = DEFAULT_HOSTED_TIMEOUT_SECONDS,
    text_temperature: Any = DEFAULT_TEXT_TEMPERATURE,
    vision_temperature: Any = DEFAULT_VISION_TEMPERATURE,
    text_max_tokens: Any = DEFAULT_TEXT_MAX_TOKENS,
    vision_max_tokens: Any = DEFAULT_VISION_MAX_TOKENS,
    asr_backend: str = DEFAULT_ASR_BACKEND,
    asr_endpoint: str = "",
    asr_timeout_seconds: Any = DEFAULT_ASR_TIMEOUT_SECONDS,
    text_latency_budget_ms: Any = DEFAULT_TEXT_LATENCY_BUDGET_MS,
    vision_latency_budget_ms: Any = DEFAULT_VISION_LATENCY_BUDGET_MS,
    asr_latency_budget_ms: Any = DEFAULT_ASR_LATENCY_BUDGET_MS,
) -> dict:
    resolved_text_endpoint = (text_endpoint or os.getenv("DREAM_CUSTOMS_TEXT_ENDPOINT", "")).strip()
    resolved_asr_endpoint = (asr_endpoint or os.getenv("DREAM_CUSTOMS_ASR_ENDPOINT", "")).strip()
    if not resolved_asr_endpoint:
        resolved_asr_endpoint = _derive_modal_asr_endpoint(resolved_text_endpoint)
    return {
        "text_endpoint": resolved_text_endpoint,
        "vision_endpoint": (vision_endpoint or os.getenv("DREAM_CUSTOMS_VISION_ENDPOINT", "")).strip(),
        "hosted_token": (hosted_token or os.getenv("DREAM_CUSTOMS_HOSTED_TOKEN", "")).strip(),
        "ollama_url": (ollama_url or os.getenv("DREAM_CUSTOMS_OLLAMA_URL", "http://localhost:11434")).strip(),
        "text_model": (text_model or os.getenv("DREAM_CUSTOMS_TEXT_MODEL", DEFAULT_TEXT_MODEL)).strip(),
        "vision_model": (vision_model or os.getenv("DREAM_CUSTOMS_VISION_MODEL", DEFAULT_VISION_MODEL)).strip(),
        "text_timeout_seconds": max(1.0, _as_float(text_timeout_seconds, DEFAULT_HOSTED_TIMEOUT_SECONDS)),
        "vision_timeout_seconds": max(1.0, _as_float(vision_timeout_seconds, DEFAULT_HOSTED_TIMEOUT_SECONDS)),
        "text_temperature": max(0.0, min(_as_float(text_temperature, DEFAULT_TEXT_TEMPERATURE), 0.7)),
        "vision_temperature": max(0.0, min(_as_float(vision_temperature, DEFAULT_VISION_TEMPERATURE), 0.7)),
        "text_max_tokens": max(64, min(_as_int(text_max_tokens, DEFAULT_TEXT_MAX_TOKENS), 1200)),
        "vision_max_tokens": max(64, min(_as_int(vision_max_tokens, DEFAULT_VISION_MAX_TOKENS), 800)),
        "asr_backend": (asr_backend or DEFAULT_ASR_BACKEND).lower(),
        "asr_endpoint": resolved_asr_endpoint,
        "asr_timeout_seconds": max(1.0, _as_float(asr_timeout_seconds, DEFAULT_ASR_TIMEOUT_SECONDS)),
        "text_latency_budget_ms": max(0, _as_int(text_latency_budget_ms, DEFAULT_TEXT_LATENCY_BUDGET_MS)),
        "vision_latency_budget_ms": max(0, _as_int(vision_latency_budget_ms, DEFAULT_VISION_LATENCY_BUDGET_MS)),
        "asr_latency_budget_ms": max(0, _as_int(asr_latency_budget_ms, DEFAULT_ASR_LATENCY_BUDGET_MS)),
    }


def _clients(text_backend: str, vision_backend: str, **settings):
    resolved = _client_settings(**settings)
    text_backend = (text_backend or DEFAULT_TEXT_BACKEND).lower()
    vision_backend = (vision_backend or DEFAULT_VISION_BACKEND).lower()
    if text_backend == "ollama":
        text_client = OllamaTextClient(
            model_name=resolved["text_model"],
            base_url=resolved["ollama_url"],
            timeout=resolved["text_timeout_seconds"],
            temperature=resolved["text_temperature"],
            max_tokens=resolved["text_max_tokens"],
        )
    elif text_backend in {"model", "modal", "huggingface"}:
        text_client = HostedMiniCPMTextClient(
            endpoint=resolved["text_endpoint"],
            token=resolved["hosted_token"],
            timeout=resolved["text_timeout_seconds"],
            temperature=resolved["text_temperature"],
            max_tokens=resolved["text_max_tokens"],
            latency_budget_ms=resolved["text_latency_budget_ms"],
        )
    else:
        text_client = FakeTextClient()

    if vision_backend == "ollama":
        vision_client = OllamaVisionClient(
            model_name=resolved["vision_model"],
            base_url=resolved["ollama_url"],
            timeout=resolved["vision_timeout_seconds"],
        )
    elif vision_backend in {"model", "modal", "huggingface"}:
        vision_client = HostedMiniCPMVisionClient(
            endpoint=resolved["vision_endpoint"],
            token=resolved["hosted_token"],
            timeout=resolved["vision_timeout_seconds"],
            temperature=resolved["vision_temperature"],
            max_tokens=resolved["vision_max_tokens"],
            latency_budget_ms=resolved["vision_latency_budget_ms"],
        )
    else:
        vision_client = FakeVisionClient()

    if resolved["asr_backend"] in {"model", "modal", "huggingface"}:
        asr_client = HostedASRClient(
            endpoint=resolved["asr_endpoint"],
            token=resolved["hosted_token"],
            timeout=resolved["asr_timeout_seconds"],
            latency_budget_ms=resolved["asr_latency_budget_ms"],
        )
    else:
        asr_client = FakeASRClient()

    return text_client, vision_client, asr_client


def _session_from_state(state: Any) -> CustomsSession:
    if isinstance(state, CustomsSession):
        return state
    if isinstance(state, str) and state.strip():
        try:
            return CustomsSession.model_validate_json(state)
        except ValueError:
            return create_session()
    if isinstance(state, dict):
        try:
            return CustomsSession.model_validate(state)
        except ValueError:
            return create_session()
    return create_session()


def _debug_json(session: CustomsSession, text_backend: str, vision_backend: str, **settings) -> str:
    resolved = _client_settings(**settings)
    payload = {
        "status": session.phase,
        "text_backend": text_backend,
        "vision_backend": vision_backend,
        "developer_settings": {
            "text_endpoint_configured": bool(resolved["text_endpoint"]),
            "vision_endpoint_configured": bool(resolved["vision_endpoint"]),
            "asr_endpoint_configured": bool(resolved["asr_endpoint"]),
            "hosted_token_configured": bool(resolved["hosted_token"]),
            "ollama_url": resolved["ollama_url"],
            "text_model": resolved["text_model"],
            "vision_model": resolved["vision_model"],
            "text_timeout_seconds": resolved["text_timeout_seconds"],
            "vision_timeout_seconds": resolved["vision_timeout_seconds"],
            "asr_backend": resolved["asr_backend"],
            "asr_timeout_seconds": resolved["asr_timeout_seconds"],
            "text_temperature": resolved["text_temperature"],
            "vision_temperature": resolved["vision_temperature"],
            "text_max_tokens": resolved["text_max_tokens"],
            "vision_max_tokens": resolved["vision_max_tokens"],
            "text_latency_budget_ms": resolved["text_latency_budget_ms"],
            "vision_latency_budget_ms": resolved["vision_latency_budget_ms"],
            "asr_latency_budget_ms": resolved["asr_latency_budget_ms"],
        },
        "session": session.model_dump(mode="json"),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _notice(session: CustomsSession) -> str:
    latest_error = next((event for event in reversed(session.events) if event.role == "error"), None)
    if latest_error:
        return f"<div class='dc-inline-notice is-error'>{latest_error.body}</div>"
    if session.phase == "tip":
        return "<div class='dc-inline-notice is-sealed'>今日小 Tips 已生成。可以截图或复制。</div>"
    if session.phase == "drafting":
        return "<div class='dc-inline-notice'>解读草稿已准备好。可以补充细节、再问一个问题，或生成今日小 Tips。</div>"
    if session.phase in {"ask", "negotiating"}:
        return "<div class='dc-inline-notice'>梦境助手有一个追问。你可以回答、跳过、补充材料，或生成今日小 Tips。</div>"
    return "<div class='dc-inline-notice'>File any fragment. Text-only stays available if image or voice fails.</div>"


def _today_tip_plain_text(card) -> str:
    lines = [
        "Today Tip",
        f"Dream summary: {card.dream_summary}",
        f"Question: {card.main_question}",
        f"Dream anchors: {', '.join(card.dream_anchors)}",
        f"Interpretation: {card.interpretation}",
        f"Today Tip: {card.today_tip}",
    ]
    if card.tiny_action:
        lines.append(f"Tiny 5-minute action: {card.tiny_action}")
    if card.caring_note:
        lines.append(f"Caring note: {card.caring_note}")
    if card.safety_note:
        lines.append(f"Safety note: {card.safety_note}")
    return "\n".join(lines)


def _view(
    session: CustomsSession,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
):
    sealed_html = render_today_tip_card(session.sealed_tip) if session.sealed_tip else ""
    return (
        json.dumps(session.model_dump(mode="json"), ensure_ascii=False),
        render_status_bar(session, text_backend, vision_backend),
        render_timeline(session),
        render_pact_inspector(session),
        sealed_html,
        _debug_json(session, text_backend, vision_backend, **settings),
        _notice(session),
    )


def initial_workbench_state(
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
):
    return _view(create_session(), text_backend, vision_backend, **settings)


def start_declaration_action(
    state: Any,
    dream_text: str,
    image_value: Any = None,
    audio_value: Any = None,
    mood: str = "",
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
):
    session = _session_from_state(state)
    text_client, vision_client, asr_client = _clients(text_backend, vision_backend, **settings)
    session = add_evidence(
        session,
        dream_text=dream_text or "",
        image_path=_file_path(image_value) or None,
        audio_path=_file_path(audio_value) or None,
        mood=mood or "",
        vision_client=vision_client,
        asr_client=asr_client,
    )
    if session.phase != "error":
        session = ask_questions(session, text_client)
    return _view(session, text_backend, vision_backend, **settings)


def add_material_action(
    state: Any,
    dream_text: str,
    image_value: Any = None,
    audio_value: Any = None,
    mood: str = "",
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
):
    session = _session_from_state(state)
    _text_client, vision_client, asr_client = _clients(text_backend, vision_backend, **settings)
    session = add_evidence(
        session,
        dream_text=dream_text or "",
        image_path=_file_path(image_value) or None,
        audio_path=_file_path(audio_value) or None,
        mood=mood or "",
        vision_client=vision_client,
        asr_client=asr_client,
    )
    return _view(session, text_backend, vision_backend, **settings)


def answer_question_action(
    state: Any,
    answer: str,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
):
    session = answer_question(_session_from_state(state), answer or "")
    return _view(session, text_backend, vision_backend, **settings)


def skip_question_action(
    state: Any,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
):
    session = skip_question(_session_from_state(state))
    return _view(session, text_backend, vision_backend, **settings)


def ask_another_question_action(
    state: Any,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
):
    session = _session_from_state(state)
    text_client, _vision_client, _asr_client = _clients(text_backend, vision_backend, **settings)
    session = ask_questions(session, text_client, force_another=True)
    return _view(session, text_backend, vision_backend, **settings)


def draft_pact_action(
    state: Any,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
):
    session = _session_from_state(state)
    text_client, _vision_client, _asr_client = _clients(text_backend, vision_backend, **settings)
    session = draft_pact(session, text_client)
    return _view(session, text_backend, vision_backend, **settings)


def revise_pact_action(
    state: Any,
    revision_request: str,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
):
    session = _session_from_state(state)
    text_client, _vision_client, _asr_client = _clients(text_backend, vision_backend, **settings)
    session = revise_pact(session, revision_request or "", text_client)
    return _view(session, text_backend, vision_backend, **settings)


def seal_pact_action(
    state: Any,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
):
    session = _session_from_state(state)
    text_client, _vision_client, _asr_client = _clients(text_backend, vision_backend, **settings)
    session = finish_today_tip(session, text_client)
    return _view(session, text_backend, vision_backend, **settings)


def start_new_action(
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
):
    return _view(create_session(), text_backend, vision_backend, **settings)


def run_customs_once(
    dream_text: str,
    image_value: Any = None,
    audio_value: Any = None,
    mood: str = "",
    answers: str = "",
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
) -> Tuple[str, str, str, str]:
    image_path = _file_path(image_value)
    audio_path = _file_path(audio_value)
    if not any([dream_text and dream_text.strip(), image_path, audio_path]):
        return (
            "还没有收到梦境记录。",
            "请先添加文字、图片或语音，再生成今日小 Tips。",
            "",
            json.dumps({"status": "empty"}, ensure_ascii=False, indent=2),
        )

    text_client, vision_client, asr_client = _clients(text_backend, vision_backend, **settings)
    intake = intake_from_modalities(
        dream_text=dream_text or "",
        image_path=image_path or None,
        audio_path=audio_path or None,
        mood=mood or "",
        vision_client=vision_client,
        asr_client=asr_client,
    )
    negotiation = generate_negotiation(intake, text_client)
    answer_text = answers or "用户还没有回答追问，请根据已有记录生成温和今日小 Tips。"
    card = generate_today_tip(intake, answer_text, text_client)
    html = render_today_tip_card(card)
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
        "developer_settings": json.loads(_debug_json(create_session(), text_backend, vision_backend, **settings))[
            "developer_settings"
        ],
        "intake": intake.model_dump(),
        "negotiation": negotiation,
        "today_tip": card.model_dump(),
    }
    return negotiation_text, _today_tip_plain_text(card), html, json.dumps(debug, ensure_ascii=False, indent=2)
