import json

from dream_customs.app_logic import (
    _clients,
    _client_settings,
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
from dream_customs.defaults import DEFAULT_ASR_BACKEND, DEFAULT_TEXT_BACKEND, DEFAULT_VISION_BACKEND
from dream_customs.models import HostedASRClient, HostedMiniCPMTextClient, HostedMiniCPMVisionClient


def test_defaults_use_modal_model_entrypoint():
    assert DEFAULT_TEXT_BACKEND == "modal"
    assert DEFAULT_VISION_BACKEND == "modal"
    assert DEFAULT_ASR_BACKEND == "modal"


def test_run_customs_once_generates_demo_outputs():
    negotiation, pact_text, html, debug_json = run_customs_once(
        dream_text="I dreamed of a late elevator.",
        mood="foggy",
        answers="I want to start one small thing first.",
    )
    debug = json.loads(debug_json)
    assert "Visitor:" in negotiation
    assert "Today Tip" in pact_text
    assert "Today Tip" in html
    assert debug["status"] == "ok"
    assert debug["intake"]["dream_text"] == "I dreamed of a late elevator."


def test_run_customs_once_requires_one_modality():
    negotiation, pact_text, html, debug_json = run_customs_once(dream_text="")
    assert negotiation == "还没有收到梦境记录。"
    assert "请先添加文字" in pact_text
    assert html == ""
    assert json.loads(debug_json) == {"status": "empty"}


def test_workbench_actions_progress_to_today_tip():
    state, _status, timeline, inspector, sealed_html, debug_json, _notice = initial_workbench_state()
    assert "梦境问答流程" in timeline
    assert "还没有生成今日小 Tips" in inspector
    assert sealed_html == ""
    assert json.loads(debug_json)["status"] == "empty"

    state, _status, _timeline, _inspector, _sealed_html, debug_json, _notice = start_declaration_action(
        state,
        dream_text="I found a blue stamp in my pillow.",
        mood="curious",
    )
    debug = json.loads(debug_json)
    assert debug["status"] == "ask"
    assert debug["session"]["question_history"]

    state, _status, _timeline, _inspector, sealed_html, debug_json, _notice = seal_pact_action(state)
    assert json.loads(debug_json)["status"] == "tip"
    assert "Today Tip" in sealed_html


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


def test_developer_settings_configure_hosted_clients():
    text_client, vision_client, asr_client = _clients(
        "modal",
        "huggingface",
        text_endpoint="https://modal.example/text",
        vision_endpoint="https://hf.example/vision",
        asr_backend="modal",
        asr_endpoint="https://modal.example/asr",
        hosted_token="secret-token",
        text_timeout_seconds=12,
        vision_timeout_seconds=34,
        asr_timeout_seconds=5,
        text_temperature=0.42,
        vision_temperature=0.22,
        text_max_tokens=256,
        vision_max_tokens=128,
    )

    assert isinstance(text_client, HostedMiniCPMTextClient)
    assert isinstance(vision_client, HostedMiniCPMVisionClient)
    assert isinstance(asr_client, HostedASRClient)
    assert text_client.endpoint == "https://modal.example/text"
    assert vision_client.endpoint == "https://hf.example/vision"
    assert asr_client.endpoint == "https://modal.example/asr"
    assert text_client.timeout == 12
    assert vision_client.timeout == 34
    assert asr_client.timeout == 5
    assert text_client.temperature == 0.42
    assert vision_client.temperature == 0.22
    assert text_client.max_tokens == 256
    assert vision_client.max_tokens == 128


def test_asr_endpoint_derives_from_modal_text_endpoint_when_secret_is_missing():
    settings = _client_settings(
        text_endpoint="https://workspace--dream-customs-minicpm-backend-text.modal.run",
        asr_endpoint="",
    )

    assert settings["asr_endpoint"] == "https://workspace--dream-customs-minicpm-backend-asr.modal.run"
