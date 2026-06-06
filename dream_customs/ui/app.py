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

VOICE_JS = r"""
() => {
  const bindVoiceButton = () => {
    const button = document.querySelector(".dc-mic-button");
    const status = document.querySelector(".dc-mic-status");
    const textarea = document.querySelector(".dc-dream-text textarea");

    if (!button || !textarea || button.dataset.bound === "true") {
      return;
    }
    button.dataset.bound = "true";

    const setStatus = (message, mode) => {
      if (status) {
        status.textContent = message;
        status.dataset.mode = mode || "";
      }
      button.dataset.mode = mode || "";
      button.setAttribute("aria-label", message);
    };

    const appendTranscript = (text) => {
      const transcript = text.trim();
      if (!transcript) {
        return;
      }
      const spacer = textarea.value.trim() ? "\n" : "";
      textarea.value = `${textarea.value}${spacer}${transcript}`;
      textarea.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: transcript }));
      textarea.dispatchEvent(new Event("change", { bubbles: true }));
      textarea.focus();
    };

    button.addEventListener("click", async () => {
      const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!Recognition) {
        setStatus("当前浏览器不支持直接语音输入，可先手动输入，ASR 通道待接入。", "error");
        textarea.focus();
        return;
      }

      try {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          stream.getTracks().forEach((track) => track.stop());
        }
      } catch (error) {
        setStatus("没有获得麦克风权限，请允许浏览器录音后再试。", "error");
        return;
      }

      const recognition = new Recognition();
      recognition.lang = "zh-CN";
      recognition.interimResults = true;
      recognition.continuous = false;
      recognition.maxAlternatives = 1;

      let latestTranscript = "";

      recognition.onstart = () => {
        setStatus("正在听，把梦说出来。", "listening");
      };

      recognition.onresult = (event) => {
        latestTranscript = Array.from(event.results)
          .map((result) => result[0]?.transcript || "")
          .join("")
          .trim();
        if (latestTranscript) {
          setStatus(`正在记录：${latestTranscript}`, "listening");
        }
      };

      recognition.onerror = (event) => {
        const message = event.error === "not-allowed"
          ? "麦克风权限被拒绝，请允许录音后再试。"
          : "这次没有听清，可以再点一次话筒。";
        setStatus(message, "error");
      };

      recognition.onend = () => {
        if (latestTranscript) {
          appendTranscript(latestTranscript);
          setStatus("已写入梦境碎片。", "done");
        } else if (button.dataset.mode === "listening") {
          setStatus("没有检测到语音，可以再点一次话筒。", "idle");
        }
      };

      recognition.start();
    });
  };

  bindVoiceButton();
  const observer = new MutationObserver(bindVoiceButton);
  observer.observe(document.body, { childList: true, subtree: true });
}
"""


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
    question = escape(view.get("question") or "")
    optional_question = (
        f"<p class='dc-question-original'><span>可选问题</span>{question}</p>"
        if question
        else ""
    )
    return f"""
<div class="dc-question-card">
  <span class="dc-question-kicker">Optional check-in</span>
  <h2>还想补充一点吗？</h2>
  <p>如果你愿意，可以写下醒来后最想处理的一件现实小事，或者告诉我这个梦让你身体有什么感觉。</p>
  {optional_question}
  <p class="dc-question-note">不想补充也没关系，直接跳过就能生成今日通行证。</p>
</div>
""".strip()


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

    with gr.Blocks(css=CSS, js=VOICE_JS, title="梦境海关") as demo:
        session_state = gr.State(initial_state)
        view_state = gr.State(initial_view)

        with gr.Column(elem_classes=["dc-shell"]):
            gr.HTML(
                f"""
<header class="dc-hero">
  <div class="dc-hero-top">
    <div class="dc-menu-mark" aria-hidden="true"><span></span><span></span><span></span></div>
    <div class="dc-brand-lockup">
      <div class="dc-passport-icon" aria-hidden="true">
        <span class="dc-cloud-dot one"></span>
        <span class="dc-cloud-dot two"></span>
        <span class="dc-cloud-dot three"></span>
      </div>
      <div>
        <p class="dc-brand-kicker">DREAM CUSTOMS</p>
        <h1>{APP_TITLE}</h1>
        <p class="dc-brand-subtitle">A gentle dream declaration desk</p>
      </div>
    </div>
    <div class="dc-clearance-badge" aria-hidden="true">
      <span>Dream Clearance</span>
      <strong>DC-2026-0606</strong>
      <small>Status: Ready</small>
    </div>
  </div>
  <p class="dc-hero-copy">{APP_SUBTITLE}</p>
</header>
""".strip()
            )
            notice = gr.HTML(_notice_html(initial))

            with gr.Row(elem_classes=["dc-workspace-grid"]):
                with gr.Column(elem_classes=["dc-flow-column"]):
                    with gr.Group(visible=True, elem_classes=["dc-stage"]) as declaration_group:
                        with gr.Group(elem_classes=["dc-composer"]):
                            gr.HTML(
                                """
<div class="dc-section-title">
  <span class="dc-title-icon">1</span>
  <strong>Describe your dream</strong>
</div>
""".strip()
                            )
                            dream_text = gr.Textbox(
                                label="写下梦的碎片",
                                placeholder=DREAM_PLACEHOLDER,
                                lines=12,
                                value="",
                                elem_classes=["dc-dream-text"],
                            )
                            gr.HTML(
                                """
<div class="dc-mic-control">
  <button type="button" class="dc-mic-button" aria-label="点击话筒开始语音输入">
    <span class="dc-mic-glyph" aria-hidden="true"></span>
  </button>
  <div class="dc-mic-status" aria-live="polite">点击话筒开始语音输入</div>
</div>
""".strip()
                            )
                            audio_input = gr.State(None)
                            gr.HTML(
                                """
<p class="dc-field-tip">Tips: include people, places, emotions, colors, and anything that stood out.</p>
""".strip()
                            )
                        with gr.Row(elem_classes=["dc-submit-row"]):
                            example_button = gr.Button("清空并试一个例子  →", variant="secondary")
                            submit_button = gr.Button("盖章生成今日通行证  →", variant="primary")
                        with gr.Accordion("附加材料", open=False, elem_classes=["dc-attachment-drawer"]):
                            image_input = gr.Image(label="图片线索", type="filepath", height=160)

                    with gr.Group(visible=False, elem_classes=["dc-stage", "dc-question"]) as question_group:
                        question_markdown = gr.HTML(_question_markdown(initial))
                        answer_text = gr.Textbox(
                            label="你的补充",
                            placeholder=ANSWER_PLACEHOLDER,
                            lines=4,
                            value="",
                        )
                        with gr.Row(elem_classes=["dc-question-actions"]):
                            answer_button = gr.Button("用这条补充生成卡片", variant="primary")
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

                with gr.Column(elem_classes=["dc-side-panel"]):
                    gr.HTML(
                        """
<div class="dc-section-title">
  <span class="dc-title-icon">2</span>
  <strong>After waking feeling</strong>
</div>
""".strip()
                    )
                    mood = gr.Dropdown(label="醒来后的感觉", choices=MOOD_OPTIONS, value=DEFAULT_MOOD)
                    gr.HTML(
                        """
<div class="dc-side-stamp">
  <span>Dream Customs</span>
  <strong>Calm clearance</strong>
  <small>Gentle declarations</small>
</div>
""".strip()
                    )
                    with gr.Accordion("运行设置", open=True, elem_classes=["dc-dev"]):
                        gr.HTML(
                            """
<div class="dc-dev-help">
  <strong>给调试用，普通体验不用改。</strong>
  <span>自动模式会优先使用 Space 已配置的后端；没有端点时会安全回落到演示数据。</span>
</div>
""".strip()
                        )
                        text_backend = gr.Dropdown(
                            label="文字生成",
                            choices=[
                                ("自动：Space 已配置模型", "model"),
                                ("演示：稳定假数据", "demo"),
                                ("Modal/API：私有端点", "modal"),
                                ("本地 Ollama", "ollama"),
                            ],
                            value=DEFAULT_TEXT_BACKEND,
                        )
                        vision_backend = gr.Dropdown(
                            label="图片理解",
                            choices=[
                                ("自动：Space 已配置视觉模型", "model"),
                                ("演示：不调用图片模型", "demo"),
                                ("Modal/API：私有端点", "modal"),
                                ("本地 Ollama", "ollama"),
                            ],
                            value=DEFAULT_VISION_BACKEND,
                        )
                        asr_backend = gr.Dropdown(
                            label="语音输入",
                            choices=[
                                ("浏览器直接转写（当前）", "demo"),
                                ("Modal ASR 端点（待接入）", "modal"),
                                ("Hugging Face ASR 端点（待接入）", "huggingface"),
                            ],
                            value="demo",
                        )
                        with gr.Accordion("高级端点", open=False, elem_classes=["dc-dev-advanced"]):
                            text_endpoint = gr.Textbox(label="文字 Endpoint", value="")
                            vision_endpoint = gr.Textbox(label="图片 Endpoint", value="")
                            asr_endpoint = gr.Textbox(label="ASR Endpoint", value="")
                            hosted_token = gr.Textbox(label="Hosted Token", value="", type="password")
                            text_model = gr.Textbox(label="文字模型", value=DEFAULT_TEXT_MODEL)
                            vision_model = gr.Textbox(label="图片模型", value=DEFAULT_VISION_MODEL)
                            ollama_url = gr.Textbox(label="Ollama URL", value="http://localhost:11434")
                            text_timeout_seconds = gr.Number(
                                label="文字超时秒",
                                value=DEFAULT_HOSTED_TIMEOUT_SECONDS,
                                precision=1,
                            )
                            vision_timeout_seconds = gr.Number(
                                label="图片超时秒",
                                value=DEFAULT_HOSTED_TIMEOUT_SECONDS,
                                precision=1,
                            )
                            asr_timeout_seconds = gr.Number(
                                label="ASR 超时秒",
                                value=DEFAULT_ASR_TIMEOUT_SECONDS,
                                precision=1,
                            )
                            text_latency_budget_ms = gr.Number(
                                label="Modal 文字延迟预算 ms",
                                value=DEFAULT_TEXT_LATENCY_BUDGET_MS,
                                precision=0,
                            )
                            vision_latency_budget_ms = gr.Number(
                                label="Modal 图片延迟预算 ms",
                                value=DEFAULT_VISION_LATENCY_BUDGET_MS,
                                precision=0,
                            )
                            asr_latency_budget_ms = gr.Number(
                                label="ASR 延迟预算 ms",
                                value=DEFAULT_ASR_LATENCY_BUDGET_MS,
                                precision=0,
                            )
                            text_temperature = gr.Slider(
                                label="文字温度",
                                minimum=0,
                                maximum=0.7,
                                step=0.05,
                                value=DEFAULT_TEXT_TEMPERATURE,
                            )
                            vision_temperature = gr.Slider(
                                label="图片温度",
                                minimum=0,
                                maximum=0.7,
                                step=0.05,
                                value=DEFAULT_VISION_TEMPERATURE,
                            )
                            text_max_tokens = gr.Slider(
                                label="文字 max tokens",
                                minimum=64,
                                maximum=1200,
                                step=1,
                                value=DEFAULT_TEXT_MAX_TOKENS,
                            )
                            vision_max_tokens = gr.Slider(
                                label="图片 max tokens",
                                minimum=64,
                                maximum=800,
                                step=1,
                                value=DEFAULT_VISION_MAX_TOKENS,
                            )
                        debug_json = gr.Code(
                            label="当前状态",
                            value=json.dumps(initial.get("debug", {}), ensure_ascii=False, indent=2),
                            language="json",
                            visible=False,
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
