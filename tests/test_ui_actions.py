import json

from dream_customs.ui.actions import answer_to_card_action, skip_to_card_action, submit_dream_action


def test_mobile_mvp_submit_then_skip_auto_seals_pact():
    state, view_json = submit_dream_action(
        dream_text="我梦见迟到的电梯。",
        mood="焦虑",
    )
    view = json.loads(view_json)

    assert view["status"] == "question"
    assert view["question"]
    assert len(view["questions"]) == 1
    assert "DC-DEMO-014" not in view["card_text"]

    state, view_json = skip_to_card_action(state)
    view = json.loads(view_json)

    assert view["status"] == "card"
    assert view["phase"] == "sealed"
    assert "今日通行证" in view["card_title"]
    assert "DC-DEMO-014" in view["card_text"]
    assert "迟到的电梯" in view["card_html"]


def test_mobile_mvp_answer_to_card_auto_seals_pact():
    state, _view_json = submit_dream_action(
        dream_text="我梦见按钮融化，电梯一直不到。",
        mood="迷雾",
    )

    state, view_json = answer_to_card_action(state, "它可能是在让我慢一点。")
    view = json.loads(view_json)

    assert view["status"] == "card"
    assert view["phase"] == "sealed"
    assert "它可能是在让我慢一点。" in view["debug"]["session"]["answer_history"]
