from dream_customs.models import FakeTextClient
from dream_customs.pipeline import build_intake, generate_model_led_pact
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
    assert "emotional_hypothesis" in prompt
    assert "today_bridge" in prompt
    assert "safety_flags" in prompt
    assert "language" in prompt
    assert '"en"' in prompt
    assert "Return strict JSON" in prompt


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
    assert "Use visual_evidence if present" in prompt
    assert "elevator" in prompt
    assert "visitor_name" in prompt
    assert "permit_id" in prompt
    assert "contraband" in prompt
    assert "risk_level" in prompt
    assert "alliance_reading" in prompt
    assert "practical_suggestion" in prompt
    assert "weird_task" in prompt
    assert "bedtime_release" in prompt
    assert "safety_note" in prompt


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
    assert "passes" in prompt
    assert "issues" in prompt
    assert "rewrite_instruction" in prompt
    assert "diagnosis" in prompt
    assert "frightening certainty" in prompt
    assert "generic wellness" in prompt
    assert "missing anchors" in prompt


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
    assert "visitor_name" in prompt
    assert "permit_id" in prompt
    assert "contraband" in prompt
    assert "risk_level" in prompt
    assert "alliance_reading" in prompt
    assert "practical_suggestion" in prompt
    assert "weird_task" in prompt
    assert "bedtime_release" in prompt
    assert "safety_note" in prompt
    assert "safe non-diagnostic" in prompt
    assert "natural English" in prompt
    assert "Do not add objects" in prompt


def test_fake_text_client_supports_model_led_methods():
    client = FakeTextClient()

    brief = client.generate_brief("brief prompt")
    card = client.generate_pact_draft("draft prompt")
    critique = client.critique_pact("critique prompt")

    assert brief.language == "en"
    assert brief.anchors
    assert card.visitor_name
    assert critique.passes


def test_model_led_pact_rewrites_screenshot_elevator_regression():
    class CriticTextClient(FakeTextClient):
        def generate_pact_draft(self, prompt):
            return PactCard(
                visitor_name="An Elevator",
                permit_id="DREAM20260608-015",
                contraband=["melted buttons", "froze at 14"],
                risk_level="medium: handle gently, without treating it as a warning sign",
                alliance_reading="I am safe, but the wax is sticky and the floor is cold.",
                practical_suggestion="Pick one real task that feels like the an elevator.",
                weird_task="I will try to push the floor button with my hand instead of the lever.",
                bedtime_release="Tonight, the an elevator and the the button are logged.",
            )

        def critique_pact(self, prompt):
            return PactCritique(
                passes=False,
                issues=["repeated article", "invented lever"],
                rewrite_instruction="Rewrite without repeated articles or the invented lever.",
            )

        def rewrite_pact(self, prompt):
            return PactCard(
                visitor_name="The Elevator Stuck at 14",
                permit_id="DREAM20260608-015",
                contraband=["melted buttons", "floor 14", "the urge to freeze before starting"],
                risk_level="medium: handle gently, without treating it as a warning sign",
                alliance_reading=(
                    "The elevator, wax-soft buttons, and frozen 14 can be treated as a small scene "
                    "about getting stuck before the first move."
                ),
                practical_suggestion="Choose one stalled task and write only the next button-sized action.",
                weird_task="Draw floor 14 on a sticky note, tap it once, and spend five minutes on the first step.",
                bedtime_release=(
                    "Tonight, the elevator can stay on floor 14 while tomorrow's first button waits quietly."
                ),
            )

    intake = build_intake(
        dream_text="I kept missing an elevator. The buttons melted like wax, and the floor number froze at 14.",
        visual_clues=["Visible text: 14", "Object: melted elevator button"],
        mood="Uneasy",
    )

    card, html = generate_model_led_pact(intake, "", CriticTextClient())
    joined = card.to_plain_text().lower()

    assert "the an" not in joined
    assert "the the" not in joined
    assert "lever" not in joined
    assert "floor 14" in joined
    assert "melted" in joined or "wax" in joined
    assert "Today's Clearance Pass" in html or "Today's Pact" in html
