from dream_customs.pipeline import build_intake
from dream_customs.prompts import (
    dream_brief_prompt,
    pact_critique_prompt,
    pact_draft_prompt,
    pact_rewrite_prompt,
)
from dream_customs.schema import DreamBrief, PactCard, PactCritique


def test_dream_brief_prompt_requires_english_demo_brief():
    intake = build_intake(
        dream_text="I kept missing an elevator. The buttons melted like wax, and floor 14 froze.",
        visual_clues=["Visible text: 14", "Object: melted button"],
        mood="Uneasy",
    )

    prompt = dream_brief_prompt(intake)

    assert "English demo" in prompt
    assert "anchors" in prompt
    assert "visual_evidence" in prompt
    assert "Do not diagnose" in prompt


def test_pact_draft_prompt_uses_brief_not_template_fallback():
    brief = DreamBrief(
        anchors=["elevator", "melted wax", "floor 14"],
        emotional_hypothesis="The dream may be protecting a fear of getting stuck.",
        today_bridge="Choose one stalled task and name the next small movement.",
        visual_evidence=["Visible text: 14"],
    )

    prompt = pact_draft_prompt(brief, "I want to stop freezing before a task.")

    assert "Write natural English" in prompt
    assert "Use at least two anchors" in prompt
    assert "Do not use template phrases" in prompt
    assert "elevator" in prompt


def test_pact_critique_prompt_checks_screenshot_regression():
    brief = DreamBrief(
        anchors=["elevator", "melted wax", "floor 14"],
        emotional_hypothesis="The dream may be protecting a fear of getting stuck.",
        today_bridge="Choose one stalled task and name the next small movement.",
        visual_evidence=["Visible text: 14"],
    )
    card = PactCard(
        visitor_name="The Elevator",
        permit_id="DREAM20260608-014",
        contraband=["stuck feeling"],
        risk_level="low",
        alliance_reading="The an elevator is trying to keep you from rushing.",
        practical_suggestion="Take the the next small step.",
        weird_task="Tap an imaginary floor 14 button.",
        bedtime_release="The elevator can rest outside my room tonight.",
    )

    prompt = pact_critique_prompt(brief, card)

    assert "the an" in prompt
    assert "the the" in prompt
    assert "invented details" in prompt
    assert "natural English" in prompt


def test_pact_rewrite_prompt_uses_critique_instruction():
    brief = DreamBrief(
        anchors=["elevator", "melted wax", "floor 14"],
        emotional_hypothesis="The dream may be protecting a fear of getting stuck.",
        today_bridge="Choose one stalled task and name the next small movement.",
        visual_evidence=["Visible text: 14"],
    )
    card = PactCard(
        visitor_name="The Elevator",
        permit_id="DREAM20260608-014",
        contraband=["stuck feeling"],
        risk_level="low",
        alliance_reading="The an elevator is trying to keep you from rushing.",
        practical_suggestion="Take the the next small step.",
        weird_task="Tap an imaginary floor 14 button.",
        bedtime_release="The elevator can rest outside my room tonight.",
    )
    critique = PactCritique(
        passes=False,
        issues=["repeated article"],
        rewrite_instruction="Rewrite without repeated articles while preserving floor 14.",
    )

    prompt = pact_rewrite_prompt(brief, card, critique)

    assert "Rewrite without repeated articles" in prompt
    assert "Return strict JSON" in prompt
    assert "floor 14" in prompt
