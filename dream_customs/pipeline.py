from typing import Dict, List, Optional, Tuple

from dream_customs.prompts import negotiation_prompt, pact_prompt
from dream_customs.render import render_pact_card
from dream_customs.safety import needs_escalation, safety_note
from dream_customs.schema import DreamIntake, PactCard


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
    if needs_escalation(merged):
        card.safety_note = safety_note()
    return card, render_pact_card(card)
