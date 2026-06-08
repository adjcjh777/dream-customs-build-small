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


from dream_customs.schema import DreamBrief, PactCritique, VisionWitness


def test_vision_witness_flattens_report_into_demo_clues():
    witness = VisionWitness(
        scene_summary="A hand-drawn elevator panel is stuck on floor 14.",
        objects=["elevator button", "wax"],
        visible_text=["14"],
        spatial_relations=["button below the frozen number"],
        mood_cues=["stuck", "cold"],
        uncertain_details=["whether the floor is a basement"],
        surprising_detail="The buttons look melted rather than broken.",
    )

    clues = witness.to_visual_clues()

    assert clues[0] == "Scene: A hand-drawn elevator panel is stuck on floor 14."
    assert "Object: elevator button" in clues
    assert "Visible text: 14" in clues
    assert "Surprising detail: The buttons look melted rather than broken." in clues


def test_dream_brief_carries_evidence_and_demo_language():
    brief = DreamBrief(
        anchors=["elevator", "melted wax", "floor 14"],
        emotional_hypothesis="The dream may be protecting a fear of getting stuck.",
        today_bridge="Choose one stalled task and name the next small movement.",
        visual_evidence=["Visible text: 14"],
        safety_flags=[],
        language="en",
    )

    assert brief.language == "en"
    assert "floor 14" in brief.anchors
    assert brief.visual_evidence == ["Visible text: 14"]


def test_pact_critique_flags_template_and_grammar_failures():
    critique = PactCritique(
        passes=False,
        issues=["repeated article", "template fallback"],
        rewrite_instruction="Rewrite in natural English using elevator, wax, and floor 14.",
    )

    assert not critique.passes
    assert "repeated article" in critique.issues
    assert "natural English" in critique.rewrite_instruction
