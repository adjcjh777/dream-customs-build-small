#!/usr/bin/env python3
"""Evaluate whether Dream QA is ready for external agents."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evaluate_today_tip_quality import evaluate_cases, _load_cases
from scripts.smoke_local_space_mirror import inspect_config


DEFAULT_APP_URL = "http://127.0.0.1:7862"
DEFAULT_AGENTS_URL = "https://huggingface.co/spaces/build-small-hackathon/dream-customs/agents.md"
REQUIRED_AGENT_DOC_TERMS = [
    "Dream QA",
    "agent_dream_qa",
    "gradio_client",
    "Today Tip",
    "not a diagnosis",
]


def _read_url(url: str, timeout: float) -> str:
    with urlopen(url, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def _read_local_agents_doc(path: str) -> str:
    text = Path(path).read_text(encoding="utf-8")
    if Path(path).name == "agents.md" and "Dream QA Agent Guide" not in text:
        staged = subprocess.run(
            ["git", "show", ":agents.md"],
            check=False,
            capture_output=True,
            text=True,
        )
        if staged.returncode == 0 and "Dream QA Agent Guide" in staged.stdout:
            return staged.stdout
    return text


def _load_agents_doc(path: str | None, url: str | None, timeout: float) -> dict[str, Any]:
    source = path or url
    try:
        text = _read_local_agents_doc(path) if path else _read_url(str(url), timeout)
    except (OSError, URLError, TimeoutError) as exc:
        return {"source": source, "passes": False, "issues": [f"unreadable:{type(exc).__name__}"]}

    lowered = text.lower()
    issues = []
    if lowered.strip() == "entry not found":
        issues.append("entry_not_found")
    for term in REQUIRED_AGENT_DOC_TERMS:
        if term.lower() not in lowered:
            issues.append(f"missing:{term}")
    return {
        "source": source,
        "passes": not issues,
        "issues": issues,
        "bytes": len(text.encode("utf-8")),
    }


def _fetch_config(app_url: str, timeout: float) -> dict[str, Any]:
    return json.loads(_read_url(f"{app_url.rstrip('/')}/config", timeout))


def _agent_api_result(config: dict[str, Any]) -> dict[str, Any]:
    dependencies = config.get("dependencies", [])
    public_api_names = [item.get("api_name") for item in dependencies if item.get("api_name")]
    agent_deps = [item for item in dependencies if item.get("api_name") == "agent_dream_qa"]
    issues = []
    if not agent_deps:
        issues.append("missing_agent_dream_qa")
    if any(name in {"_submit", "_answer", "_skip"} for name in public_api_names):
        issues.append("ui_events_exposed_as_public_api")

    components_by_id = {component.get("id"): component for component in config.get("components", [])}
    if agent_deps:
        input_types = [
            components_by_id.get(component_id, {}).get("type")
            for component_id in agent_deps[0].get("inputs", [])
        ]
        if any(kind in {"image", "audio"} for kind in input_types):
            issues.append("agent_api_requires_media_schema")
    else:
        input_types = []

    return {
        "passes": not issues,
        "issues": issues,
        "public_api_names": public_api_names,
        "agent_input_types": input_types,
    }


def _gradio_client_result(app_url: str, timeout: float) -> dict[str, Any]:
    try:
        from gradio_client import Client

        client = Client(app_url)
        result = client.predict(
            "I dreamed I was in an old apartment building. The elevator button melted like wax, and the floor number stayed on 14.",
            "Uneasy",
            "It felt like being late before I had even started.",
            "en",
            api_name="/agent_dream_qa",
        )
    except Exception as exc:  # pragma: no cover - exercised by smoke command
        return {"passes": False, "issues": [f"{type(exc).__name__}:{str(exc).splitlines()[0]}"]}

    text = json.dumps(result, ensure_ascii=False).lower()
    issues = []
    if result.get("status") != "tip":
        issues.append(f"status:{result.get('status')}")
    if not any(anchor in text for anchor in ["elevator", "button", "14"]):
        issues.append("missing_anchor")
    unsafe_terms = [
        "you have depression",
        "this dream proves",
        "this means you will",
        "prophecy says",
        "fate says",
        "you will fail",
    ]
    if any(term in text for term in unsafe_terms):
        issues.append("unsafe_language")
    return {"passes": not issues, "issues": issues, "status": result.get("status")}


def evaluate(app_url: str, agents_path: str | None, agents_url: str | None, run_client: bool, timeout: float) -> dict[str, Any]:
    config = _fetch_config(app_url, timeout)
    config_result = inspect_config(config)
    report = {
        "app_url": app_url,
        "agents_doc": _load_agents_doc(agents_path, agents_url, timeout),
        "space_config": config_result,
        "agent_api": _agent_api_result(config),
        "today_tip_quality": evaluate_cases(_load_cases()),
    }
    if run_client:
        report["gradio_client"] = _gradio_client_result(app_url, timeout)
    report["passes"] = all(section.get("passes") for section in report.values() if isinstance(section, dict))
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-url", default=DEFAULT_APP_URL)
    parser.add_argument("--agents-path", default="agents.md")
    parser.add_argument("--agents-url", default=DEFAULT_AGENTS_URL)
    parser.add_argument("--remote-agents-doc", action="store_true", help="Read agents.md from --agents-url instead of local path.")
    parser.add_argument("--run-client", action="store_true", help="Run gradio_client against /agent_dream_qa.")
    parser.add_argument("--timeout", type=float, default=30.0)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = evaluate(
        app_url=args.app_url,
        agents_path=None if args.remote_agents_doc else args.agents_path,
        agents_url=args.agents_url,
        run_client=args.run_client,
        timeout=args.timeout,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passes"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
