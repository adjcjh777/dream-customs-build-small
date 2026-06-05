from dream_customs.schema import CustomsSession, DreamIntake, EvidenceItem, PactCard


def test_dream_intake_defaults_lists():
    intake = DreamIntake(dream_text="I missed an elevator.")
    assert intake.dream_text == "I missed an elevator."
    assert intake.visual_clues == []
    assert intake.recurring_symbols == []


def test_dream_intake_merged_text_includes_modalities():
    intake = DreamIntake(
        dream_text="I missed an elevator.",
        voice_transcript="The buttons melted.",
        visual_clues=["blue hallway"],
        mood="anxious",
        recurring_symbols=["elevator"],
        user_context="I slept badly.",
    )
    merged = intake.merged_text()
    assert "I missed an elevator." in merged
    assert "The buttons melted." in merged
    assert "blue hallway" in merged
    assert "Mood: anxious" in merged


def test_pact_card_requires_core_fields():
    card = PactCard(
        visitor_name="Late Elevator",
        permit_id="DC-0001",
        contraband=["unfiled anxiety"],
        risk_level="orange",
        alliance_reading="The dream asks for a smaller start.",
        practical_suggestion="Open one task ten minutes early.",
        weird_task="Write the elevator an apology note.",
        bedtime_release="Today the elevator has docked.",
    )
    assert card.safety_note == ""
    assert "Late Elevator" in card.to_plain_text()


def test_customs_session_defaults_to_empty_workbench():
    session = CustomsSession()
    assert session.phase == "empty"
    assert session.evidence_items == []
    assert session.question_history == []
    assert session.evidence_count() == 0


def test_evidence_item_tracks_failure_state():
    item = EvidenceItem(type="image", label="Image evidence", status="failed", error="No clues extracted")
    assert item.type == "image"
    assert item.status == "failed"
    assert "No clues" in item.error
