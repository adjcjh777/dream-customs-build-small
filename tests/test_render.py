from dream_customs.pipeline import add_evidence, create_session
from dream_customs.render import (
    render_pact_card,
    render_pact_inspector,
    render_status_bar,
    render_timeline,
    render_today_tip_card,
)
from dream_customs.schema import PactCard, TodayTipCard


def test_render_pact_card_contains_core_fields():
    html = render_pact_card(
        PactCard(
            visitor_name="Late Elevator",
            permit_id="DC-1",
            contraband=["unfiled anxiety"],
            risk_level="orange",
            alliance_reading="The dream asks for a smaller start.",
            practical_suggestion="Open one task ten minutes early.",
            weird_task="Write the elevator an apology note.",
            bedtime_release="Today the elevator has docked.",
        )
    )
    assert "Late Elevator" in html
    assert "Today&apos;s Pact" in html or "Today's Pact" in html
    assert "<script" not in html.lower()


def test_render_pact_card_escapes_user_like_content():
    html = render_pact_card(
        PactCard(
            visitor_name="<bad>",
            permit_id="DC-2",
            contraband=["<script>alert(1)</script>"],
            risk_level="green",
            alliance_reading="Maybe this visitor wants a smaller morning.",
            practical_suggestion="Drink water.",
            weird_task="Salute the kettle.",
            bedtime_release="The kettle is released.",
        )
    )
    assert "<bad>" not in html
    assert "<script" not in html.lower()


def test_render_pact_card_uses_night_desk_treatment():
    html = render_pact_card(
        PactCard(
            visitor_name="Late Elevator",
            permit_id="DC-1",
            contraband=["unfiled anxiety"],
            risk_level="orange",
            alliance_reading="The dream asks for a smaller start.",
            practical_suggestion="Open one task ten minutes early.",
            weird_task="Write the elevator an apology note.",
            bedtime_release="Today the elevator has docked.",
            safety_note="Reach out for support if you feel unsafe.",
        )
    )
    assert "oklch" in html
    assert "#fff8ea" not in html
    assert "border-left" not in html


def test_render_timeline_and_inspector_show_session_state():
    session = add_evidence(create_session(), dream_text="A blue gate opened.", mood="foggy")
    timeline = render_timeline(session)
    inspector = render_pact_inspector(session)
    assert "梦境问答流程" in timeline
    assert "Dream note" in timeline
    assert "还没有生成今日小 Tips" in inspector
    assert "2 filed" in inspector


def test_status_bar_is_status_not_fake_navigation():
    html = render_status_bar(create_session())
    assert "Current: Empty desk" in html
    assert "dc-phase-rail" not in html
    assert "<nav" not in html


def test_today_tip_card_prioritizes_tip_before_interpretation():
    html = render_today_tip_card(
        TodayTipCard(
            dream_summary="You dreamed about an elevator.",
            main_question="What feels hard to start?",
            dream_anchors=["floor 14", "elevator"],
            followup_questions=["What real task feels stuck?"],
            user_answers=["An overdue email feels hard to start."],
            interpretation="Maybe this dream is pointing to a stuck beginning.",
            today_tip="Open the overdue email and write only the first sentence.",
            tiny_action="Set a five-minute timer and stop after one sentence.",
            caring_note="One line is enough for now.",
        )
    )

    assert html.index("Today's small suggestion") < html.index("Maybe this dream is pointing to")
