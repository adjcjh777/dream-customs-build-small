from datetime import date

from dream_customs.models import FakeASRClient, FakeTextClient, FakeVisionClient
from dream_customs.pipeline import (
    add_evidence,
    answer_question,
    ask_questions,
    build_intake,
    create_session,
    dated_permit_id,
    draft_pact,
    generate_negotiation,
    generate_pact,
    intake_from_modalities,
    revise_pact,
    seal_pact,
    skip_question,
)
from dream_customs.prompts import pact_prompt
from dream_customs.schema import PactCard


def test_dated_permit_id_uses_runtime_date_and_preserves_serial():
    assert dated_permit_id("DREAM2024-001", today=date(2026, 6, 6)) == "DREAM20260606-001"
    assert dated_permit_id("DC-DEMO-014", today=date(2026, 6, 6)) == "DREAM20260606-014"


def test_build_intake_merges_modalities():
    intake = build_intake(
        dream_text="I missed an elevator.",
        voice_transcript="The buttons melted.",
        visual_clues=["blue hallway"],
        mood="anxious",
    )
    assert "elevator" in intake.merged_text()
    assert "blue hallway" in intake.merged_text()


def test_intake_from_modalities_uses_adapters():
    intake = intake_from_modalities(
        dream_text="",
        image_path="demo.png",
        audio_path="demo.wav",
        mood="foggy",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
    )
    merged = intake.merged_text()
    assert "The buttons melted" in merged
    assert "blue hallway" in merged
    assert "Mood: foggy" in merged


def test_generate_negotiation_returns_questions():
    intake = build_intake(dream_text="I missed an elevator.", mood="anxious")
    negotiation = generate_negotiation(intake, FakeTextClient())
    assert negotiation["visitor_name"]
    assert len(negotiation["questions"]) == 3


def test_ask_questions_grounds_generic_question_in_dream_detail():
    session = add_evidence(
        create_session(),
        dream_text=(
            "I dreamed I was at a customs window carrying a suitcase full of wet paper. "
            "The clerk asked me to declare every unfinished promise before sunrise."
        ),
        mood="Uneasy",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
    )

    session = ask_questions(session, FakeTextClient())

    assert "customs window" in session.question_history[0].lower() or "wet paper" in session.question_history[0].lower()


def test_generate_pact_returns_card_and_html():
    intake = build_intake(dream_text="I missed an elevator.", mood="anxious")
    card, html = generate_pact(intake, "I want a small start.", FakeTextClient())
    assert card.visitor_name
    assert "Today's Pact" in html


def test_generate_pact_adds_safety_note_for_distress():
    intake = build_intake(dream_text="I might hurt myself if I cannot sleep.")
    card, _html = generate_pact(intake, "", FakeTextClient())
    assert card.safety_note


def test_generate_pact_polishes_unclear_model_output_into_daily_tip():
    class UnclearTextClient:
        def generate_pact(self, prompt):
            return PactCard(
                visitor_name="Dreamer",
                permit_id="DC-001",
                contraband=["融化蜡", "数字14"],
                risk_level="中",
                alliance_reading="联盟成员",
                practical_suggestion="明天早起观察电梯运行情况，若未超速可尝试模拟操作以熟悉流程。",
                weird_task="把今天最小的任务写在纸上，给它盖一个看不见的放行章。",
                bedtime_release="06:30",
                safety_note="梦境内容无医疗价值，建议保持冷静观察。",
            )

    intake = build_intake(dream_text="我梦见电梯按钮融化，数字停在 14。", mood="焦虑")
    card, html = generate_pact(intake, "", UnclearTextClient())

    assert card.visitor_name == "Night Visitor"
    assert "drink water" in card.practical_suggestion
    assert "电梯运行" not in card.practical_suggestion
    assert card.safety_note == ""
    assert "Life tip" in html


def test_generate_pact_repairs_generic_hosted_output_with_dream_details():
    class GenericHostedTextClient:
        def generate_pact(self, prompt):
            return PactCard(
                visitor_name="Elena",
                permit_id="DC-015",
                contraband=["unfiled worry", "one stamp asking to be noticed"],
                risk_level="medium",
                alliance_reading=(
                    "You can treat this as a small signal from last night's feelings, not a prophecy. "
                    "Today, protect a realistic pace."
                ),
                practical_suggestion=(
                    "Hydrate and eat a piece of fruit to support your morning routine, as dehydration "
                    "can affect cognitive function."
                ),
                weird_task=(
                    "Count the number of birds in the sky before bed, as it is a harmless and playful "
                    "activity that requires no special skills."
                ),
                bedtime_release="7:00 PM",
                safety_note="",
            )

    intake = build_intake(
        dream_text=(
            "I dreamed I was at a customs window carrying a suitcase full of wet paper. "
            "The clerk asked me to declare every unfinished promise before sunrise."
        ),
        mood="Uneasy",
    )

    card, html = generate_pact(intake, "", GenericHostedTextClient())
    joined = "\n".join(
        [
            card.visitor_name,
            card.alliance_reading,
            card.practical_suggestion,
            card.weird_task,
            card.bedtime_release,
        ]
    ).lower()

    assert "wet paper" in joined or "unfinished promise" in joined
    assert "customs window" in card.alliance_reading.lower() or "wet paper" in card.alliance_reading.lower()
    assert "promise" in card.practical_suggestion.lower() or "first step" in card.practical_suggestion.lower()
    assert any(anchor in card.weird_task.lower() for anchor in ["paper", "promise", "suitcase", "customs"])
    assert card.bedtime_release != "7:00 PM"
    assert "Hydrate and eat a piece of fruit" not in html


def test_pact_prompt_requires_dream_grounded_card():
    intake = build_intake(
        dream_text="I carried wet paper through a customs window before sunrise.",
        mood="Uneasy",
    )
    prompt = pact_prompt(intake, "I want to keep one promise small today.")

    assert "reuse at least two concrete dream details" in prompt
    assert "avoid generic wellness filler" in prompt
    assert "bedtime_release must be a sentence" in prompt
    assert "not a human name unless a person appears" in prompt


def test_add_evidence_updates_session_with_text_image_audio_and_mood():
    session = add_evidence(
        create_session(),
        dream_text="I dreamed the elevator buttons melted.",
        image_path="demo.png",
        audio_path="demo.wav",
        mood="anxious",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
    )
    assert session.phase == "declaring"
    assert "elevator" in session.intake.dream_text
    assert "blue hallway" in session.intake.visual_clues
    assert "The buttons melted" in session.intake.voice_transcript
    assert session.intake.mood == "anxious"
    assert {item.type for item in session.evidence_items} == {"text", "image", "audio", "mood"}


def test_ask_answer_skip_draft_revise_and_seal_actions():
    session = add_evidence(
        create_session(),
        dream_text="I missed an elevator.",
        mood="restless",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
    )
    session = ask_questions(session, FakeTextClient())
    assert session.phase == "negotiating"
    assert len(session.question_history) == 3

    session = answer_question(session, "I want one small start.")
    assert session.answer_history[-1] == "I want one small start."

    session = ask_questions(session, FakeTextClient(), force_another=True)
    assert len(session.question_history) == 4

    session = skip_question(session)
    assert "skip" in session.answer_history[-1].lower()

    session = draft_pact(session, FakeTextClient())
    assert session.phase == "drafting"
    assert session.draft_pact is not None

    original_task = session.draft_pact.weird_task
    session = revise_pact(session, "make it stranger", FakeTextClient())
    assert session.draft_pact is not None
    assert session.draft_pact.weird_task != original_task

    session = seal_pact(session)
    assert session.phase == "sealed"
    assert session.sealed_pact == session.draft_pact


def test_draft_pact_falls_back_to_legacy_generate_pact_client():
    class LegacyPactOnlyClient:
        def generate_pact(self, prompt):
            return PactCard(
                visitor_name="Legacy Elevator",
                permit_id="DC-014",
                contraband=["melted buttons"],
                risk_level="medium: handle gently, without treating it as a warning sign",
                alliance_reading="The elevator can be treated as a request for one smaller move.",
                practical_suggestion="Write one next step before touching the bigger task.",
                weird_task="Draw a tiny elevator button and press it once.",
                bedtime_release="Tonight, the elevator can wait quietly outside the room.",
            )

    session = add_evidence(
        create_session(),
        dream_text="I missed an elevator and the buttons melted.",
        mood="Uneasy",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
    )

    session = draft_pact(session, LegacyPactOnlyClient())

    assert session.phase == "drafting"
    assert session.draft_pact is not None
    assert session.draft_pact.visitor_name == "Legacy Elevator"


def test_image_audio_failures_keep_text_path_alive():
    class FailingVision:
        def extract_clues(self, image_path):
            raise RuntimeError("offline")

    class EmptyASR:
        def transcribe(self, audio_path):
            return ""

    session = add_evidence(
        create_session(),
        dream_text="Text still works.",
        image_path="missing.png",
        audio_path="missing.wav",
        mood="foggy",
        vision_client=FailingVision(),
        asr_client=EmptyASR(),
    )
    session = ask_questions(session, FakeTextClient())
    session = draft_pact(session, FakeTextClient())
    assert session.draft_pact is not None
    assert any(item.status == "failed" for item in session.evidence_items)
    assert "Text still works." in session.intake.dream_text
