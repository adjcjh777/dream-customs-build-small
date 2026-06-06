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

    assert card.visitor_name == "昨夜来访者"
    assert "喝水" in card.practical_suggestion
    assert "电梯运行" not in card.practical_suggestion
    assert card.safety_note == ""
    assert "Life tip" in html


def test_add_evidence_updates_session_with_text_image_audio_and_mood():
    session = add_evidence(
        create_session(),
        dream_text="我梦见电梯按钮融化。",
        image_path="demo.png",
        audio_path="demo.wav",
        mood="anxious",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
    )
    assert session.phase == "declaring"
    assert "电梯" in session.intake.dream_text
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
