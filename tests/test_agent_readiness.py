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
