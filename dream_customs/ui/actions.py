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
from dream_customs.schema import CustomsSession, TimelineEvent, TodayTipCard
from dream_customs.ui.copy import copy_for, normalize_language


def _looks_mostly_chinese(text: str) -> bool:
    clean = text or ""
    cjk_count = sum(1 for char in clean if "\u4e00" <= char <= "\u9fff")
    latin_count = sum(1 for char in clean if char.isascii() and char.isalpha())
    return cjk_count >= 4 and cjk_count >= latin_count


def _resolve_language_for_input(language: str, dream_text: str = "") -> str:
    normalized = normalize_language(language)
    if normalized == "en" and _looks_mostly_chinese(dream_text):
        return "zh"
    return normalized


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


def _card_plain_text(card: TodayTipCard, language: str) -> str:
    structured = json.dumps(
        {
            "dream_summary": card.dream_summary,
            "main_question": card.main_question,
            "dream_anchors": card.dream_anchors,
            "followup_questions": card.followup_questions,
            "user_answers": card.user_answers,
            "interpretation": card.interpretation,
            "today_tip": card.today_tip,
            "tiny_action": card.tiny_action,
            "caring_note": card.caring_note,
            "safety_note": card.safety_note,
        },
        ensure_ascii=False,
        indent=2,
    )
    if language == "zh":
        text = card.to_plain_text()
        if card.followup_questions:
            text += "\n追问记录: " + " / ".join(card.followup_questions)
        if card.user_answers:
            text += "\n用户回答: " + " / ".join(card.user_answers)
        if card.followup_questions and card.user_answers:
            text += "\n追问线索: 你的回答已进入今日小 Tips 的解读与行动建议。"
        text += "\n模型说明: 文本推理由 MiniCPM5-1B 路线生成；图片线索由 MiniCPM-V-4.6 路线理解。"
        text += f"\n\n结构化结果 JSON:\n{structured}"
        return text
    lines = [
        "Morning Ticket",
        f"Dream summary: {card.dream_summary}",
        f"Question: {card.main_question}",
        f"Dream anchors: {', '.join(card.dream_anchors)}",
        f"Follow-up questions: {' / '.join(card.followup_questions)}",
        f"User answers: {' / '.join(card.user_answers)}",
        f"Interpretation: {card.interpretation}",
        f"Today Tip: {card.today_tip}",
    ]
    if card.tiny_action:
        lines.append(f"Tiny 5-minute action: {card.tiny_action}")
    if card.caring_note:
        lines.append(f"Caring note: {card.caring_note}")
    if card.safety_note:
        lines.append(f"Safety note: {card.safety_note}")
    if card.followup_questions and card.user_answers:
        lines.append("Reasoning trail: Your follow-up answer shaped the interpretation and Today Tip.")
    lines.append("Small-model note: text via MiniCPM5-1B route; visual clues via MiniCPM-V-4.6 route.")
    lines.extend(["", "Structured result JSON:", structured])
    return "\n".join(lines)


def _render_today_pass(card: TodayTipCard, language: str) -> str:
    return render_today_tip_card(card, language=language)


def _questions(session: CustomsSession) -> List[str]:
    return session.question_history[-1:] if session.question_history else []


def _view_payload(
    session: CustomsSession,
    text_backend: str,
    vision_backend: str,
    language: str = "en",
    **settings,
) -> Dict[str, Any]:
    language = normalize_language(language)
    session_language = normalize_language(getattr(session, "language", language))
    if session_language != language and session.phase != "empty":
        language = session_language
    error = _latest_error(session)
    if error:
        status = "error"
    elif session.phase == "ask" and session.question_history:
        status = "ask"
    elif session.sealed_tip:
        status = "tip"
    elif session.question_history:
        status = "ask"
    else:
        status = "record"
    copy = copy_for(language)
    card = None if status == "ask" else session.sealed_tip or session.draft_tip
    payload = {
        "status": status,
        "phase": session.phase,
        "language": language,
        "question": _questions(session)[0] if _questions(session) else "",
        "questions": _questions(session),
        "card_title": copy["card_title"] if card else "",
        "card_text": _card_plain_text(card, language) if card else "",
        "card_html": _render_today_pass(card, language) if card else "",
        "error": error,
        "notice": _notice_for_status(status, error, language),
        "dream_summary": "",
        "main_question": "",
        "dream_anchors": [],
        "followup_questions": list(session.question_history),
        "user_answers": list(session.answer_history),
        "interpretation": "",
        "today_tip": "",
        "tiny_action": "",
        "caring_note": "",
        "safety_note": "",
        "debug": json.loads(_debug_json(session, text_backend, vision_backend, **settings)),
    }
    if card:
        payload.update(
            {
                "dream_summary": card.dream_summary,
                "main_question": card.main_question,
                "dream_anchors": card.dream_anchors,
                "followup_questions": card.followup_questions,
                "user_answers": card.user_answers,
                "interpretation": card.interpretation,
                "today_tip": card.today_tip,
                "tiny_action": card.tiny_action,
                "caring_note": card.caring_note,
                "safety_note": card.safety_note,
            }
        )
    return payload


def _view(
    session: CustomsSession,
    text_backend: str,
    vision_backend: str,
    language: str = "en",
    **settings,
) -> Tuple[str, str]:
    return _state_json(session), json.dumps(
        _view_payload(session, text_backend, vision_backend, language=language, **settings),
        ensure_ascii=False,
        indent=2,
    )


def _notice_for_status(status: str, error: str = "", language: str = "en") -> str:
    copy = copy_for(language)
    if status == "error":
        base = error or copy["notice_error"]
        if language == "zh":
            return f"{base} 你可以保留文字再点一次继续，或点击重新开始；Text-only 路径仍可用。"
        return f"{base} You can keep the text and try Continue again, or start over; the text-only path still works."
    if status == "ask":
        return copy["notice_ask"]
    if status == "tip":
        return copy["notice_tip"]
    return copy["notice_record"]


def initial_mobile_state(
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    language: str = "en",
    **settings,
) -> Tuple[str, str]:
    language = normalize_language(language)
    return _view(create_session(language=language), text_backend, vision_backend, language=language, **settings)


def submit_dream_action(
    dream_text: str,
    image_value: Any = None,
    audio_value: Any = None,
    mood: str = "",
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    language: str = "en",
    **settings,
) -> Tuple[str, str]:
    language = _resolve_language_for_input(language, dream_text)
    if not (dream_text or "").strip() and not _file_path(image_value) and not _file_path(audio_value):
        session = create_session(language=language)
        session.phase = "error"
        session.events.append(
            TimelineEvent(
                role="error",
                title="还没有梦境材料" if language == "zh" else "No dream material yet",
                body=(
                    "请先写一句梦境，或上传图片/语音；这样今日小 Tips 才能引用真实细节。"
                    if language == "zh"
                    else "Write at least one dream sentence, or add image/voice evidence, so the Today Tip can use real details."
                ),
                status="empty",
            )
        )
        return _view(session, text_backend, vision_backend, language=language, **settings)
    text_client, vision_client, asr_client = _clients(text_backend, vision_backend, **settings)
    session = add_evidence(
        create_session(language=language),
        dream_text=dream_text or "",
        image_path=_file_path(image_value) or None,
        audio_path=_file_path(audio_value) or None,
        mood=mood or "",
        vision_client=vision_client,
        asr_client=asr_client,
        language=language,
    )
    if session.phase != "error":
        previous_count = len(session.question_history)
        session = ask_questions(session, text_client, language=language)
        session = _trim_to_one_visible_question(session, previous_count)
    return _view(session, text_backend, vision_backend, language=language, **settings)


def skip_to_card_action(
    state: Any,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    language: str = "en",
    **settings,
) -> Tuple[str, str]:
    session = _session_from_state(state)
    language = normalize_language(getattr(session, "language", language))
    session = skip_question(session, language=language)
    return _seal_view(session, text_backend, vision_backend, language=language, **settings)


def answer_to_card_action(
    state: Any,
    answer: str,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    language: str = "en",
    **settings,
) -> Tuple[str, str]:
    session = _session_from_state(state)
    language = normalize_language(getattr(session, "language", language))
    session = answer_question(session, answer or "", language=language)
    if session.phase == "error":
        return _view(session, text_backend, vision_backend, language=language, **settings)
    return _seal_view(session, text_backend, vision_backend, language=language, **settings)


def revise_card_action(
    state: Any,
    revision_request: str,
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    language: str = "en",
    **settings,
) -> Tuple[str, str]:
    session = _session_from_state(state)
    language = normalize_language(getattr(session, "language", language))
    if session.sealed_tip and not session.draft_tip:
        session.draft_tip = session.sealed_tip
    text_client, _vision_client, _asr_client = _clients(text_backend, vision_backend, **settings)
    session = ask_questions(session, text_client, force_another=True, language=language)
    return _view(session, text_backend, vision_backend, language=language, **settings)


def reset_mobile_action(
    text_backend: str = DEFAULT_TEXT_BACKEND,
    vision_backend: str = DEFAULT_VISION_BACKEND,
    language: str = "en",
    **settings,
) -> Tuple[str, str]:
    return initial_mobile_state(text_backend, vision_backend, language=language, **settings)


def _seal_view(
    session: CustomsSession,
    text_backend: str,
    vision_backend: str,
    language: str = "en",
    **settings,
) -> Tuple[str, str]:
    text_client, _vision_client, _asr_client = _clients(text_backend, vision_backend, **settings)
    language = normalize_language(getattr(session, "language", language))
    session = finish_today_tip(session, text_client, language=language)
    return _view(session, text_backend, vision_backend, language=language, **settings)
