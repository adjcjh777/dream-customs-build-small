import json

from scripts.local_space_mirror import mirror_manifest
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


def test_local_space_mirror_config_smoke_requires_composer_debug_markers():
    config = {
        "title": "Dream QA",
        "css": ".dc-stepper .dc-mic-button .dc-attachment-drawer .dc-debug-panel",
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
