import json
from datetime import date

from dream_customs.ui.actions import answer_to_card_action, initial_mobile_state, skip_to_card_action, submit_dream_action
from dream_customs.ui.app import _reset
from dream_customs.ui.copy import DEFAULT_MOOD


def test_mobile_defaults_to_model_backends():
    _state, view_json = initial_mobile_state()
    view = json.loads(view_json)

    assert view["debug"]["text_backend"] == "model"
    assert view["debug"]["vision_backend"] == "model"


def test_mobile_reset_restores_calm_mood():
    settings_values = [
        "",
        "",
        "",
        "http://localhost:11434",
        "hf.co/openbmb/MiniCPM5-1B-GGUF:Q8_0",
        "openbmb/minicpm-v4.6",
        60,
        60,
        0.2,
        0.1,
        780,
        320,
        "demo",
        "",
        45,
        3500,
        6500,
        2500,
    ]
    result = _reset("demo", "demo", *settings_values)

    assert result[-1] == DEFAULT_MOOD


def test_zerogpu_probe_is_importable_without_local_gpu():
    from dream_customs.zerogpu import zerogpu_startup_probe

    assert zerogpu_startup_probe() == {"status": "ok", "purpose": "zerogpu-startup-detection"}


def test_mobile_mvp_submit_then_skip_auto_seals_pact():
    state, view_json = submit_dream_action(
        dream_text="我梦见迟到的电梯。",
        mood="焦虑",
        text_backend="demo",
        vision_backend="demo",
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
    assert f"DREAM{date.today():%Y%m%d}-014" in view["card_text"]
    assert "DC-DEMO-014" not in view["card_text"]
    assert "迟到的电梯" in view["card_html"]


def test_mobile_mvp_answer_to_card_auto_seals_pact():
    state, _view_json = submit_dream_action(
        dream_text="我梦见按钮融化，电梯一直不到。",
        mood="迷雾",
        text_backend="demo",
        vision_backend="demo",
    )

    state, view_json = answer_to_card_action(state, "它可能是在让我慢一点。", text_backend="demo", vision_backend="demo")
    view = json.loads(view_json)

    assert view["status"] == "card"
    assert view["phase"] == "sealed"
    assert "它可能是在让我慢一点。" in view["debug"]["session"]["answer_history"]
