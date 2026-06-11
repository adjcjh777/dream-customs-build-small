from scripts.evaluate_agent_readiness import _agent_api_result, _load_agents_doc


def test_gradio_api_info_alias_matches_agent_endpoint():
    from fastapi.testclient import TestClient

    from app import demo

    response = TestClient(demo.app).get("/gradio_api/info")

    assert response.status_code == 200
    assert "/agent_dream_qa" in response.json()["named_endpoints"]


def test_agents_doc_is_present_and_agent_facing():
    result = _load_agents_doc("agents.md", None, timeout=1)

    assert result["passes"] is True
    assert result["issues"] == []


def test_agent_api_requires_text_only_public_endpoint():
    config = {
        "components": [
            {"id": 1, "type": "textbox"},
            {"id": 2, "type": "textbox"},
            {"id": 3, "type": "textbox"},
            {"id": 4, "type": "textbox"},
            {"id": 5, "type": "json"},
        ],
        "dependencies": [
            {
                "api_name": "agent_dream_qa",
                "inputs": [1, 2, 3, 4],
                "outputs": [5],
            }
        ],
    }

    result = _agent_api_result(config)

    assert result["passes"] is True
    assert result["agent_input_types"] == ["textbox", "textbox", "textbox", "textbox"]


def test_agent_dream_qa_returns_stable_flat_contract():
    from dream_customs.ui.app import _agent_dream_qa

    result = _agent_dream_qa(
        "I dreamed of a red room with no door.",
        mood="Uneasy",
        answer="I woke up nervous.",
        language="en",
    )

    assert result["api_contract"]["schema_version"] == "dream_qa.agent.v1"
    assert result["api_contract"]["route_mode"] == "text_only_queue"
    assert result["api_contract"]["expected_fields"] == ["dream_text", "mood", "answer", "language"]
    assert "text-only" in result["api_contract"]["media_note"]
    for key in [
        "dream_summary",
        "main_question",
        "dream_anchors",
        "followup_questions",
        "user_answers",
        "interpretation",
        "today_tip",
        "tiny_action",
        "caring_note",
        "safety_note",
    ]:
        assert key in result


def test_agent_dream_qa_rejects_empty_text_with_structured_error():
    from dream_customs.ui.app import _agent_dream_qa

    result = _agent_dream_qa("", mood="Uneasy", answer="", language="en")

    assert result["status"] == "error"
    assert result["error_code"] == "missing_dream_text"
    assert result["api_contract"]["expected_fields"] == ["dream_text", "mood", "answer", "language"]


def test_agent_api_fails_if_media_schema_is_public():
    config = {
        "components": [
            {"id": 1, "type": "textbox"},
            {"id": 2, "type": "image"},
            {"id": 3, "type": "json"},
        ],
        "dependencies": [
            {
                "api_name": "agent_dream_qa",
                "inputs": [1, 2],
                "outputs": [3],
            },
            {"api_name": "_submit", "inputs": [1, 2], "outputs": [3]},
        ],
    }

    result = _agent_api_result(config)

    assert result["passes"] is False
    assert "agent_api_requires_media_schema" in result["issues"]
    assert "ui_events_exposed_as_public_api" in result["issues"]
