import re
from datetime import date
from typing import Dict, List, Optional, Tuple

from dream_customs.prompts import (
    dream_brief_prompt,
    followup_question_prompt,
    negotiation_prompt,
    pact_critique_prompt,
    pact_draft_prompt,
    pact_prompt,
    pact_revision_prompt,
    pact_rewrite_prompt,
)
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


_ANCHOR_STOPWORDS = {
    "about",
    "after",
    "again",
    "an",
    "asked",
    "a",
    "before",
    "behind",
    "being",
    "carrying",
    "declare",
    "dream",
    "dreamed",
    "dreamt",
    "every",
    "feeling",
    "fragment",
    "from",
    "full",
    "into",
    "last",
    "left",
    "night",
    "paper",
    "promise",
    "through",
    "today",
    "the",
    "window",
    "with",
}


def _dedupe_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        clean = re.sub(r"\s+", " ", item.strip(" .,:;!?\"'()[]{}")).lower()
        if clean and clean not in seen:
            result.append(clean)
            seen.add(clean)
    return result


def _extract_dream_anchors(intake: DreamIntake) -> List[str]:
    text = " ".join(
        [
            intake.dream_text,
            intake.voice_transcript,
            " ".join(intake.visual_clues),
            " ".join(intake.recurring_symbols),
        ]
    ).lower()
    candidates: List[str] = []
    pair_pattern = re.compile(
        r"\b([a-z][a-z'-]+)\s+("
        r"paper|papers|promise|promises|window|windows|suitcase|suitcases|"
        r"clerk|clerks|sunrise|elevator|elevators|button|buttons|hallway|"
        r"gate|gates|floor|floors|stamp|stamps|number|numbers"
        r")\b"
    )
    for match in pair_pattern.finditer(text):
        modifier, noun = match.groups()
        phrase = f"{modifier} {noun.rstrip('s')}"
        if modifier not in _ANCHOR_STOPWORDS:
            candidates.append(phrase)

    noun_pattern = re.compile(
        r"\b(customs|suitcase|clerk|sunrise|elevator|button|hallway|gate|stamp|number|floor)\b"
    )
    candidates.extend(match.group(1) for match in noun_pattern.finditer(text))
    candidates.extend(clue.lower() for clue in intake.visual_clues if clue.strip())

    return _dedupe_preserve_order(candidates)[:3]


def _primary_anchor(intake: DreamIntake) -> str:
    anchors = _extract_dream_anchors(intake)
    return anchors[0] if anchors else "night visitor"


def _secondary_anchor(intake: DreamIntake) -> str:
    anchors = _extract_dream_anchors(intake)
    return anchors[1] if len(anchors) > 1 else _primary_anchor(intake)


def _title_anchor(text: str) -> str:
    return " ".join(part.capitalize() for part in text.split())


def _text_uses_anchor(text: str, anchors: List[str]) -> bool:
    clean = (text or "").lower()
    return any(anchor in clean for anchor in anchors)


def _is_generic_visitor_name(text: str, intake: DreamIntake) -> bool:
    clean = (text or "").strip()
    if not clean:
        return True
    lowered = clean.lower()
    merged = intake.merged_text().lower()
    generic_names = {"dreamer", "night visitor", "elena", "visitor", "the visitor"}
    if lowered in generic_names:
        return True
    anchors = _extract_dream_anchors(intake)
    if anchors and not _text_uses_anchor(lowered, anchors) and lowered not in merged and len(clean.split()) <= 2:
        return True
    return False


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
        "dream content has no medical value",
        "release stamp",
        "customs stamp",
        "clearance stamp",
        "magical",
    ]
    return any(term in clean for term in dream_literals)


def _is_generic_daily_tip(text: str, anchors: List[str]) -> bool:
    clean = (text or "").lower()
    generic_markers = [
        "hydrate",
        "dehydration",
        "piece of fruit",
        "cognitive function",
        "morning routine",
        "take a short walk",
        "eat something",
        "drink water",
    ]
    return any(marker in clean for marker in generic_markers) and not _text_uses_anchor(clean, anchors)


def _is_generic_weird_task(text: str, anchors: List[str]) -> bool:
    clean = (text or "").lower()
    generic_markers = [
        "count the number of birds",
        "requires no special skills",
        "harmless and playful activity",
        "salute the kettle",
    ]
    return any(marker in clean for marker in generic_markers) and not _text_uses_anchor(clean, anchors)


def _is_bare_time_or_generic_release(text: str) -> bool:
    clean = (text or "").strip()
    if re.fullmatch(r"\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)?", clean):
        return True
    if len(clean.split()) <= 3:
        return True
    return False


def _safe_practical_suggestion(intake: DreamIntake) -> str:
    mood = intake.mood.strip().lower()
    if mood in {"uneasy", "foggy", "tired", "焦虑", "迷雾", "累"}:
        return (
            "Start with one body-level reset today: drink water, eat something simple, "
            "then write the most important task as a 10-minute first step."
        )
    return "Do one low-risk stabilizing thing today: drink water, eat something, and write the most important task as a 10-minute first step."


def _safe_weird_task(intake: DreamIntake) -> str:
    return "Write your smallest task on paper, draw a tiny clearance stamp beside it, and work on it for just five minutes."


def _grounded_practical_suggestion(intake: DreamIntake) -> str:
    primary = _primary_anchor(intake)
    secondary = _secondary_anchor(intake)
    if "promise" in primary or "promise" in secondary:
        return (
            "Choose one unfinished promise and shrink it into a first step small enough to finish in "
            "10 minutes."
        )
    return (
        f"Pick one real task that feels like the {primary}, then define only its first step for the next 10 minutes."
    )


def _grounded_weird_task(intake: DreamIntake) -> str:
    primary = _primary_anchor(intake)
    secondary = _secondary_anchor(intake)
    if "paper" in primary or "paper" in secondary:
        return "Write one unfinished promise on a scrap of paper, fold it like a tiny suitcase, and stamp it cleared."
    if "customs" in primary or "customs" in secondary:
        return "Make a one-line customs form for today's smallest task and mark it cleared after five minutes."
    return f"Draw the {primary} as a tiny customs stamp, press it once, and work for five minutes."


def _grounded_bedtime_release(intake: DreamIntake) -> str:
    primary = _primary_anchor(intake)
    secondary = _secondary_anchor(intake)
    return f"Tonight, the {primary} and the {secondary} are logged, cleared, and allowed to rest until morning."


def _grounded_alliance_reading(intake: DreamIntake) -> str:
    primary = _primary_anchor(intake)
    secondary = _secondary_anchor(intake)
    return (
        f"You can treat the {primary} and the {secondary} as last night's way of asking for one promise "
        "to become smaller and easier to carry today."
    )


def _grounded_question(intake: DreamIntake, question: str) -> str:
    anchors = _extract_dream_anchors(intake)
    if not anchors or _text_uses_anchor(question, anchors):
        return question
    primary = _primary_anchor(intake)
    secondary = _secondary_anchor(intake)
    return (
        f"When you picture the {primary} and the {secondary}, what is one real-life promise "
        "or task you want to make easier today?"
    )


def _grounded_followup_question(intake: DreamIntake) -> str:
    primary = _primary_anchor(intake)
    return f"If the {primary} could hand you one smaller first step for today, what would that step be?"


def _polish_card_for_daily_use(card: PactCard, intake: DreamIntake, answers: str) -> PactCard:
    polished = card.model_copy(deep=True)
    merged = "\n".join([intake.merged_text(), answers or ""])
    anchors = _extract_dream_anchors(intake)
    if _is_generic_visitor_name(polished.visitor_name, intake):
        polished.visitor_name = _title_anchor(_primary_anchor(intake))

    if _looks_unclear_or_dream_literal(polished.practical_suggestion):
        polished.practical_suggestion = _safe_practical_suggestion(intake)
    elif _is_generic_daily_tip(polished.practical_suggestion, anchors):
        polished.practical_suggestion = _grounded_practical_suggestion(intake)
    elif anchors and not _text_uses_anchor(polished.practical_suggestion, anchors):
        polished.practical_suggestion = _grounded_practical_suggestion(intake)

    if _looks_unclear_or_dream_literal(polished.weird_task) and polished.weird_task.strip() == polished.practical_suggestion.strip():
        polished.weird_task = _safe_weird_task(intake)
    elif len((polished.weird_task or "").strip()) < 8:
        polished.weird_task = _safe_weird_task(intake)
    elif _is_generic_weird_task(polished.weird_task, anchors):
        polished.weird_task = _grounded_weird_task(intake)
    elif anchors and not _text_uses_anchor(polished.weird_task, anchors):
        polished.weird_task = _grounded_weird_task(intake)

    if (
        len((polished.alliance_reading or "").strip()) < 12
        or "联盟成员" in polished.alliance_reading
        or (anchors and not _text_uses_anchor(polished.alliance_reading, anchors))
    ):
        polished.alliance_reading = _grounded_alliance_reading(intake)
    if polished.risk_level.strip() in {"低", "中", "高", "low", "medium", "high"}:
        polished.risk_level = "medium: handle gently, without treating it as a warning sign"
    if _is_bare_time_or_generic_release(polished.bedtime_release) or (
        anchors and not _text_uses_anchor(polished.bedtime_release, anchors)
    ):
        polished.bedtime_release = _grounded_bedtime_release(intake)

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


def _clean_repeated_articles(text: str) -> str:
    clean = re.sub(r"\bthe\s+an\s+", "an ", text, flags=re.IGNORECASE)
    clean = re.sub(r"\bthe\s+the\s+", "the ", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\ban\s+an\s+", "an ", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\ba\s+a\s+", "a ", clean, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", clean).strip()


def _clean_card_grammar(card: PactCard) -> PactCard:
    cleaned = card.model_copy(deep=True)
    cleaned.visitor_name = _clean_repeated_articles(cleaned.visitor_name)
    cleaned.risk_level = _clean_repeated_articles(cleaned.risk_level)
    cleaned.alliance_reading = _clean_repeated_articles(cleaned.alliance_reading)
    cleaned.practical_suggestion = _clean_repeated_articles(cleaned.practical_suggestion)
    cleaned.weird_task = _clean_repeated_articles(cleaned.weird_task)
    cleaned.bedtime_release = _clean_repeated_articles(cleaned.bedtime_release)
    cleaned.contraband = [_clean_repeated_articles(item) for item in cleaned.contraband]
    return cleaned


def generate_model_led_pact(intake: DreamIntake, answers: str, text_client) -> Tuple[PactCard, str]:
    brief = text_client.generate_brief(dream_brief_prompt(intake))
    card = text_client.generate_pact_draft(pact_draft_prompt(brief, answers))
    critique = text_client.critique_pact(pact_critique_prompt(brief, card))
    if not critique.passes and critique.rewrite_instruction.strip():
        card = text_client.rewrite_pact(pact_rewrite_prompt(brief, card, critique))
    card = _clean_card_grammar(card)
    card = _polish_card_for_daily_use(card, intake, answers)
    merged = intake.merged_text() + "\n" + answers
    if needs_escalation(merged):
        card.safety_note = safety_note()
    else:
        card.safety_note = ""
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
        fresh_questions = ["If today only needs one smaller first step, what should that step be?"]
    if not fresh_questions:
        fresh_questions = questions[:3]
    if fresh_questions:
        fresh_questions = [_grounded_question(next_session.intake, fresh_questions[0])] + fresh_questions[1:]
    seen_questions = set(next_session.question_history)
    deduped_questions: List[str] = []
    for question in fresh_questions:
        if question and question not in seen_questions:
            deduped_questions.append(question)
            seen_questions.add(question)
    if force_another and not deduped_questions:
        deduped_questions = [_grounded_followup_question(next_session.intake)]
    fresh_questions = deduped_questions

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
    try:
        card, _html = generate_model_led_pact(next_session.intake, answers, text_client)
    except AttributeError:
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
    if any(term in request for term in ["strange", "weird", "怪", "更奇怪", "更怪"]):
        revised.weird_task = (
            "Write the smallest task on paper and stamp it with an invisible release mark."
        )
    elif any(term in request for term in ["gentle", "softer", "温和", "轻一点"]):
        revised.risk_level = (
            "soft orange: place it gently before interpreting it"
        )
        revised.practical_suggestion = (
            "Choose one start that does not need finishing today. Stop after five minutes."
        )
    elif revision_request.strip():
        revised.practical_suggestion = (
            f"{revised.practical_suggestion} Revision note: {revision_request.strip()}"
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
