import json
import os
from typing import Any, Tuple

from dream_customs.models import (
    FakeASRClient,
    FakeTextClient,
    FakeVisionClient,
    HostedMiniCPMTextClient,
    HostedMiniCPMVisionClient,
    OllamaTextClient,
    OllamaVisionClient,
)
from dream_customs.defaults import DEFAULT_TEXT_BACKEND, DEFAULT_VISION_BACKEND
from dream_customs.pipeline import (
    add_evidence,
    answer_question,
    ask_questions,
    create_session,
    draft_pact,
    generate_negotiation,
    generate_pact,
    intake_from_modalities,
    revise_pact,
    seal_pact,
    skip_question,
)
from dream_customs.render import render_pact_card, render_pact_inspector, render_status_bar, render_timeline
from dream_customs.schema import CustomsSession


DEFAULT_TEXT_MODEL = "hf.co/openbmb/MiniCPM5-1B-GGUF:Q8_0"
DEFAULT_VISION_MODEL = "openbmb/minicpm-v4.6"


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


def _clients(text_backend: str, vision_backend: str):
    text_backend = (text_backend or DEFAULT_TEXT_BACKEND).lower()
    vision_backend = (vision_backend or DEFAULT_VISION_BACKEND).lower()
    if text_backend == "ollama":
        text_client = OllamaTextClient(
            model_name=os.getenv("DREAM_CUSTOMS_TEXT_MODEL", DEFAULT_TEXT_MODEL),
            base_url=os.getenv("DREAM_CUSTOMS_OLLAMA_URL", "http://localhost:11434"),
        )
    elif text_backend == "model":
        text_client = HostedMiniCPMTextClient(
            endpoint=os.getenv("DREAM_CUSTOMS_TEXT_ENDPOINT", ""),
            token=os.getenv("DREAM_CUSTOMS_HOSTED_TOKEN", ""),
        )
    else:
        text_client = FakeTextClient()

    if vision_backend == "ollama":
        vision_client = OllamaVisionClient(
            model_name=os.getenv("DREAM_CUSTOMS_VISION_MODEL", DEFAULT_VISION_MODEL),
            base_url=os.getenv("DREAM_CUSTOMS_OLLAMA_URL", "http://localhost:11434"),
        )
    elif vision_backend == "model":
        vision_client = HostedMiniCPMVisionClient(
            endpoint=os.getenv("DREAM_CUSTOMS_VISION_ENDPOINT", ""),
            token=os.getenv("DREAM_CUSTOMS_HOSTED_TOKEN", ""),
        )
    else:
        vision_client = FakeVisionClient()

    return text_client, vision_client, FakeASRClient()


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


def _debug_json(session: CustomsSession, text_backend: str, vision_backend: str) -> str:
    payload = {
        "status": session.phase,
        "text_backend": text_backend,
        "vision_backend": vision_backend,
        "session": session.model_dump(mode="json"),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _notice(session: CustomsSession) -> str:
    latest_error = next((event for event in reversed(session.events) if event.role == "error"), None)
    if latest_error:
        return f"<div class='dc-inline-notice is-error'>{latest_error.body}</div>"
    if session.phase == "sealed":
        return "<div class='dc-inline-notice is-sealed'>Today's pact is sealed. The card below is ready for a screenshot.</div>"
    if session.phase == "drafting":
        return "<div class='dc-inline-notice'>Draft ready. Revise it, ask another question, add material, or seal today's pact.</div>"
    if session.phase == "negotiating":
        return "<div class='dc-inline-notice'>The clerk has questions. Answer, skip, add material, or draft a pact.</div>"
    return "<div class='dc-inline-notice'>File any fragment. Text-only stays available if image or voice fails.</div>"


def _view(
    session: CustomsSession,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
):
    sealed_html = render_pact_card(session.sealed_pact) if session.sealed_pact else ""
    return (
        json.dumps(session.model_dump(mode="json"), ensure_ascii=False),
        render_status_bar(session, text_backend, vision_backend),
        render_timeline(session),
        render_pact_inspector(session),
        sealed_html,
        _debug_json(session, text_backend, vision_backend),
        _notice(session),
    )


def initial_workbench_state(
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
):
    return _view(create_session(), text_backend, vision_backend)


def start_declaration_action(
    state: Any,
    dream_text: str,
    image_value: Any = None,
    audio_value: Any = None,
    mood: str = "",
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
):
    session = _session_from_state(state)
    text_client, vision_client, asr_client = _clients(text_backend, vision_backend)
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
    return _view(session, text_backend, vision_backend)


def add_material_action(
    state: Any,
    dream_text: str,
    image_value: Any = None,
    audio_value: Any = None,
    mood: str = "",
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
):
    session = _session_from_state(state)
    _text_client, vision_client, asr_client = _clients(text_backend, vision_backend)
    session = add_evidence(
        session,
        dream_text=dream_text or "",
        image_path=_file_path(image_value) or None,
        audio_path=_file_path(audio_value) or None,
        mood=mood or "",
        vision_client=vision_client,
        asr_client=asr_client,
    )
    return _view(session, text_backend, vision_backend)


def answer_question_action(
    state: Any,
    answer: str,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
):
    session = answer_question(_session_from_state(state), answer or "")
    return _view(session, text_backend, vision_backend)


def skip_question_action(
    state: Any,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
):
    session = skip_question(_session_from_state(state))
    return _view(session, text_backend, vision_backend)


def ask_another_question_action(
    state: Any,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
):
    session = _session_from_state(state)
    text_client, _vision_client, _asr_client = _clients(text_backend, vision_backend)
    session = ask_questions(session, text_client, force_another=True)
    return _view(session, text_backend, vision_backend)


def draft_pact_action(
    state: Any,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
):
    session = _session_from_state(state)
    text_client, _vision_client, _asr_client = _clients(text_backend, vision_backend)
    session = draft_pact(session, text_client)
    return _view(session, text_backend, vision_backend)


def revise_pact_action(
    state: Any,
    revision_request: str,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
):
    session = _session_from_state(state)
    text_client, _vision_client, _asr_client = _clients(text_backend, vision_backend)
    session = revise_pact(session, revision_request or "", text_client)
    return _view(session, text_backend, vision_backend)


def seal_pact_action(
    state: Any,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
):
    session = _session_from_state(state)
    text_client, _vision_client, _asr_client = _clients(text_backend, vision_backend)
    if not session.draft_pact and session.intake.merged_text():
        session = draft_pact(session, text_client)
    session = seal_pact(session)
    return _view(session, text_backend, vision_backend)


def start_new_action(
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
):
    return _view(create_session(), text_backend, vision_backend)


def run_customs_once(
    dream_text: str,
    image_value: Any = None,
    audio_value: Any = None,
    mood: str = "",
    answers: str = "",
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
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
