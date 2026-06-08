import json
import inspect
from datetime import date

from dream_customs.ui.actions import answer_to_card_action, initial_mobile_state, skip_to_card_action, submit_dream_action
import dream_customs.ui.app as ui_app
from dream_customs.ui.app import _reset
from dream_customs.ui.copy import DEFAULT_MOOD, PROCESSING_NOTE


def test_mobile_defaults_to_model_backends():
    _state, view_json = initial_mobile_state()
    view = json.loads(view_json)

    assert view["debug"]["text_backend"] == "model"
    assert view["debug"]["vision_backend"] == "model"


def test_runtime_settings_are_collapsed_for_public_flow():
    source = inspect.getsource(ui_app.build_demo)

    assert 'gr.Accordion("Runtime settings", open=False' in source


def test_processing_note_is_story_copy_not_backend_jargon():
    lowered = PROCESSING_NOTE.lower()

    assert "grounded question" in lowered
    assert "today tip" in lowered
    assert "model routes" in lowered
    assert "fallback" in lowered
    assert "token" not in lowered
    assert "endpoint" not in lowered
    assert "debug" not in lowered


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


def test_mobile_mvp_submit_then_skip_generates_today_tip():
    state, view_json = submit_dream_action(
        dream_text="I dreamed of a late elevator.",
        mood="Uneasy",
        text_backend="demo",
        vision_backend="demo",
    )
    view = json.loads(view_json)

    assert view["status"] == "ask"
    assert view["question"]
    assert len(view["questions"]) == 1
    assert "DC-DEMO-014" not in view["card_text"]

    state, view_json = skip_to_card_action(state)
    view = json.loads(view_json)

    assert view["status"] == "tip"
    assert view["phase"] == "tip"
    assert "Today Tip" in view["card_title"]
    assert "电梯" in view["card_text"] or "elevator" in view["card_text"].lower()
    assert "DC-DEMO-014" not in view["card_text"]
    assert "Today Tip" in view["card_html"]


def test_mobile_mvp_zh_language_switch_keeps_chinese_today_tip():
    state, _view_json = submit_dream_action(
        dream_text="我梦到电梯按钮融化，楼层数字停在 14。",
        mood="焦虑",
        text_backend="demo",
        vision_backend="demo",
        language="zh",
    )
    _state, view_json = skip_to_card_action(
        state,
        text_backend="demo",
        vision_backend="demo",
        language="zh",
    )
    view = json.loads(view_json)

    assert view["language"] == "zh"
    assert view["card_title"] == "今日小 Tips"
    assert "今日小 Tips" in view["card_html"]


def test_mobile_mvp_answer_to_card_generates_today_tip():
    state, _view_json = submit_dream_action(
        dream_text="I dreamed the elevator buttons melted and the elevator never came.",
        mood="Foggy",
        text_backend="demo",
        vision_backend="demo",
    )

    state, view_json = answer_to_card_action(
        state,
        "It may be asking me to slow down.",
        text_backend="demo",
        vision_backend="demo",
    )
    view = json.loads(view_json)

    assert view["status"] == "tip"
    assert view["phase"] == "tip"
    assert "It may be asking me to slow down." in view["debug"]["session"]["answer_history"]
