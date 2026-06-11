#!/usr/bin/env python3
"""Run the Dream QA Hugging Face Space app locally for pre-merge review."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPACE_ID = "build-small-hackathon/dream-customs"


def _repo_root_on_path() -> None:
    root = str(ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def _configured_env() -> dict:
    return {
        "space_id": os.getenv("SPACE_ID", SPACE_ID),
        "text_endpoint_configured": bool(os.getenv("DREAM_CUSTOMS_TEXT_ENDPOINT", "").strip()),
        "vision_endpoint_configured": bool(os.getenv("DREAM_CUSTOMS_VISION_ENDPOINT", "").strip()),
        "asr_endpoint_configured": bool(os.getenv("DREAM_CUSTOMS_ASR_ENDPOINT", "").strip()),
        "hosted_token_configured": bool(os.getenv("DREAM_CUSTOMS_HOSTED_TOKEN", "").strip()),
    }


def mirror_manifest(host: str, port: int) -> dict:
    _repo_root_on_path()
    from dream_customs.defaults import DEFAULT_ASR_BACKEND, DEFAULT_TEXT_BACKEND, DEFAULT_VISION_BACKEND

    return {
        "mode": "local-space-mirror",
        "space_id": SPACE_ID,
        "url": f"http://{host}:{port}",
        "app_file": "app.py",
        "default_backends": {
            "text": DEFAULT_TEXT_BACKEND,
            "vision": DEFAULT_VISION_BACKEND,
            "asr": DEFAULT_ASR_BACKEND,
        },
        "env": _configured_env(),
        "notes": [
            "Uses the same app.py/build_demo path as the Hugging Face Space.",
            "Missing hosted endpoint secrets fall back to deterministic demo behavior.",
            "Do not print or store endpoint URLs or tokens in logs.",
        ],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.getenv("GRADIO_SERVER_NAME", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("GRADIO_SERVER_PORT", "7862")))
    parser.add_argument("--share", action="store_true", help="Create a public Gradio share link.")
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Print the local mirror manifest without starting Gradio.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    os.environ["GRADIO_SERVER_NAME"] = args.host
    os.environ["GRADIO_SERVER_PORT"] = str(args.port)
    os.environ.setdefault("SPACE_ID", SPACE_ID)
    os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")

    manifest = mirror_manifest(args.host, args.port)
    print(json.dumps(manifest, ensure_ascii=False, indent=2), flush=True)
    if args.manifest_only:
        return 0

    _repo_root_on_path()
    from app import demo

    demo.launch(
        server_name=args.host,
        server_port=args.port,
        show_api=False,
        show_error=True,
        share=args.share,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
