#!/usr/bin/env python3
"""Run the Dream QA Hugging Face Space app locally for pre-merge review."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
root = str(ROOT)
if root not in sys.path:
    sys.path.insert(0, root)

from dream_customs.runtime_env import (
    DEFAULT_RUNTIME_ENV_JSON,
    SPACE_ID,
    configured_env,
    load_runtime_env_json,
)


DEFAULT_LOCAL_HOST = "127.0.0.1"
DEFAULT_LOCAL_PORT = 7862


def _repo_root_on_path() -> None:
    root = str(ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


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
        "env": configured_env(SPACE_ID),
        "notes": [
            "Uses the same app.py/build_demo path as the Hugging Face Space.",
            "Missing hosted endpoint secrets fall back to deterministic demo behavior.",
            "Do not print or store endpoint URLs or tokens in logs.",
        ],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.getenv("GRADIO_SERVER_NAME", DEFAULT_LOCAL_HOST))
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("GRADIO_SERVER_PORT", str(DEFAULT_LOCAL_PORT))),
    )
    parser.add_argument("--share", action="store_true", help="Create a public Gradio share link.")
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Print the local mirror manifest without starting Gradio.",
    )
    parser.add_argument(
        "--runtime-env-json",
        type=Path,
        default=Path(os.getenv("DREAM_CUSTOMS_RUNTIME_ENV_JSON", DEFAULT_RUNTIME_ENV_JSON)),
        help=(
            "Load hosted endpoint/token secrets from a local JSON file before launching. "
            "Only configuration booleans are printed."
        ),
    )
    parser.add_argument(
        "--no-runtime-env-json",
        action="store_true",
        help="Do not auto-load the default local runtime env JSON.",
    )
    parser.add_argument(
        "--no-replace",
        action="store_true",
        help="Do not stop an older Dream QA local app that is already listening on the target port.",
    )
    return parser.parse_args(argv)


def _run_text(argv: list[str]) -> str:
    try:
        result = subprocess.run(argv, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _listener_pids(port: int) -> list[int]:
    output = _run_text(["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"])
    pids: list[int] = []
    for line in output.splitlines():
        try:
            pids.append(int(line.strip()))
        except ValueError:
            continue
    return pids


def _process_command(pid: int) -> str:
    return _run_text(["ps", "-p", str(pid), "-o", "command="])


def _process_cwd(pid: int) -> Path | None:
    output = _run_text(["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"])
    for line in output.splitlines():
        if line.startswith("n"):
            return Path(line[1:]).resolve()
    return None


def _is_repo_gradio_command(command: str) -> bool:
    return "scripts/local_space_mirror.py" in command or command.endswith(" app.py")


def _is_repo_local_gradio_process(pid: int) -> bool:
    cwd = _process_cwd(pid)
    command = _process_command(pid)
    return cwd == ROOT.resolve() and _is_repo_gradio_command(command)


def _wait_until_port_is_free(port: int, stopped_pids: list[int]) -> None:
    deadline = time.time() + 4
    while time.time() < deadline:
        remaining = [pid for pid in _listener_pids(port) if pid in stopped_pids]
        if not remaining:
            return
        time.sleep(0.2)
    raise RuntimeError(
        f"Stopped local Gradio process(es) {stopped_pids}, but port {port} is still busy."
    )


def stop_previous_local_app(port: int) -> list[int]:
    stopped_pids: list[int] = []
    for pid in _listener_pids(port):
        if pid == os.getpid() or not _is_repo_local_gradio_process(pid):
            continue
        os.kill(pid, signal.SIGTERM)
        stopped_pids.append(pid)
    if stopped_pids:
        _wait_until_port_is_free(port, stopped_pids)
    return stopped_pids


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    os.environ["GRADIO_SERVER_NAME"] = args.host
    os.environ["GRADIO_SERVER_PORT"] = str(args.port)
    os.environ.setdefault("SPACE_ID", SPACE_ID)
    os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")

    runtime_env = {"loaded": False, "reason": "disabled"}
    if not args.no_runtime_env_json:
        runtime_env = load_runtime_env_json(args.runtime_env_json)

    manifest = mirror_manifest(args.host, args.port)
    manifest["runtime_env_json"] = runtime_env
    if args.manifest_only or args.no_replace:
        manifest["replaced_local_pids"] = []
    else:
        manifest["replaced_local_pids"] = stop_previous_local_app(args.port)
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
