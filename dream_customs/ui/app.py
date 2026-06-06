import json
from html import escape

import gradio as gr
from gradio_client import utils as gradio_client_utils

from dream_customs.app_logic import (
    DEFAULT_ASR_LATENCY_BUDGET_MS,
    DEFAULT_ASR_TIMEOUT_SECONDS,
    DEFAULT_HOSTED_TIMEOUT_SECONDS,
    DEFAULT_TEXT_LATENCY_BUDGET_MS,
    DEFAULT_TEXT_MAX_TOKENS,
    DEFAULT_TEXT_MODEL,
    DEFAULT_TEXT_TEMPERATURE,
    DEFAULT_VISION_LATENCY_BUDGET_MS,
    DEFAULT_VISION_MAX_TOKENS,
    DEFAULT_VISION_MODEL,
    DEFAULT_VISION_TEMPERATURE,
)
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
    DEFAULT_MOOD,
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


def _settings_from_inputs(
    text_endpoint,
    vision_endpoint,
    hosted_token,
    ollama_url,
    text_model,
    vision_model,
    text_timeout_seconds,
    vision_timeout_seconds,
    text_temperature,
    vision_temperature,
    text_max_tokens,
    vision_max_tokens,
    asr_backend,
    asr_endpoint,
    asr_timeout_seconds,
    text_latency_budget_ms,
    vision_latency_budget_ms,
    asr_latency_budget_ms,
) -> dict:
    return {
        "text_endpoint": text_endpoint,
        "vision_endpoint": vision_endpoint,
        "hosted_token": hosted_token,
        "ollama_url": ollama_url,
        "text_model": text_model,
        "vision_model": vision_model,
        "text_timeout_seconds": text_timeout_seconds,
        "vision_timeout_seconds": vision_timeout_seconds,
        "text_temperature": text_temperature,
        "vision_temperature": vision_temperature,
        "text_max_tokens": text_max_tokens,
        "vision_max_tokens": vision_max_tokens,
        "asr_backend": asr_backend,
        "asr_endpoint": asr_endpoint,
        "asr_timeout_seconds": asr_timeout_seconds,
        "text_latency_budget_ms": text_latency_budget_ms,
        "vision_latency_budget_ms": vision_latency_budget_ms,
        "asr_latency_budget_ms": asr_latency_budget_ms,
    }


def _submit(dream_text, image_value, audio_value, mood, text_backend, vision_backend, *settings_values):
    settings = _settings_from_inputs(*settings_values)
    state, view_json = submit_dream_action(
        dream_text=dream_text,
        image_value=image_value,
        audio_value=audio_value,
        mood=mood,
        text_backend=text_backend,
        vision_backend=vision_backend,
        **settings,
    )
    return _updates(state, view_json)


def _answer(state, answer, text_backend, vision_backend, *settings_values):
    settings = _settings_from_inputs(*settings_values)
    state, view_json = answer_to_card_action(
        state,
        answer=answer,
        text_backend=text_backend,
        vision_backend=vision_backend,
        **settings,
    )
    return _updates(state, view_json)


def _skip(state, text_backend, vision_backend, *settings_values):
    settings = _settings_from_inputs(*settings_values)
    state, view_json = skip_to_card_action(
        state,
        text_backend=text_backend,
        vision_backend=vision_backend,
        **settings,
    )
    return _updates(state, view_json)


def _revise(state, revision_request, text_backend, vision_backend, *settings_values):
    settings = _settings_from_inputs(*settings_values)
    state, view_json = revise_card_action(
        state,
        revision_request=revision_request,
        text_backend=text_backend,
        vision_backend=vision_backend,
        **settings,
    )
    return _updates(state, view_json)


def _reset(text_backend, vision_backend, *settings_values):
    settings = _settings_from_inputs(*settings_values)
    state, view_json = reset_mobile_action(text_backend=text_backend, vision_backend=vision_backend, **settings)
    return (*_updates(state, view_json), "", "", None, None, DEFAULT_MOOD)


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
                with gr.Row(elem_classes=["dc-intake-grid"]):
                    with gr.Group(elem_classes=["dc-composer"]):
                        dream_text = gr.Textbox(
                            label="写下梦的碎片",
                            placeholder=DREAM_PLACEHOLDER,
                            lines=8,
                            value="",
                            elem_classes=["dc-dream-text"],
                        )
                        audio_input = gr.Audio(
                            label="语音线索",
                            sources=["microphone"],
                            type="filepath",
                            elem_classes=["dc-mic-input"],
                        )
                    with gr.Column(elem_classes=["dc-side-panel"]):
                        mood = gr.Dropdown(label="醒来后的感觉", choices=MOOD_OPTIONS, value=DEFAULT_MOOD)
                        gr.HTML(
                            """
<div class="dc-side-stamp">
  <span>Dream Customs</span>
  <strong>Calm clearance</strong>
</div>
""".strip()
                        )
                with gr.Row(elem_classes=["dc-submit-row"]):
                    example_button = gr.Button("试一个例子", variant="secondary")
                    submit_button = gr.Button("生成今日通行证", variant="primary")
                with gr.Accordion("附加材料", open=False, elem_classes=["dc-attachment-drawer"]):
                    image_input = gr.Image(label="图片线索", type="filepath", height=160)

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
                with gr.Row(elem_classes=["dc-dev-grid"]):
                    text_backend = gr.Radio(
                        label="文本后端",
                        choices=["demo", "model", "modal", "huggingface", "ollama"],
                        value=DEFAULT_TEXT_BACKEND,
                    )
                    vision_backend = gr.Radio(
                        label="视觉后端",
                        choices=["demo", "model", "modal", "huggingface", "ollama"],
                        value=DEFAULT_VISION_BACKEND,
                    )
                    asr_backend = gr.Radio(
                        label="ASR 后端",
                        choices=["demo", "modal", "huggingface"],
                        value="demo",
                    )
                with gr.Row(elem_classes=["dc-dev-grid"]):
                    text_endpoint = gr.Textbox(label="文本 Endpoint", value="")
                    vision_endpoint = gr.Textbox(label="视觉 Endpoint", value="")
                    asr_endpoint = gr.Textbox(label="ASR Endpoint", value="")
                hosted_token = gr.Textbox(label="Hosted Token", value="", type="password")
                with gr.Row(elem_classes=["dc-dev-grid"]):
                    text_model = gr.Textbox(label="文本模型", value=DEFAULT_TEXT_MODEL)
                    vision_model = gr.Textbox(label="视觉模型", value=DEFAULT_VISION_MODEL)
                    ollama_url = gr.Textbox(label="Ollama URL", value="http://localhost:11434")
                with gr.Row(elem_classes=["dc-dev-grid"]):
                    text_timeout_seconds = gr.Number(
                        label="文本超时秒",
                        value=DEFAULT_HOSTED_TIMEOUT_SECONDS,
                        precision=1,
                    )
                    vision_timeout_seconds = gr.Number(
                        label="视觉超时秒",
                        value=DEFAULT_HOSTED_TIMEOUT_SECONDS,
                        precision=1,
                    )
                    asr_timeout_seconds = gr.Number(
                        label="ASR 超时秒",
                        value=DEFAULT_ASR_TIMEOUT_SECONDS,
                        precision=1,
                    )
                with gr.Row(elem_classes=["dc-dev-grid"]):
                    text_latency_budget_ms = gr.Number(
                        label="Modal 文本延迟预算 ms",
                        value=DEFAULT_TEXT_LATENCY_BUDGET_MS,
                        precision=0,
                    )
                    vision_latency_budget_ms = gr.Number(
                        label="Modal 视觉延迟预算 ms",
                        value=DEFAULT_VISION_LATENCY_BUDGET_MS,
                        precision=0,
                    )
                    asr_latency_budget_ms = gr.Number(
                        label="ASR 延迟预算 ms",
                        value=DEFAULT_ASR_LATENCY_BUDGET_MS,
                        precision=0,
                    )
                with gr.Row(elem_classes=["dc-dev-grid"]):
                    text_temperature = gr.Slider(
                        label="文本温度",
                        minimum=0,
                        maximum=0.7,
                        step=0.05,
                        value=DEFAULT_TEXT_TEMPERATURE,
                    )
                    vision_temperature = gr.Slider(
                        label="视觉温度",
                        minimum=0,
                        maximum=0.7,
                        step=0.05,
                        value=DEFAULT_VISION_TEMPERATURE,
                    )
                with gr.Row(elem_classes=["dc-dev-grid"]):
                    text_max_tokens = gr.Slider(
                        label="文本 max tokens",
                        minimum=64,
                        maximum=1200,
                        step=16,
                        value=DEFAULT_TEXT_MAX_TOKENS,
                    )
                    vision_max_tokens = gr.Slider(
                        label="视觉 max tokens",
                        minimum=64,
                        maximum=800,
                        step=16,
                        value=DEFAULT_VISION_MAX_TOKENS,
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
        settings_inputs = [
            text_endpoint,
            vision_endpoint,
            hosted_token,
            ollama_url,
            text_model,
            vision_model,
            text_timeout_seconds,
            vision_timeout_seconds,
            text_temperature,
            vision_temperature,
            text_max_tokens,
            vision_max_tokens,
            asr_backend,
            asr_endpoint,
            asr_timeout_seconds,
            text_latency_budget_ms,
            vision_latency_budget_ms,
            asr_latency_budget_ms,
        ]

        submit_button.click(
            _submit,
            inputs=[dream_text, image_input, audio_input, mood, text_backend, vision_backend] + settings_inputs,
            outputs=outputs,
        )
        answer_button.click(
            _answer,
            inputs=[session_state, answer_text, text_backend, vision_backend] + settings_inputs,
            outputs=outputs,
        )
        skip_button.click(
            _skip,
            inputs=[session_state, text_backend, vision_backend] + settings_inputs,
            outputs=outputs,
        )
        gentle_button.click(
            _revise,
            inputs=[session_state, gr.State("再温柔一点"), text_backend, vision_backend] + settings_inputs,
            outputs=outputs,
        )
        weird_button.click(
            _revise,
            inputs=[session_state, gr.State("更怪一点"), text_backend, vision_backend] + settings_inputs,
            outputs=outputs,
        )
        copy_button.click(lambda text: text, inputs=card_text, outputs=card_text)
        reset_button.click(
            _reset,
            inputs=[text_backend, vision_backend] + settings_inputs,
            outputs=outputs + [dream_text, answer_text, image_input, audio_input, mood],
        )
        example_button.click(lambda: (EXAMPLE_DREAM, EXAMPLE_MOOD), outputs=[dream_text, mood])

    return demo
