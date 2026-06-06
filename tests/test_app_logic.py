import json

from dream_customs.app_logic import (
    _debug_json,
    add_material_action,
    ask_another_question_action,
    create_session,
    draft_pact_action,
    initial_workbench_state,
    run_customs_once,
    seal_pact_action,
    start_declaration_action,
)


def test_run_customs_once_generates_demo_outputs():
    negotiation, pact_text, html, debug_json = run_customs_once(
        dream_text="我梦见迟到的电梯。",
        mood="foggy",
        answers="我想先完成一件小事。",
    )
    debug = json.loads(debug_json)
    assert "Visitor:" in negotiation
    assert "Dream visitor:" in pact_text
    assert "Today's Pact" in html
    assert debug["status"] == "ok"
    assert debug["intake"]["dream_text"] == "我梦见迟到的电梯。"


def test_run_customs_once_requires_one_modality():
    negotiation, pact_text, html, debug_json = run_customs_once(dream_text="")
    assert negotiation == "No declaration received."
    assert "Please add text" in pact_text
    assert html == ""
    assert json.loads(debug_json) == {"status": "empty"}


def test_workbench_actions_progress_to_sealed_pact():
    state, _status, timeline, inspector, sealed_html, debug_json, _notice = initial_workbench_state()
    assert "Customs timeline" in timeline
    assert "No pact drafted yet" in inspector
    assert sealed_html == ""
    assert json.loads(debug_json)["status"] == "empty"

    state, _status, _timeline, _inspector, _sealed_html, debug_json, _notice = start_declaration_action(
        state,
        dream_text="I found a blue stamp in my pillow.",
        mood="curious",
    )
    debug = json.loads(debug_json)
    assert debug["status"] == "negotiating"
    assert debug["session"]["question_history"]

    state, _status, _timeline, inspector, _sealed_html, debug_json, _notice = draft_pact_action(state)
    assert json.loads(debug_json)["status"] == "drafting"
    assert "Pact inspector" in inspector

    state, _status, _timeline, _inspector, sealed_html, debug_json, _notice = seal_pact_action(state)
    assert json.loads(debug_json)["status"] == "sealed"
    assert "Today's Pact" in sealed_html


def test_workbench_model_route_without_endpoint_falls_back_to_demo():
    state, *_rest = initial_workbench_state(text_backend="model", vision_backend="model")
    state, _status, _timeline, _inspector, _sealed_html, debug_json, _notice = add_material_action(
        state,
        dream_text="Text-only path should stay alive.",
        text_backend="model",
        vision_backend="model",
    )
    state, _status, _timeline, _inspector, _sealed_html, debug_json, _notice = ask_another_question_action(
        state,
        text_backend="model",
        vision_backend="model",
    )
    debug = json.loads(debug_json)
    assert debug["text_backend"] == "model"
    assert debug["session"]["question_history"]


def test_debug_settings_do_not_expose_hosted_secrets():
    debug_json = _debug_json(
        create_session(),
        "modal",
        "huggingface",
        text_endpoint="https://modal.example/text",
        vision_endpoint="https://hf.example/vision",
        asr_endpoint="https://modal.example/asr",
        hosted_token="secret-token",
        text_latency_budget_ms=1234,
        vision_latency_budget_ms=5678,
        asr_latency_budget_ms=900,
    )
    debug = json.loads(debug_json)

    assert debug["developer_settings"]["text_endpoint_configured"] is True
    assert debug["developer_settings"]["vision_endpoint_configured"] is True
    assert debug["developer_settings"]["asr_endpoint_configured"] is True
    assert debug["developer_settings"]["hosted_token_configured"] is True
    assert debug["developer_settings"]["text_latency_budget_ms"] == 1234
    assert "secret-token" not in debug_json
    assert "modal.example" not in debug_json
