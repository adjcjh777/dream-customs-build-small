import os

import gradio as gr
from gradio_client import utils as gradio_client_utils

from dream_customs.app_logic import run_customs_once


_ORIGINAL_SCHEMA_TO_TYPE = gradio_client_utils._json_schema_to_python_type


def _json_schema_to_python_type(schema, defs):
    # Gradio 4.44 can pass JSON Schema booleans here on newer dependency sets.
    if isinstance(schema, bool):
        return "Any" if schema else "None"
    return _ORIGINAL_SCHEMA_TO_TYPE(schema, defs)


gradio_client_utils._json_schema_to_python_type = _json_schema_to_python_type


CSS = """
body { background: #f6f1e7; }
.gradio-container {
  color: #17272f;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.dc-shell {
  max-width: 1180px;
  margin: 0 auto;
}
.dc-title h1 {
  font-size: clamp(30px, 5vw, 56px);
  line-height: 1;
  margin-bottom: 4px;
}
.dc-title p {
  color: #49626b;
  font-size: 16px;
  margin-top: 0;
}
.dc-stamp button {
  background: #17313b !important;
  border: 0 !important;
  color: #fff8ed !important;
  font-weight: 800 !important;
}
textarea, input, select {
  font-size: 16px !important;
}
@media (max-width: 760px) {
  .dc-title h1 { font-size: 34px; }
  .dc-title p { font-size: 14px; }
}
"""


def build_demo() -> gr.Blocks:
    with gr.Blocks(css=CSS, title="Dream Customs") as demo:
        with gr.Column(elem_classes=["dc-shell"]):
            gr.Markdown(
                """
                # Dream Customs / 梦境海关
                夜间来访者入境申报处
                """,
                elem_classes=["dc-title"],
            )
            with gr.Row():
                with gr.Column(scale=5):
                    dream_text = gr.Textbox(
                        label="Dream declaration",
                        lines=8,
                        value="我梦见一部迟到的电梯，按钮都融化了，我一直到不了 14 楼。",
                    )
                    with gr.Row():
                        image_input = gr.Image(label="Image evidence", type="filepath")
                        audio_input = gr.Audio(label="Voice evidence", type="filepath")
                    mood = gr.Dropdown(
                        label="Current weather",
                        choices=["foggy", "anxious", "curious", "tired", "restless", "calm"],
                        value="foggy",
                    )
                    answers = gr.Textbox(
                        label="Answers to the clerk",
                        lines=4,
                        value="我想和它结盟，但今天只想完成一件很小的事。",
                    )
                    with gr.Row():
                        text_backend = gr.Radio(
                            label="Text engine",
                            choices=["demo", "ollama"],
                            value="demo",
                        )
                        vision_backend = gr.Radio(
                            label="Vision engine",
                            choices=["demo", "ollama"],
                            value="demo",
                        )
                    submit = gr.Button("Stamp clearance", elem_classes=["dc-stamp"])

                with gr.Column(scale=6):
                    negotiation = gr.Textbox(label="Customs questions", lines=7)
                    pact_text = gr.Textbox(label="Pact manifest", lines=12)
                    pact_html = gr.HTML(label="Today's pact card")
                    debug_json = gr.Code(label="Debug manifest", language="json")

            submit.click(
                run_customs_once,
                inputs=[dream_text, image_input, audio_input, mood, answers, text_backend, vision_backend],
                outputs=[negotiation, pact_text, pact_html, debug_json],
            )

            gr.Examples(
                examples=[
                    [
                        "梦见一间便利店漂在海上，收银员让我用旧日历付款。",
                        "curious",
                        "我想知道它到底在保护什么。",
                    ],
                    [
                        "I found a tiny border checkpoint inside my pillow. The officer stamped my hand with blue ink.",
                        "restless",
                        "I want a small action that makes tomorrow less loud.",
                    ],
                ],
                inputs=[dream_text, mood, answers],
            )
    return demo


demo = build_demo()


if __name__ == "__main__":
    server_name = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    server_port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
    demo.launch(server_name=server_name, server_port=server_port, show_api=False, show_error=True)
