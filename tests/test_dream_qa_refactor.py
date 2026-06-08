import json

from dream_customs.models import FakeTextClient
from dream_customs.pipeline import (
    add_evidence,
    answer_question,
    ask_questions,
    create_session,
    finish_today_tip,
    generate_today_tip,
)
from dream_customs.render import render_today_tip_card
from dream_customs.schema import DreamQuestionIntake, DreamQAState, TodayTipCard
from dream_customs.ui.actions import submit_dream_action, skip_to_card_action
from dream_customs.ui.copy import APP_TITLE, PROCESSING_NOTE


def test_dream_qa_schema_contract_requires_grounded_tip():
    intake = DreamQuestionIntake(
        dream_text="我梦到老楼里的电梯按钮融化了。",
        main_question="这是不是和我最近拖延有关？",
    )
    state = DreamQAState.from_intake(
        intake,
        dream_summary="你梦见老楼里的电梯按钮融化。",
        dream_anchors=["老楼", "电梯按钮融化"],
        followup_questions=["梦里最强烈的是焦虑、荒诞，还是卡住？"],
    )
    card = TodayTipCard(
        dream_summary=state.dream_summary,
        main_question=state.main_question,
        dream_anchors=state.dream_anchors,
        followup_questions=state.followup_questions,
        user_answers=["更像是卡住。"],
        interpretation="也许这个梦把还没开始就担心来不及的感觉，演成了融化的电梯按钮。",
        today_tip="今天先把一件事缩小成一个按钮大小的第一步。",
    )

    assert card.references_dream_anchor()
    assert card.safety_note == ""
    assert "permit_id" not in card.model_dump()
    assert "contraband" not in card.model_dump()


def test_pipeline_progresses_record_ask_interpret_tip_without_pact_language():
    session = add_evidence(
        create_session(),
        dream_text="我梦到老楼里的电梯按钮融化了，数字停在 14。",
        mood="焦虑但有点滑稽",
    )
    assert session.phase == "record"

    session = ask_questions(session, FakeTextClient())
    assert session.phase == "ask"
    assert session.question_history

    session = answer_question(session, "像是还没开始就觉得来不及。")
    card = generate_today_tip(session.intake, session.answers_text(), FakeTextClient())
    assert card.references_dream_anchor()
    assert "电梯" in card.today_tip or "按钮" in card.today_tip or "14" in card.today_tip

    session = finish_today_tip(session, FakeTextClient())
    assert session.phase == "tip"
    assert session.sealed_tip is not None
    dumped = json.dumps(session.model_dump(mode="json"), ensure_ascii=False).lower()
    assert "contraband" not in dumped
    assert "sealed_pact" not in dumped


def test_render_today_tip_card_matches_new_public_contract():
    card = TodayTipCard(
        dream_summary="你梦见老楼里的电梯按钮融化，数字停在 14。",
        main_question="它是否和最近拖延有关？",
        dream_anchors=["电梯按钮融化", "数字 14"],
        followup_questions=["梦里最强烈的感受是什么？"],
        user_answers=["还没开始就觉得迟到。"],
        interpretation="也许这个梦不是预言，而是在提醒你把开始这件事变小。",
        today_tip="今天先按下一个很小的“电梯按钮”：只打开任务，不要求完成。",
        tiny_action="用 5 分钟写下今天要停靠的一层。",
        caring_note="你不需要一下子抵达所有楼层。",
    )

    html = render_today_tip_card(card)

    assert "今日小 Tips" in html
    assert "电梯按钮" in html
    assert "诊断" in html
    assert "permit" not in html.lower()
    assert "contraband" not in html.lower()
    assert "sealed" not in html.lower()


def test_mobile_action_payload_uses_today_tip_not_clearance_pass():
    state, view_json = submit_dream_action(
        dream_text="我梦到电梯按钮融化，楼层数字停在 14。",
        mood="焦虑",
        text_backend="demo",
        vision_backend="demo",
    )
    view = json.loads(view_json)

    assert view["status"] == "ask"
    assert view["question"]

    _state, view_json = skip_to_card_action(state, text_backend="demo", vision_backend="demo")
    view = json.loads(view_json)

    assert view["status"] == "tip"
    assert view["card_title"] == "今日小 Tips"
    assert "电梯" in view["card_text"] or "14" in view["card_text"]
    assert "clearance" not in view["card_text"].lower()
    assert "permit" not in view["card_html"].lower()
    assert "sealed" not in view["card_html"].lower()


def test_public_copy_is_dream_qa_not_customs_ritual():
    assert APP_TITLE == "梦境问答台"
    lowered = PROCESSING_NOTE.lower()
    assert "追问" in PROCESSING_NOTE
    assert "今日小 tips" in lowered
    assert "clerk" not in lowered
    assert "pass" not in lowered
