import json

from scripts.local_space_mirror import load_runtime_env_json, mirror_manifest
from scripts.smoke_local_space_mirror import inspect_config


def test_local_space_mirror_manifest_matches_space_entrypoint():
    manifest = mirror_manifest("127.0.0.1", 7862)

    assert manifest["mode"] == "local-space-mirror"
    assert manifest["space_id"] == "build-small-hackathon/dream-customs"
    assert manifest["app_file"] == "app.py"
    assert manifest["url"] == "http://127.0.0.1:7862"
    assert manifest["default_backends"] == {
        "text": "modal",
        "vision": "modal",
        "asr": "modal",
    }
    assert manifest["env"]["text_endpoint_configured"] is False
    assert manifest["env"]["vision_endpoint_configured"] is False
    assert manifest["env"]["asr_endpoint_configured"] is False
    assert manifest["env"]["hosted_token_configured"] is False
    serialized_env = json.dumps(manifest["env"]).lower()
    assert "https://" not in serialized_env
    assert "secret" not in serialized_env


def test_local_space_mirror_loads_runtime_env_json_without_printing_values(tmp_path, monkeypatch):
    for key in [
        "DREAM_CUSTOMS_TEXT_ENDPOINT",
        "DREAM_CUSTOMS_VISION_ENDPOINT",
        "DREAM_CUSTOMS_ASR_ENDPOINT",
        "DREAM_CUSTOMS_HOSTED_TOKEN",
    ]:
        monkeypatch.delenv(key, raising=False)
    runtime_json = tmp_path / "runtime.json"
    runtime_json.write_text(
        json.dumps(
            {
                "DREAM_CUSTOMS_TEXT_ENDPOINT": "https://example.test/text",
                "DREAM_CUSTOMS_VISION_ENDPOINT": "https://example.test/vision",
                "DREAM_CUSTOMS_ASR_ENDPOINT": "https://example.test/asr",
                "DREAM_CUSTOMS_HOSTED_TOKEN": "super-secret-token",
                "UNRELATED": "ignored",
            }
        ),
        encoding="utf-8",
    )

    load_result = load_runtime_env_json(runtime_json)
    manifest = mirror_manifest("127.0.0.1", 7862)

    assert load_result["loaded"] is True
    assert "UNRELATED" not in load_result["configured_keys"]
    assert manifest["env"]["text_endpoint_configured"] is True
    assert manifest["env"]["vision_endpoint_configured"] is True
    assert manifest["env"]["asr_endpoint_configured"] is True
    assert manifest["env"]["hosted_token_configured"] is True
    serialized = json.dumps(manifest, ensure_ascii=False)
    assert "https://example.test" not in serialized
    assert "super-secret-token" not in serialized


def test_local_space_mirror_config_smoke_requires_composer_debug_markers():
    config = {
        "title": "Dream QA",
        "css": ".dc-stepper .dc-mic-button .dc-attach-button .dc-image-popover .dc-debug-panel",
        "components": [
            {"props": {"label": "Dream note"}},
            {"props": {"label": "Language"}},
            {"props": {"label": "Text generation", "value": "modal"}},
            {"props": {"label": "Image understanding", "value": "modal"}},
            {"props": {"label": "Voice input", "value": "modal"}},
            {"props": {"label": "Runtime state"}},
        ],
    }

    result = inspect_config(config)

    assert result["passes"] is True
    assert result["backend_defaults"]["Text generation"] == "modal"


def test_local_space_mirror_config_smoke_fails_on_stale_ui():
    config = {
        "title": "Dream QA",
        "css": ".dc-stepper",
        "components": [
            {"props": {"label": "Dream note"}},
            {"props": {"label": "Text generation", "value": "demo"}},
        ],
    }

    result = inspect_config(config)

    assert result["passes"] is False
    assert ".dc-mic-button" in result["failures"]["missing_css"]
    assert result["failures"]["backend_defaults"]["Text generation"] == "demo"
