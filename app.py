import os
import tempfile

from gradio.routes import App
from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse

from dream_customs import zerogpu  # noqa: F401
from dream_customs.app_logic import _clients
from dream_customs.runtime_env import auto_load_runtime_env_json
from dream_customs.ui.app import build_demo


auto_load_runtime_env_json()
demo = build_demo()


_ORIGINAL_CREATE_APP = App.create_app


def _install_gradio_api_aliases(app, blocks) -> None:
    existing_paths = {getattr(route, "path", "") for route in app.routes}

    if "/dream-asr" not in existing_paths:
        @app.post("/dream-asr", include_in_schema=False)
        async def dream_asr(request: Request) -> JSONResponse:
            """Transcribe a browser-recorded voice note through the server-side ASR client."""

            form = await request.form()
            upload = form.get("audio")
            if upload is None or not hasattr(upload, "read"):
                return JSONResponse(
                    {"status": "error", "transcript": "", "error": "Missing audio."},
                    status_code=400,
                )

            filename = str(getattr(upload, "filename", "") or "dream-voice.webm")
            suffix = os.path.splitext(filename)[1] or ".webm"
            temp_path = ""
            try:
                audio_bytes = await upload.read()
                if not audio_bytes:
                    return JSONResponse(
                        {"status": "error", "transcript": "", "error": "Empty audio."},
                        status_code=400,
                    )
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                    temp_file.write(audio_bytes)
                    temp_path = temp_file.name
                _text_client, _vision_client, asr_client = _clients("demo", "demo")
                transcript = asr_client.transcribe(temp_path)
            finally:
                if temp_path:
                    try:
                        os.unlink(temp_path)
                    except OSError:
                        pass

            if not transcript:
                return JSONResponse(
                    {"status": "error", "transcript": "", "error": "No transcript returned."},
                    status_code=502,
                )
            return JSONResponse({"status": "ok", "transcript": transcript})

    if "/gradio_api/info" not in existing_paths:
        @app.get("/gradio_api/info", include_in_schema=False)
        async def gradio_api_info_alias() -> JSONResponse:
            """Compatibility for Hugging Face's generated agents.md schema URL."""

            return JSONResponse(blocks.get_api_info())

    async def _redirect_to_gradio4_path(request: Request) -> RedirectResponse:
        suffix = request.url.path.removeprefix("/gradio_api")
        target = suffix or "/"
        if request.url.query:
            target = f"{target}?{request.url.query}"
        return RedirectResponse(url=target, status_code=307)

    for alias_path in (
        "/gradio_api/queue/join",
        "/gradio_api/queue/data",
        "/gradio_api/upload",
    ):
        if alias_path not in existing_paths:
            app.add_api_route(
                alias_path,
                _redirect_to_gradio4_path,
                methods=["GET", "POST"],
                include_in_schema=False,
            )


def _create_app_with_gradio_api_aliases(blocks, app_kwargs=None, auth_dependency=None):
    app = _ORIGINAL_CREATE_APP(blocks, app_kwargs=app_kwargs, auth_dependency=auth_dependency)
    _install_gradio_api_aliases(app, blocks)
    return app


App.create_app = staticmethod(_create_app_with_gradio_api_aliases)
_install_gradio_api_aliases(demo.app, demo)


if __name__ == "__main__":
    demo.launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
        show_api=False,
        show_error=True,
    )
