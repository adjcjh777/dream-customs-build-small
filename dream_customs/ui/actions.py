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
    draft_pact,
    revise_pact,
    seal_pact,
    skip_question,
)
from dream_customs.schema import CustomsSession, PactCard


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
        if event.role == "customs" and event.status == "question":
            event.title = "Customs question filed"
            event.body = visible_question
            break
    return next_session


def _card_plain_text(card: PactCard) -> str:
    contraband = "、".join(card.contraband)
    parts = [
        "今日通行证",
        f"来访者：{card.visitor_name}",
        f"入境编号：{card.permit_id}",
        f"携带情绪违禁品：{contraband}",
        f"风险等级：{card.risk_level}",
        f"结盟解读：{card.alliance_reading}",
        f"今日生活建议：{card.practical_suggestion}",
        f"5 分钟怪趣任务：{card.weird_task}",
        f"睡前放行仪式：{card.bedtime_release}",
    ]
    if card.safety_note:
        parts.append(f"安全提示：{card.safety_note}")
    return "\n".join(parts)


def _render_today_pass(card: PactCard) -> str:
    contraband = "".join(f"<li>{escape(item)}</li>" for item in card.contraband)
    safety = (
        "<section class='dc-pass-safety'>"
        "<strong>必要时的安全提示</strong>"
        f"<p>{escape(card.safety_note)}</p>"
        "</section>"
        if card.safety_note
        else ""
    )
    return f"""
<article class="dc-pass-card">
  <div class="dc-pass-topline">
    <span>今日通行证</span>
    <span>{escape(card.permit_id)}</span>
  </div>
  <h2>{escape(card.visitor_name)}</h2>
  <p class="dc-pass-risk">{escape(card.risk_level)}</p>
  <section>
    <h3>可能代表的情绪</h3>
    <p>{escape(card.alliance_reading)}</p>
  </section>
  <section>
    <h3>今天的生活小 tip</h3>
    <p>{escape(card.practical_suggestion)}</p>
  </section>
  <section>
    <h3>5 分钟怪趣任务</h3>
    <p>{escape(card.weird_task)}</p>
  </section>
  <section>
    <h3>携带情绪违禁品</h3>
    <ul>{contraband}</ul>
  </section>
  <section>
    <h3>睡前放行词</h3>
    <p>{escape(card.bedtime_release)}</p>
  </section>
  {safety}
  <div class="dc-pass-seal">SEALED / 已放行</div>
</article>
""".strip()


def _questions(session: CustomsSession) -> List[str]:
    return session.question_history[-1:] if session.question_history else []


def _view_payload(session: CustomsSession, text_backend: str, vision_backend: str, **settings) -> Dict[str, Any]:
    card = session.sealed_pact or session.draft_pact
    error = _latest_error(session)
    status = "error" if error else "card" if session.sealed_pact else "question" if session.question_history else "declaration"
    return {
        "status": status,
        "phase": session.phase,
        "question": _questions(session)[0] if _questions(session) else "",
        "questions": _questions(session),
        "card_title": "今日通行证" if card else "",
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
        return error or "海关还没收到梦的碎片。"
    if status == "question":
        return "这一步是可选补充：说一点醒来后的真实感受，或者直接跳过。"
    if status == "card":
        return "今日通行证已盖章。它是一个温柔的行动提示，不是诊断。"
    return "写一句、几句，或贴一段梦；文字路径永远可用。"


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
    if session.sealed_pact and not session.draft_pact:
        session.draft_pact = session.sealed_pact
    text_client, _vision_client, _asr_client = _clients(text_backend, vision_backend, **settings)
    session = revise_pact(session, revision_request or "", text_client)
    if session.phase == "error":
        return _view(session, text_backend, vision_backend, **settings)
    session = seal_pact(session)
    return _view(session, text_backend, vision_backend, **settings)


def reset_mobile_action(
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    **settings,
) -> Tuple[str, str]:
    return initial_mobile_state(text_backend, vision_backend, **settings)


def _seal_view(session: CustomsSession, text_backend: str, vision_backend: str, **settings) -> Tuple[str, str]:
    text_client, _vision_client, _asr_client = _clients(text_backend, vision_backend, **settings)
    session = draft_pact(session, text_client)
    if session.phase != "error":
        session = seal_pact(session)
    return _view(session, text_backend, vision_backend, **settings)
