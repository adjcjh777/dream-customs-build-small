import re
from datetime import date
from typing import Dict, List, Optional, Tuple

from dream_customs.prompts import followup_question_prompt, negotiation_prompt, pact_prompt, pact_revision_prompt
from dream_customs.render import render_pact_card
from dream_customs.safety import needs_escalation, safety_note
from dream_customs.schema import CustomsSession, DreamIntake, EvidenceItem, PactCard, TimelineEvent


def build_intake(
    dream_text: str = "",
    voice_transcript: str = "",
    visual_clues: Optional[List[str]] = None,
    mood: str = "",
    recurring_symbols: Optional[List[str]] = None,
    uncertainty: str = "",
    user_context: str = "",
) -> DreamIntake:
    return DreamIntake(
        dream_text=dream_text,
        voice_transcript=voice_transcript,
        visual_clues=visual_clues or [],
        mood=mood,
        recurring_symbols=recurring_symbols or [],
        uncertainty=uncertainty,
        user_context=user_context,
    )


def dated_permit_id(permit_id: str, today: Optional[date] = None) -> str:
    today = today or date.today()
    text = (permit_id or "").strip()
    serial_match = re.search(r"(?:^|[-_#])(\d{1,6})\s*$", text) or re.search(
        r"(\d+)(?!.*\d)",
        text,
    )
    serial = serial_match.group(1)[-3:].zfill(3) if serial_match else "001"
    return f"DREAM{today:%Y%m%d}-{serial}"


def _stamp_card_for_today(card: PactCard) -> PactCard:
    stamped = card.model_copy(deep=True)
    stamped.permit_id = dated_permit_id(stamped.permit_id)
    return stamped


def _looks_unclear_or_dream_literal(text: str) -> bool:
    clean = (text or "").strip()
    if len(clean) < 12:
        return True
    dream_literals = [
        "电梯运行",
        "模拟操作",
        "印章",
        "放行",
        "联盟",
        "梦境内容",
        "梦境无",
        "海关",
        "宣言",
        "魔法",
        "香薰皮",
        "果酱",
        "Dreamer",
    ]
    return any(term in clean for term in dream_literals)


def _safe_practical_suggestion(intake: DreamIntake) -> str:
    if _contains_cjk(intake.merged_text()):
        mood = intake.mood.strip()
        if mood in {"焦虑", "迷雾", "累"}:
            return "今天先做一件能稳住身体的小事：喝水、吃点东西，把最重要的一件事写成 10 分钟能开始的版本。"
        return "今天给自己留一个低风险开头：先整理桌面或日程 5 分钟，再只开始一件最小的任务。"
    return "Do one low-risk stabilizing thing today: drink water, eat something, and write the most important task as a 10-minute first step."


def _safe_weird_task(intake: DreamIntake) -> str:
    if _contains_cjk(intake.merged_text()):
        return "把今天最小的任务写在纸上，旁边画一个很小的通行章，然后只做 5 分钟。"
    return "Write your smallest task on paper, draw a tiny clearance stamp beside it, and work on it for just five minutes."


def _polish_card_for_daily_use(card: PactCard, intake: DreamIntake, answers: str) -> PactCard:
    polished = card.model_copy(deep=True)
    merged = "\n".join([intake.merged_text(), answers or ""])
    chinese = _contains_cjk(merged)

    if chinese and (not polished.visitor_name.strip() or re.fullmatch(r"[A-Za-z\s_-]+", polished.visitor_name.strip())):
        polished.visitor_name = "昨夜来访者"

    if _looks_unclear_or_dream_literal(polished.practical_suggestion):
        polished.practical_suggestion = _safe_practical_suggestion(intake)

    if _looks_unclear_or_dream_literal(polished.weird_task) and polished.weird_task.strip() == polished.practical_suggestion.strip():
        polished.weird_task = _safe_weird_task(intake)
    elif len((polished.weird_task or "").strip()) < 8:
        polished.weird_task = _safe_weird_task(intake)

    if chinese:
        if len((polished.alliance_reading or "").strip()) < 12 or "联盟成员" in polished.alliance_reading:
            polished.alliance_reading = "这个梦可以先当作昨晚情绪留下的一点信号，不需要急着解释，今天先照顾好现实里的节奏。"
        if polished.risk_level.strip() in {"低", "中", "高"}:
            polished.risk_level = f"{polished.risk_level.strip()}：适合温和处理，不需要把它当成预兆。"

    if not needs_escalation(merged):
        polished.safety_note = ""

    return polished


def intake_from_modalities(
    dream_text: str,
    image_path: Optional[str],
    audio_path: Optional[str],
    mood: str,
    vision_client,
    asr_client,
    user_context: str = "User wants a gentle next-day suggestion after vivid dreams.",
) -> DreamIntake:
    return build_intake(
        dream_text=dream_text or "",
        voice_transcript=asr_client.transcribe(audio_path),
        visual_clues=vision_client.extract_clues(image_path),
        mood=mood or "",
        user_context=user_context,
    )


def generate_negotiation(intake: DreamIntake, text_client) -> Dict:
    prompt = negotiation_prompt(intake)
    return text_client.generate_negotiation(prompt)


def generate_pact(intake: DreamIntake, answers: str, text_client) -> Tuple[PactCard, str]:
    prompt = pact_prompt(intake, answers)
    card = text_client.generate_pact(prompt)
    merged = intake.merged_text() + "\n" + answers
    card = _polish_card_for_daily_use(card, intake, answers)
    if needs_escalation(merged):
        card.safety_note = safety_note()
    card = _stamp_card_for_today(card)
    return card, render_pact_card(card)


def create_session() -> CustomsSession:
    return CustomsSession(
        events=[
            TimelineEvent(
                role="system",
                title="Dream Customs desk opened",
                body="Start with any fragment: a sentence, a sketch, a voice note, or just the mood left behind.",
                status="ready",
            )
        ]
    )


def _contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def _append_text(existing: str, new_text: str) -> str:
    new_text = new_text.strip()
    if not new_text:
        return existing
    if not existing.strip():
        return new_text
    if new_text in existing:
        return existing
    return f"{existing.strip()}\n{new_text}"


def _merge_unique(existing: List[str], incoming: List[str]) -> List[str]:
    seen = {item.strip().lower() for item in existing}
    merged = list(existing)
    for item in incoming:
        clean = item.strip()
        if clean and clean.lower() not in seen:
            merged.append(clean)
            seen.add(clean.lower())
    return merged


def _event(role: str, title: str, body: str = "", meta: str = "", status: str = "") -> TimelineEvent:
    return TimelineEvent(role=role, title=title, body=body, meta=meta, status=status)


def _record_safety(session: CustomsSession) -> None:
    merged = "\n".join([session.intake.merged_text(), session.answers_text()])
    if needs_escalation(merged) and "escalation" not in session.safety_flags:
        session.safety_flags.append("escalation")
        session.events.append(
            _event(
                "system",
                "Safety note attached",
                safety_note(),
                status="support",
            )
        )


def add_evidence(
    session: CustomsSession,
    dream_text: str = "",
    image_path: Optional[str] = None,
    audio_path: Optional[str] = None,
    mood: str = "",
    vision_client=None,
    asr_client=None,
) -> CustomsSession:
    next_session = session.model_copy(deep=True)
    added_items: List[EvidenceItem] = []

    if dream_text and dream_text.strip():
        clean_text = dream_text.strip()
        next_session.intake.dream_text = _append_text(next_session.intake.dream_text, clean_text)
        added_items.append(EvidenceItem(type="text", label="Dream note", status="selected", content=clean_text))

    if mood and mood.strip() and mood.strip() != next_session.intake.mood:
        next_session.intake.mood = mood.strip()
        added_items.append(EvidenceItem(type="mood", label=f"Mood: {mood.strip()}", status="selected", content=mood.strip()))

    if image_path:
        clues: List[str] = []
        error = ""
        try:
            clues = vision_client.extract_clues(image_path) if vision_client else []
        except Exception:
            clues = []
            error = "Image clue extraction failed. Text-only path remains available."
        if clues:
            next_session.intake.visual_clues = _merge_unique(next_session.intake.visual_clues, clues)
            added_items.append(
                EvidenceItem(
                    type="image",
                    label=f"Image clues ({len(clues)})",
                    status="extracted",
                    content=", ".join(clues),
                    source_path=image_path,
                )
            )
        else:
            added_items.append(
                EvidenceItem(
                    type="image",
                    label="Image evidence",
                    status="failed",
                    source_path=image_path,
                    error=error or "No visual clues extracted. Continue with text or voice.",
                )
            )

    if audio_path:
        transcript = ""
        error = ""
        try:
            transcript = asr_client.transcribe(audio_path) if asr_client else ""
        except Exception:
            error = "Voice transcription failed. Text-only path remains available."
        if transcript.strip():
            clean_transcript = transcript.strip()
            next_session.intake.voice_transcript = _append_text(next_session.intake.voice_transcript, clean_transcript)
            added_items.append(
                EvidenceItem(
                    type="audio",
                    label="Voice transcript",
                    status="extracted",
                    content=clean_transcript,
                    source_path=audio_path,
                )
            )
        else:
            added_items.append(
                EvidenceItem(
                    type="audio",
                    label="Voice evidence",
                    status="failed",
                    source_path=audio_path,
                    error=error or "No transcript returned. Continue by typing the fragment.",
                )
            )

    if not added_items:
        next_session.phase = "error"
        next_session.events.append(
            _event("error", "No material added", "Add text, image, or voice before asking the clerk.", status="empty")
        )
        return next_session

    next_session.evidence_items.extend(added_items)
    next_session.phase = "declaring"
    summary = "\n".join(f"{item.label}: {item.content or item.error}" for item in added_items)
    next_session.events.append(_event("user", "Material added", summary, status="filed"))
    _record_safety(next_session)
    return next_session


def ask_questions(session: CustomsSession, text_client, force_another: bool = False) -> CustomsSession:
    next_session = session.model_copy(deep=True)
    if not next_session.intake.merged_text():
        next_session.phase = "error"
        next_session.events.append(
            _event("error", "Customs has no declaration yet", "Add one dream fragment before asking a question.", status="empty")
        )
        return next_session

    prompt = (
        followup_question_prompt(next_session.intake, next_session.question_history, next_session.answer_history)
        if force_another
        else negotiation_prompt(next_session.intake)
    )
    negotiation = text_client.generate_negotiation(prompt)
    questions = [question for question in negotiation.get("questions", []) if question]
    fresh_questions = [question for question in questions if question not in next_session.question_history]
    if force_another and not fresh_questions:
        if _contains_cjk(next_session.intake.merged_text()):
            fresh_questions = ["如果海关只批准一个更小的动作，你希望今天先放行哪一件事？"]
        else:
            fresh_questions = ["If customs approves one smaller action today, which one should it release first?"]
    if not fresh_questions:
        fresh_questions = questions[:3]

    next_session.question_history.extend(fresh_questions[:3])
    next_session.phase = "negotiating"
    next_session.events.append(
        _event(
            "customs",
            "Customs question filed" if len(fresh_questions) == 1 else "Customs questions filed",
            "\n".join(fresh_questions[:3]),
            meta=str(negotiation.get("visitor_name", "")),
            status="question",
        )
    )
    return next_session


def answer_question(session: CustomsSession, answer: str) -> CustomsSession:
    next_session = session.model_copy(deep=True)
    if not answer or not answer.strip():
        next_session.phase = "error"
        next_session.events.append(
            _event("error", "No answer filed", "Write a reply, or choose to skip the question.", status="empty")
        )
        return next_session
    next_session.answer_history.append(answer.strip())
    next_session.phase = "negotiating"
    next_session.events.append(_event("user", "Answer filed", answer.strip(), status="answered"))
    _record_safety(next_session)
    return next_session


def skip_question(session: CustomsSession) -> CustomsSession:
    next_session = session.model_copy(deep=True)
    if _contains_cjk(next_session.intake.merged_text()):
        skip_text = "用户选择跳过这一轮问题。"
    else:
        skip_text = "The user chose to skip this question."
    next_session.answer_history.append(skip_text)
    next_session.phase = "negotiating"
    next_session.events.append(_event("user", "Question skipped", skip_text, status="skipped"))
    return next_session


def draft_pact(session: CustomsSession, text_client) -> CustomsSession:
    next_session = session.model_copy(deep=True)
    if not next_session.intake.merged_text():
        next_session.phase = "error"
        next_session.events.append(
            _event("error", "Pact needs dream material", "Add at least one fragment before drafting a pact.", status="empty")
        )
        return next_session

    answers = next_session.answers_text() or "The user has not answered yet; infer a gentle pact from the declaration."
    card, _html = generate_pact(next_session.intake, answers, text_client)
    next_session.draft_pact = card
    next_session.phase = "drafting"
    next_session.events.append(
        _event(
            "pact",
            "Draft pact prepared",
            f"{card.visitor_name}\n{card.practical_suggestion}\n{card.weird_task}",
            meta=card.permit_id,
            status="draft",
        )
    )
    _record_safety(next_session)
    return next_session


def _apply_revision_hint(card: PactCard, revision_request: str) -> PactCard:
    request = revision_request.lower()
    revised = card.model_copy(deep=True)
    cjk = _contains_cjk(" ".join([revision_request, card.visitor_name, card.alliance_reading]))
    if any(term in request for term in ["strange", "weird", "怪", "更奇怪", "更怪"]):
        revised.weird_task = (
            "把今天最小的任务写在纸上，给它盖一个看不见的放行章。"
            if cjk
            else "Write the smallest task on paper and stamp it with an invisible release mark."
        )
    elif any(term in request for term in ["gentle", "softer", "温和", "轻一点"]):
        revised.risk_level = (
            "浅橙色：先安置它，不急着解释它"
            if cjk
            else "soft orange: place it gently before interpreting it"
        )
        revised.practical_suggestion = (
            "今天先选一个不需要立刻完成的小开头，做 5 分钟就停。"
            if cjk
            else "Choose one start that does not need finishing today. Stop after five minutes."
        )
    elif revision_request.strip():
        revised.practical_suggestion = (
            f"{revised.practical_suggestion}（按你的修订请求：{revision_request.strip()}）"
            if cjk
            else f"{revised.practical_suggestion} Revision note: {revision_request.strip()}"
        )
    return revised


def revise_pact(session: CustomsSession, revision_request: str, text_client) -> CustomsSession:
    next_session = session.model_copy(deep=True)
    if not next_session.draft_pact:
        next_session = draft_pact(next_session, text_client)
        if not next_session.draft_pact:
            return next_session

    answers = next_session.answers_text()
    prompt = pact_revision_prompt(
        next_session.intake,
        answers,
        next_session.draft_pact.to_plain_text(),
        revision_request,
    )
    card = text_client.generate_pact(prompt)
    merged = next_session.intake.merged_text() + "\n" + answers
    if needs_escalation(merged):
        card.safety_note = safety_note()
    card = _apply_revision_hint(card, revision_request or "")
    card = _stamp_card_for_today(card)
    next_session.draft_pact = card
    next_session.phase = "drafting"
    next_session.events.append(
        _event(
            "pact",
            "Draft pact revised",
            revision_request.strip() or "The draft was tightened for today's smallest action.",
            meta=card.permit_id,
            status="revised",
        )
    )
    return next_session


def seal_pact(session: CustomsSession) -> CustomsSession:
    next_session = session.model_copy(deep=True)
    if not next_session.draft_pact:
        next_session.phase = "error"
        next_session.events.append(
            _event("error", "Nothing to seal yet", "Draft a pact before sealing today's agreement.", status="empty")
        )
        return next_session
    next_session.draft_pact = _stamp_card_for_today(next_session.draft_pact)
    next_session.sealed_pact = next_session.draft_pact
    next_session.phase = "sealed"
    next_session.events.append(
        _event(
            "pact",
            "Today's pact sealed",
            next_session.sealed_pact.bedtime_release,
            meta=next_session.sealed_pact.permit_id,
            status="sealed",
        )
    )
    return next_session
