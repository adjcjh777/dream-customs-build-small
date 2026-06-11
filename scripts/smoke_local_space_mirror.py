#!/usr/bin/env python3
"""Verify a running local Dream QA Space mirror."""

from __future__ import annotations

import argparse
import json
from typing import Any
from urllib.request import urlopen


REQUIRED_CSS_MARKERS = [
    ".dc-stepper",
    ".dc-mic-button",
    ".dc-attachment-drawer",
    ".dc-debug-panel",
]

REQUIRED_LABELS = [
    "Dream note",
    "Language",
    "Text generation",
    "Image understanding",
    "Voice input",
    "Runtime state",
]


def _component_labels(config: dict[str, Any]) -> set[str]:
    labels = set()
    for component in config.get("components", []):
        props = component.get("props") or {}
        label = props.get("label")
        if isinstance(label, str):
            labels.add(label)
    return labels


def _component_values(config: dict[str, Any]) -> dict[str, Any]:
    values = {}
    for component in config.get("components", []):
        props = component.get("props") or {}
        label = props.get("label")
        if isinstance(label, str):
            values[label] = props.get("value")
    return values


def inspect_config(config: dict[str, Any]) -> dict[str, Any]:
    css = config.get("css") or ""
    labels = _component_labels(config)
    values = _component_values(config)
    missing_css = [marker for marker in REQUIRED_CSS_MARKERS if marker not in css]
    missing_labels = [label for label in REQUIRED_LABELS if label not in labels]
    backend_defaults = {
        "Text generation": values.get("Text generation"),
        "Image understanding": values.get("Image understanding"),
        "Voice input": values.get("Voice input"),
    }
    backend_failures = {
        label: value for label, value in backend_defaults.items() if value != "modal"
    }
    title = config.get("title")
    failures = {}
    if title != "Dream QA":
        failures["title"] = title
    if missing_css:
        failures["missing_css"] = missing_css
    if missing_labels:
        failures["missing_labels"] = missing_labels
    if backend_failures:
        failures["backend_defaults"] = backend_failures
    return {
        "title": title,
        "component_count": len(config.get("components", [])),
        "backend_defaults": backend_defaults,
        "missing_css": missing_css,
        "missing_labels": missing_labels,
        "passes": not failures,
        "failures": failures,
    }


def fetch_config(base_url: str, timeout: float = 20.0) -> dict[str, Any]:
    with urlopen(f"{base_url.rstrip('/')}/config", timeout=timeout) as response:
        return json.load(response)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:7862")
    parser.add_argument("--timeout", type=float, default=20.0)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = inspect_config(fetch_config(args.url, timeout=args.timeout))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passes"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
