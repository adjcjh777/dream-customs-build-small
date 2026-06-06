import json
from html import escape

import gradio as gr
from gradio_client import utils as gradio_client_utils

from dream_customs.defaults import DEFAULT_TEXT_BACKEND, DEFAULT_VISION_BACKEND
from dream_customs.ui.actions import (
    answer_to_card_action,
    initial_mobile_state,
    reset_mobile_action,
    revise_card_action,
    skip_to_card_action,
    submit_dream_action,
)
from dream_customs.ui.copy import (
    ANSWER_PLACEHOLDER,
    APP_SUBTITLE,
    APP_TITLE,
    DREAM_PLACEHOLDER,
    EXAMPLE_DREAM,
    EXAMPLE_MOOD,
    MOOD_OPTIONS,
)
from dream_customs.ui.styles import CSS


_ORIGINAL_SCHEMA_TO_TYPE = gradio_client_utils._json_schema_to_python_type


def _json_schema_to_python_type(schema, defs):
    if isinstance(schema, bool):
        return "Any" if schema else "None"
    return _ORIGINAL_SCHEMA_TO_TYPE(schema, defs)


gradio_client_utils._json_schema_to_python_type = _json_schema_to_python_type


def _load_view(view_json: str) -> dict:
    try:
        return json.loads(view_json or "{}")
    except json.JSONDecodeError:
        return {"status": "error", "error": "界面状态解析失败，请重新申报。"}


def _notice_html(view: dict) -> str:
    message = escape(view.get("notice") or view.get("error") or "")
    css = "dc-notice is-error" if view.get("status") == "error" else "dc-notice"
    return f"<div class='{css}'>{message}</div>" if message else ""


def _question_markdown(view: dict) -> str:
    question = view.get("question") or ""
    return f"## 海关想确认一件小事\n\n{question}" if question else "## 海关还在等梦的碎片"


def _updates(state: str, view_json: str):
    view = _load_view(view_json)
    status = view.get("status", "declaration")
    return (
        state,
        view_json,
        _notice_html(view),
        _question_markdown(view),
        view.get("card_html", ""),
        view.get("card_text", ""),
        gr.update(visible=status in {"declaration", "error"}),
        gr.update(visible=status == "question"),
        gr.update(visible=status == "card"),
        json.dumps(view.get("debug", {}), ensure_ascii=False, indent=2),
    )


def _submit(dream_text, image_value, audio_value, mood, text_backend, vision_backend):
    state, view_json = submit_dream_action(
        dream_text=dream_text,
        image_value=image_value,
        audio_value=audio_value,
        mood=mood,
        text_backend=text_backend,
        vision_backend=vision_backend,
    )
    return _updates(state, view_json)


def _answer(state, answer, text_backend, vision_backend):
    state, view_json = answer_to_card_action(
        state,
        answer=answer,
        text_backend=text_backend,
        vision_backend=vision_backend,
    )
    return _updates(state, view_json)


def _skip(state, text_backend, vision_backend):
    state, view_json = skip_to_card_action(
        state,
        text_backend=text_backend,
        vision_backend=vision_backend,
    )
    return _updates(state, view_json)


def _revise(state, revision_request, text_backend, vision_backend):
    state, view_json = revise_card_action(
        state,
        revision_request=revision_request,
        text_backend=text_backend,
        vision_backend=vision_backend,
    )
    return _updates(state, view_json)


def _reset(text_backend, vision_backend):
    state, view_json = reset_mobile_action(text_backend=text_backend, vision_backend=vision_backend)
    return (*_updates(state, view_json), "", "", None, None, "")


def build_demo() -> gr.Blocks:
    initial_state, initial_view = initial_mobile_state()
    initial = _load_view(initial_view)

    with gr.Blocks(css=CSS, title="梦境海关") as demo:
        session_state = gr.State(initial_state)
        view_state = gr.State(initial_view)

        with gr.Column(elem_classes=["dc-shell"]):
            gr.HTML(
                f"""
<header class="dc-hero">
  <h1>{APP_TITLE}</h1>
  <p>{APP_SUBTITLE}</p>
</header>
""".strip()
            )
            notice = gr.HTML(_notice_html(initial))

            with gr.Group(visible=True, elem_classes=["dc-stage"]) as declaration_group:
                dream_text = gr.Textbox(
                    label="写下梦的碎片",
                    placeholder=DREAM_PLACEHOLDER,
                    lines=7,
                    value="",
                )
                with gr.Row(elem_classes=["dc-row"]):
                    image_input = gr.Image(label="图片线索", type="filepath")
                    audio_input = gr.Audio(label="语音线索", sources=["microphone", "upload"], type="filepath")
                    mood = gr.Dropdown(label="醒来后的感觉", choices=MOOD_OPTIONS, value=None)
                with gr.Row():
                    example_button = gr.Button("试一个例子", variant="secondary")
                    submit_button = gr.Button("生成今日通行证", variant="primary")

            with gr.Group(visible=False, elem_classes=["dc-stage", "dc-question"]) as question_group:
                question_markdown = gr.Markdown("## 海关还在等梦的碎片")
                answer_text = gr.Textbox(
                    label="你的回答",
                    placeholder=ANSWER_PLACEHOLDER,
                    lines=3,
                    value="",
                )
                with gr.Row():
                    answer_button = gr.Button("回答并生成卡片", variant="primary")
                    skip_button = gr.Button("跳过，直接生成", variant="secondary")

            with gr.Group(visible=False, elem_classes=["dc-stage", "dc-card"]) as card_group:
                card_html = gr.HTML("")
                with gr.Row(elem_classes=["dc-actions"]):
                    gentle_button = gr.Button("再温柔一点", variant="secondary")
                    weird_button = gr.Button("更怪一点", variant="secondary")
                    copy_button = gr.Button("复制文本", variant="secondary")
                    reset_button = gr.Button("重新申报", variant="secondary")
                card_text = gr.Textbox(
                    label="可复制文本",
                    value="",
                    lines=8,
                    show_copy_button=True,
                    elem_classes=["dc-hidden-text"],
                )

            with gr.Accordion("开发者设置", open=False, elem_classes=["dc-dev"]):
                with gr.Row():
                    text_backend = gr.Radio(
                        label="文本后端",
                        choices=["demo", "model", "ollama"],
                        value=DEFAULT_TEXT_BACKEND,
                    )
                    vision_backend = gr.Radio(
                        label="视觉后端",
                        choices=["demo", "model", "ollama"],
                        value=DEFAULT_VISION_BACKEND,
                    )
                debug_json = gr.Code(
                    label="调试状态",
                    value=json.dumps(initial.get("debug", {}), ensure_ascii=False, indent=2),
                    language="json",
                )

        outputs = [
            session_state,
            view_state,
            notice,
            question_markdown,
            card_html,
            card_text,
            declaration_group,
            question_group,
            card_group,
            debug_json,
        ]

        submit_button.click(
            _submit,
            inputs=[dream_text, image_input, audio_input, mood, text_backend, vision_backend],
            outputs=outputs,
        )
        answer_button.click(
            _answer,
            inputs=[session_state, answer_text, text_backend, vision_backend],
            outputs=outputs,
        )
        skip_button.click(
            _skip,
            inputs=[session_state, text_backend, vision_backend],
            outputs=outputs,
        )
        gentle_button.click(
            _revise,
            inputs=[session_state, gr.State("再温柔一点"), text_backend, vision_backend],
            outputs=outputs,
        )
        weird_button.click(
            _revise,
            inputs=[session_state, gr.State("更怪一点"), text_backend, vision_backend],
            outputs=outputs,
        )
        copy_button.click(lambda text: text, inputs=card_text, outputs=card_text)
        reset_button.click(
            _reset,
            inputs=[text_backend, vision_backend],
            outputs=outputs + [dream_text, answer_text, image_input, audio_input, mood],
        )
        example_button.click(lambda: (EXAMPLE_DREAM, EXAMPLE_MOOD), outputs=[dream_text, mood])

    return demo
