import json
from html import escape
from typing import Any, Dict, List, Tuple

from dream_customs.app_logic import _clients, _debug_json, _file_path, _session_from_state
from dream_customs.defaults import DEFAULT_TEXT_BACKEND, DEFAULT_VISION_BACKEND
from dream_customs.pipeline import (
    add_evidence,
    answer_question,
    ask_questions,
    create_session,
    finish_today_tip,
    revise_pact,
    seal_pact,
    skip_question,
)
from dream_customs.render import render_today_tip_card
from dream_customs.schema import CustomsSession, TodayTipCard


def _state_json(session: CustomsSession) -> str:
    return json.dumps(session.model_dump(mode="json"), ensure_ascii=False)


def _latest_error(session: CustomsSession) -> str:
    event = next((item for item in reversed(session.events) if item.role == "error"), None)
    return event.body if event else ""


def _trim_to_one_visible_question(session: CustomsSession, previous_count: int) -> CustomsSession:
    if len(session.question_history) <= previous_count + 1:
        return session

    next_session = session.model_copy(deep=True)
    visible_question = next_session.question_history[previous_count]
    next_session.question_history = next_session.question_history[:previous_count] + [visible_question]
    for event in reversed(next_session.events):
        if event.role in {"assistant", "customs"} and event.status == "question":
            event.title = "梦境助手追问"
            event.body = visible_question
            break
    return next_session


def _card_plain_text(card: TodayTipCard) -> str:
    return card.to_plain_text()


def _render_today_pass(card: TodayTipCard) -> str:
    return render_today_tip_card(card)


def _questions(session: CustomsSession) -> List[str]:
    return session.question_history[-1:] if session.question_history else []


def _view_payload(session: CustomsSession, text_backend: str, vision_backend: str, **settings) -> Dict[str, Any]:
    card = session.sealed_tip or session.draft_tip
    error = _latest_error(session)
    status = "error" if error else "tip" if session.sealed_tip else "ask" if session.question_history else "record"
    return {
        "status": status,
        "phase": session.phase,
        "question": _questions(session)[0] if _questions(session) else "",
        "questions": _questions(session),
        "card_title": "今日小 Tips" if card else "",
        "card_text": _card_plain_text(card) if card else "",
        "card_html": _render_today_pass(card) if card else "",
        "error": error,
        "notice": _notice_for_status(status, error),
        "debug": json.loads(_debug_json(session, text_backend, vision_backend, **settings)),
    }


def _view(session: CustomsSession, text_backend: str, vision_backend: str, **settings) -> Tuple[str, str]:
    return _state_json(session), json.dumps(
        _view_payload(session, text_backend, vision_backend, **settings),
        ensure_ascii=False,
        indent=2,
    )


def _notice_for_status(status: str, error: str = "") -> str:
    if status == "error":
        return error or "梦境问答台还没有收到片段。"
    if status == "ask":
        return "可以回答这个追问，也可以跳过，直接生成今日小 Tips。"
    if status == "tip":
        return "今日小 Tips 已生成。把它当作温和参考，不是诊断或预言。"
    return "写一句、几行，或上传图片/语音。Text-only 路径始终可用。"


def initial_mobile_state(
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
) -> Tuple[str, str]:
    return _view(create_session(), text_backend, vision_backend, **settings)


def submit_dream_action(
    dream_text: str,
    image_value: Any = None,
    audio_value: Any = None,
    mood: str = "",
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
) -> Tuple[str, str]:
    text_client, vision_client, asr_client = _clients(text_backend, vision_backend, **settings)
    session = add_evidence(
        create_session(),
        dream_text=dream_text or "",
        image_path=_file_path(image_value) or None,
        audio_path=_file_path(audio_value) or None,
        mood=mood or "",
        vision_client=vision_client,
        asr_client=asr_client,
    )
    if session.phase != "error":
        previous_count = len(session.question_history)
        session = ask_questions(session, text_client)
        session = _trim_to_one_visible_question(session, previous_count)
    return _view(session, text_backend, vision_backend, **settings)


def skip_to_card_action(
    state: Any,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
) -> Tuple[str, str]:
    session = skip_question(_session_from_state(state))
    return _seal_view(session, text_backend, vision_backend, **settings)


def answer_to_card_action(
    state: Any,
    answer: str,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
) -> Tuple[str, str]:
    session = answer_question(_session_from_state(state), answer or "")
    if session.phase == "error":
        return _view(session, text_backend, vision_backend, **settings)
    return _seal_view(session, text_backend, vision_backend, **settings)


def revise_card_action(
    state: Any,
    revision_request: str,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
) -> Tuple[str, str]:
    session = _session_from_state(state)
    if session.sealed_tip and not session.draft_tip:
        session.draft_tip = session.sealed_tip
    text_client, _vision_client, _asr_client = _clients(text_backend, vision_backend, **settings)
    session = ask_questions(session, text_client, force_another=True)
    return _view(session, text_backend, vision_backend, **settings)


def reset_mobile_action(
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
) -> Tuple[str, str]:
    return initial_mobile_state(text_backend, vision_backend, **settings)


def _seal_view(session: CustomsSession, text_backend: str, vision_backend: str, **settings) -> Tuple[str, str]:
    text_client, _vision_client, _asr_client = _clients(text_backend, vision_backend, **settings)
    session = finish_today_tip(session, text_client)
    return _view(session, text_backend, vision_backend, **settings)
