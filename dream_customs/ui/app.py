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
from dream_customs.defaults import DEFAULT_ASR_BACKEND, DEFAULT_TEXT_BACKEND, DEFAULT_VISION_BACKEND
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
    APP_COPY,
    APP_SUBTITLE,
    APP_TITLE,
    DEFAULT_LANGUAGE,
    DREAM_PLACEHOLDER,
    DEFAULT_MOOD,
    LANGUAGE_OPTIONS,
    MOOD_OPTIONS,
    PROCESSING_NOTE,
    copy_for,
    default_mood_for,
    mood_options_for,
    normalize_language,
    EXAMPLE_DREAMS,
    EXAMPLE_MOODS,
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

    const messageFor = (key, fallback) => button.dataset[key] || fallback;

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
        setStatus(messageFor("unsupported", "This browser cannot transcribe voice here. You can still type the dream."), "error");
        textarea.focus();
        return;
      }

      setStatus(messageFor("checking", "Checking microphone permission..."), "listening");

      const recognition = new Recognition();
      recognition.lang = button.dataset.language === "zh" ? "zh-CN" : "en-US";
      recognition.interimResults = true;
      recognition.continuous = false;
      recognition.maxAlternatives = 1;

      let latestTranscript = "";

      recognition.onstart = () => {
        setStatus(messageFor("listening", "Listening. Say the dream fragment when you are ready."), "listening");
      };

      recognition.onresult = (event) => {
        latestTranscript = Array.from(event.results)
          .map((result) => result[0]?.transcript || "")
          .join("")
          .trim();
        if (latestTranscript) {
          setStatus(`Listening: ${latestTranscript}`, "listening");
        }
      };

      recognition.onerror = (event) => {
        const message = event.error === "not-allowed"
          ? messageFor("permission", "Microphone permission was denied. Allow recording and try again.")
          : messageFor("empty", "I did not catch that. Tap the microphone again if you want to retry.");
        setStatus(message, "error");
      };

      recognition.onend = () => {
        if (latestTranscript) {
          appendTranscript(latestTranscript);
          setStatus(messageFor("done", "Added to the dream note."), "done");
        } else if (button.dataset.mode === "listening") {
          setStatus(messageFor("empty", "No speech detected. Tap again if you want to retry."), "idle");
        }
      };

      recognition.start();
    });
  };

  const bindAttachmentButton = () => {
    const button = document.querySelector(".dc-attach-button");
    const composer = button?.closest(".dc-composer");

    if (!button || !composer || button.dataset.bound === "true") {
      return;
    }
    button.dataset.bound = "true";

    const localizeImagePopover = () => {
      const control = composer.querySelector(".dc-attach-control");
      const popover = composer.querySelector(".dc-image-popover");
      if (!control || !popover) {
        return;
      }

      const copy = {
        imageLabel: control.dataset.imageLabel || "Image clue",
        upload: control.dataset.upload || "Upload image",
        paste: control.dataset.paste || "Paste from Clipboard",
      };
      composer.dataset.imageLanguage = control.dataset.language || "en";
      const sourceButtons = popover.querySelectorAll('[data-testid="source-select"] button');
      const clipboardSelected = sourceButtons.length > 1
        && sourceButtons[sourceButtons.length - 1].classList.contains("selected");
      const primaryCopy = clipboardSelected ? copy.paste : copy.upload;

      const label = popover.querySelector('[data-testid="block-label"]');
      if (label) {
        let labelText = label.querySelector(".dc-image-label-copy");
        if (!labelText) {
          labelText = document.createElement("span");
          labelText.className = "dc-image-label-copy";
          label.appendChild(labelText);
        }
        Array.from(label.childNodes).forEach((node) => {
          if (node.nodeType === Node.TEXT_NODE) {
            node.textContent = "";
          }
        });
        labelText.textContent = copy.imageLabel;
      }

      const uploadWrap = popover.querySelector(".upload-container button .wrap");
      if (uploadWrap) {
        Array.from(uploadWrap.childNodes).forEach((node) => {
          if (node.nodeType === Node.TEXT_NODE) {
            node.textContent = "";
          }
        });
        let uploadText = uploadWrap.querySelector(".dc-image-upload-copy");
        if (!uploadText) {
          uploadText = document.createElement("strong");
          uploadText.className = "dc-image-upload-copy";
          uploadWrap.appendChild(uploadText);
        }
        uploadText.textContent = primaryCopy;
      }

      const uploadButton = popover.querySelector(".upload-container button");
      uploadButton?.setAttribute("aria-label", primaryCopy);

      if (sourceButtons[0]) {
        sourceButtons[0].setAttribute("aria-label", copy.upload);
      }
      if (sourceButtons[sourceButtons.length - 1]) {
        sourceButtons[sourceButtons.length - 1].setAttribute("aria-label", copy.paste);
      }

      const replaceText = (root) => {
        Array.from(root.childNodes).forEach((node) => {
          if (node.nodeType === Node.TEXT_NODE) {
            const text = node.textContent || "";
            if (text.includes("Paste from Clipboard") || text.includes("从剪贴板粘贴")) {
              node.textContent = text.replace("Paste from Clipboard", copy.paste).replace("从剪贴板粘贴", copy.paste);
            }
          } else if (node.nodeType === Node.ELEMENT_NODE) {
            replaceText(node);
          }
        });
      };
      replaceText(popover);
    };

    const setOpen = (open) => {
      localizeImagePopover();
      composer.classList.toggle("dc-image-open", open);
      button.setAttribute("aria-expanded", open ? "true" : "false");
    };

    button.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      const shouldOpen = !composer.classList.contains("dc-image-open");
      setOpen(shouldOpen);
      if (shouldOpen) {
        const uploadInput = composer.querySelector(".dc-image-popover input[type='file']");
        uploadInput?.focus();
      }
    });

    composer.addEventListener("click", localizeImagePopover);
    localizeImagePopover();

    document.addEventListener("click", (event) => {
      if (!composer.contains(event.target)) {
        setOpen(false);
      }
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        setOpen(false);
      }
    });
  };

  const bindComposerControls = () => {
    bindVoiceButton();
    bindAttachmentButton();
  };

  bindComposerControls();
  const observer = new MutationObserver(bindComposerControls);
  observer.observe(document.body, { childList: true, subtree: true });
}
"""


def _load_view(view_json: str) -> dict:
    try:
        return json.loads(view_json or "{}")
    except json.JSONDecodeError:
        return {"status": "error", "error": copy_for(DEFAULT_LANGUAGE)["error_state"]}


def _notice_html(view: dict) -> str:
    message = escape(view.get("notice") or view.get("error") or "")
    css = "dc-notice is-error" if view.get("status") == "error" else "dc-notice"
    return f"<div class='{css}'>{message}</div>" if message else ""


def _question_markdown(view: dict, language: str = DEFAULT_LANGUAGE) -> str:
    copy = copy_for(language)
    question = escape(view.get("question") or "")
    optional_question = (
        f"<p class='dc-question-original'><span>{copy['question_speaker']}</span>{question}</p>"
        if question
        else ""
    )
    return f"""
<div class="dc-question-card">
  <span class="dc-question-kicker">{copy['question_kicker']}</span>
  <h2>{copy['question_title']}</h2>
  <p>{copy['question_body']}</p>
  {optional_question}
  <p class="dc-question-note">{copy['question_note']}</p>
</div>
""".strip()


def _updates(state: str, view_json: str):
    view = _load_view(view_json)
    status = view.get("status", "declaration")
    language = normalize_language(view.get("language", DEFAULT_LANGUAGE))
    return (
        state,
        view_json,
        _hero_html(language, status),
        _notice_html(view),
        _question_markdown(view, language),
        view.get("card_html", ""),
        view.get("card_text", ""),
        gr.update(visible=status in {"record", "error"}),
        gr.update(visible=status == "ask"),
        gr.update(visible=status == "tip"),
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


def _submit(dream_text, image_value, audio_value, mood, language, text_backend, vision_backend, *settings_values):
    language = normalize_language(language)
    settings = _settings_from_inputs(*settings_values)
    state, view_json = submit_dream_action(
        dream_text=dream_text,
        image_value=image_value,
        audio_value=audio_value,
        mood=mood,
        text_backend=text_backend,
        vision_backend=vision_backend,
        language=language,
        **settings,
    )
    return _updates(state, view_json)


def _answer(state, answer, language, text_backend, vision_backend, *settings_values):
    language = normalize_language(language)
    settings = _settings_from_inputs(*settings_values)
    state, view_json = answer_to_card_action(
        state,
        answer=answer,
        text_backend=text_backend,
        vision_backend=vision_backend,
        language=language,
        **settings,
    )
    return _updates(state, view_json)


def _skip(state, language, text_backend, vision_backend, *settings_values):
    language = normalize_language(language)
    settings = _settings_from_inputs(*settings_values)
    state, view_json = skip_to_card_action(
        state,
        text_backend=text_backend,
        vision_backend=vision_backend,
        language=language,
        **settings,
    )
    return _updates(state, view_json)


def _revise(state, revision_request, language, text_backend, vision_backend, *settings_values):
    language = normalize_language(language)
    settings = _settings_from_inputs(*settings_values)
    state, view_json = revise_card_action(
        state,
        revision_request=revision_request,
        text_backend=text_backend,
        vision_backend=vision_backend,
        language=language,
        **settings,
    )
    return _updates(state, view_json)


def _reset(language, text_backend, vision_backend, *settings_values):
    if language not in {"en", "zh"}:
        settings_values = (vision_backend, *settings_values)
        vision_backend = text_backend
        text_backend = language
        language = DEFAULT_LANGUAGE
    language = normalize_language(language)
    settings = _settings_from_inputs(*settings_values)
    state, view_json = reset_mobile_action(
        text_backend=text_backend,
        vision_backend=vision_backend,
        language=language,
        **settings,
    )
    return (*_updates(state, view_json), "", "", None, None, default_mood_for(language))


def _active_step_for_status(status: str) -> int:
    return {"record": 1, "error": 1, "ask": 2, "drafting": 3, "tip": 4}.get(status, 1)


def _hero_html(language: str = DEFAULT_LANGUAGE, status: str = "record") -> str:
    copy = copy_for(language)
    steps = copy["steps"]
    active_step = _active_step_for_status(status)
    step_html = []
    for index, label in enumerate(steps, start=1):
        classes = ["dc-step"]
        if index < active_step:
            classes.append("is-complete")
        if index == active_step:
            classes.append("is-active")
        aria_current = ' aria-current="step"' if index == active_step else ""
        step_html.append(
            f'<span class="{" ".join(classes)}"{aria_current}><strong>{index}</strong>{label}</span>'
        )
        if index < len(steps):
            line_classes = ["dc-stepper-line"]
            if index < active_step:
                line_classes.append("is-complete")
            step_html.append(f'<i class="{" ".join(line_classes)}" aria-hidden="true"></i>')
    return f"""
<header class="dc-hero">
  <div class="dc-hero-top">
    <div class="dc-menu-mark" aria-hidden="true"><span></span><span></span><span></span></div>
    <div class="dc-brand-lockup">
      <div>
        <h1>{copy['title']}</h1>
        <p class="dc-brand-subtitle">{copy['subtitle']}</p>
      </div>
    </div>
    <div class="dc-sun-mark" aria-hidden="true">☀</div>
  </div>
  <div class="dc-stepper" aria-label="Dream QA steps">
    {''.join(step_html)}
  </div>
</header>
""".strip()


def _section_title_html(number: int, text: str) -> str:
    return f"""
<div class="dc-section-title">
  <span class="dc-title-icon">{number}</span>
  <strong>{escape(text)}</strong>
</div>
""".strip()


def _mic_html(language: str = DEFAULT_LANGUAGE) -> str:
    copy = copy_for(language)
    return f"""
<div class="dc-mic-control">
  <button
    type="button"
    class="dc-mic-button"
    aria-label="{escape(copy['mic_idle'])}"
    data-language="{escape(language)}"
    data-checking="{escape('正在请求麦克风权限...' if language == 'zh' else 'Checking microphone permission...')}"
    data-unsupported="{escape(copy['mic_unsupported'])}"
    data-permission="{escape(copy['mic_permission'])}"
    data-listening="{escape(copy['mic_listening'])}"
    data-done="{escape(copy['mic_done'])}"
    data-empty="{escape(copy['mic_empty'])}"
  >
    <span class="dc-mic-glyph" aria-hidden="true"></span>
  </button>
  <div class="dc-mic-status" aria-live="polite">{escape(copy['mic_idle'])}</div>
</div>
""".strip()


def _attachment_html(language: str = DEFAULT_LANGUAGE) -> str:
    copy = copy_for(language)
    label = escape(copy["image_accordion"])
    return f"""
<div
  class="dc-attach-control"
  data-language="{escape(language)}"
  data-image-label="{escape(copy['image_label'])}"
  data-upload="{escape(copy['image_upload'])}"
  data-paste="{escape(copy['image_paste'])}"
>
  <button type="button" class="dc-attach-button" aria-label="{label}" aria-expanded="false">
    <span aria-hidden="true">+</span>
  </button>
</div>
""".strip()


def _field_tip_html(language: str = DEFAULT_LANGUAGE) -> str:
    return f"<p class=\"dc-field-tip\">{escape(copy_for(language)['field_tip'])}</p>"


def _processing_html(language: str = DEFAULT_LANGUAGE) -> str:
    return f"<p class='dc-processing-note'>{escape(copy_for(language)['processing_note'])}</p>"


def _side_stamp_html(language: str = DEFAULT_LANGUAGE) -> str:
    copy = copy_for(language)
    return f"""
<div class="dc-side-stamp">
  <span>{escape(copy['side_stamp_label'])}</span>
  <strong>{escape(copy['side_stamp_title'])}</strong>
  <small>{escape(copy['side_stamp_body'])}</small>
</div>
""".strip()


def _dev_help_html(language: str = DEFAULT_LANGUAGE) -> str:
    return f"""
<div class="dc-dev-help">
  <strong>For debugging only. Most people can leave this alone.</strong>
  <span>{escape(copy_for(language)['runtime_help'])}</span>
</div>
""".strip()


def _debug_help_html(language: str = DEFAULT_LANGUAGE) -> str:
    return f"""
<div class="dc-debug-help">
  <strong>{escape(copy_for(language)['debug_title'])}</strong>
  <span>{escape(copy_for(language)['debug_help'])}</span>
</div>
""".strip()


def build_demo() -> gr.Blocks:
    initial_state, initial_view = initial_mobile_state(language=DEFAULT_LANGUAGE)
    initial = _load_view(initial_view)
    initial_copy = copy_for(DEFAULT_LANGUAGE)

    with gr.Blocks(css=CSS, js=VOICE_JS, title=APP_TITLE) as demo:
        session_state = gr.State(initial_state)
        view_state = gr.State(initial_view)

        with gr.Column(elem_classes=["dc-shell"]):
            hero_html = gr.HTML(_hero_html(DEFAULT_LANGUAGE))
            notice = gr.HTML(_notice_html(initial))

            with gr.Row(elem_classes=["dc-workspace-grid"]):
                with gr.Column(elem_classes=["dc-flow-column"]):
                    with gr.Group(visible=True, elem_classes=["dc-stage"]) as declaration_group:
                        with gr.Group(elem_classes=["dc-composer"]):
                            dream_section_html = gr.HTML(_section_title_html(1, initial_copy["dream_label"]))
                            dream_text = gr.Textbox(
                                label=initial_copy["dream_label"],
                                placeholder=DREAM_PLACEHOLDER,
                                lines=12,
                                value="",
                                elem_classes=["dc-dream-text"],
                            )
                            mic_html = gr.HTML(_mic_html(DEFAULT_LANGUAGE))
                            attachment_html = gr.HTML(_attachment_html(DEFAULT_LANGUAGE))
                            image_input = gr.Image(
                                label=initial_copy["image_label"],
                                sources=["upload", "clipboard"],
                                type="filepath",
                                height=180,
                                elem_classes=["dc-image-popover"],
                            )
                            audio_input = gr.Audio(
                                label=initial_copy["voice_label"],
                                sources=["upload"],
                                type="filepath",
                                format="wav",
                                elem_classes=["dc-voice-input"],
                                visible=False,
                            )
                        field_tip_html = gr.HTML(_field_tip_html(DEFAULT_LANGUAGE))
                        with gr.Row(elem_classes=["dc-submit-row"]):
                            example_button = gr.Button(initial_copy["example_button"], variant="secondary")
                            submit_button = gr.Button(initial_copy["submit_button"], variant="primary")
                        processing_html = gr.HTML(_processing_html(DEFAULT_LANGUAGE))

                    with gr.Group(visible=False, elem_classes=["dc-stage", "dc-question"]) as question_group:
                        question_markdown = gr.HTML(_question_markdown(initial, DEFAULT_LANGUAGE))
                        answer_text = gr.Textbox(
                            label=initial_copy["answer_label"],
                            placeholder=ANSWER_PLACEHOLDER,
                            lines=4,
                            value="",
                        )
                        with gr.Row(elem_classes=["dc-question-actions"]):
                            answer_button = gr.Button(initial_copy["answer_button"], variant="primary")
                            skip_button = gr.Button(initial_copy["skip_button"], variant="secondary")

                    with gr.Group(visible=False, elem_classes=["dc-stage", "dc-card"]) as card_group:
                        card_html = gr.HTML("")
                        with gr.Row(elem_classes=["dc-actions"]):
                            gentle_button = gr.Button(initial_copy["ask_again_button"], variant="secondary")
                            weird_button = gr.Button(initial_copy["angle_button"], variant="secondary")
                            copy_button = gr.Button(initial_copy["copy_button"], variant="secondary")
                            reset_button = gr.Button(initial_copy["reset_button"], variant="secondary")
                        card_text = gr.Textbox(
                            label=initial_copy["copy_label"],
                            value="",
                            lines=8,
                            show_copy_button=True,
                            elem_classes=["dc-hidden-text"],
                        )

                with gr.Column(elem_classes=["dc-side-panel"]):
                    language = gr.Radio(
                        label=initial_copy["language_label"],
                        choices=LANGUAGE_OPTIONS,
                        value=DEFAULT_LANGUAGE,
                    )
                    mood_section_html = gr.HTML(_section_title_html(2, initial_copy["side_title"]))
                    mood = gr.Dropdown(label=initial_copy["mood_label"], choices=MOOD_OPTIONS, value=DEFAULT_MOOD)
                    side_stamp_html = gr.HTML(_side_stamp_html(DEFAULT_LANGUAGE))
                    with gr.Accordion("Advanced", open=False, elem_classes=["dc-dev"]):
                        dev_help_html = gr.HTML(_dev_help_html(DEFAULT_LANGUAGE))
                        text_backend = gr.Dropdown(
                            label="Text generation",
                            choices=[
                                ("Modal: MiniCPM endpoint", "modal"),
                                ("Auto: configured Space model", "model"),
                                ("Demo: stable sample data", "demo"),
                                ("Local Ollama", "ollama"),
                            ],
                            value=DEFAULT_TEXT_BACKEND,
                        )
                        vision_backend = gr.Dropdown(
                            label="Image understanding",
                            choices=[
                                ("Modal: MiniCPM-V endpoint", "modal"),
                                ("Auto: configured vision model", "model"),
                                ("Demo: skip image model", "demo"),
                                ("Local Ollama", "ollama"),
                            ],
                            value=DEFAULT_VISION_BACKEND,
                        )
                        asr_backend = gr.Dropdown(
                            label="Voice input",
                            choices=[
                                ("Modal ASR endpoint", "modal"),
                                ("Demo: mark voice received", "demo"),
                                ("Hugging Face ASR endpoint, planned", "huggingface"),
                            ],
                            value=DEFAULT_ASR_BACKEND,
                        )
                        with gr.Accordion("Advanced endpoints", open=False, elem_classes=["dc-dev-advanced"]):
                            text_endpoint = gr.Textbox(label="Text endpoint", value="")
                            vision_endpoint = gr.Textbox(label="Image endpoint", value="")
                            asr_endpoint = gr.Textbox(label="ASR Endpoint", value="")
                            hosted_token = gr.Textbox(label="Hosted Token", value="", type="password")
                            text_model = gr.Textbox(label="Text model", value=DEFAULT_TEXT_MODEL)
                            vision_model = gr.Textbox(label="Image model", value=DEFAULT_VISION_MODEL)
                            ollama_url = gr.Textbox(label="Ollama URL", value="http://localhost:11434")
                            text_timeout_seconds = gr.Number(
                                label="Text timeout, seconds",
                                value=DEFAULT_HOSTED_TIMEOUT_SECONDS,
                                precision=1,
                            )
                            vision_timeout_seconds = gr.Number(
                                label="Image timeout, seconds",
                                value=DEFAULT_HOSTED_TIMEOUT_SECONDS,
                                precision=1,
                            )
                            asr_timeout_seconds = gr.Number(
                                label="ASR timeout, seconds",
                                value=DEFAULT_ASR_TIMEOUT_SECONDS,
                                precision=1,
                            )
                            text_latency_budget_ms = gr.Number(
                                label="Modal text latency budget, ms",
                                value=DEFAULT_TEXT_LATENCY_BUDGET_MS,
                                precision=0,
                            )
                            vision_latency_budget_ms = gr.Number(
                                label="Modal image latency budget, ms",
                                value=DEFAULT_VISION_LATENCY_BUDGET_MS,
                                precision=0,
                            )
                            asr_latency_budget_ms = gr.Number(
                                label="ASR latency budget, ms",
                                value=DEFAULT_ASR_LATENCY_BUDGET_MS,
                                precision=0,
                            )
                            text_temperature = gr.Slider(
                                label="Text temperature",
                                minimum=0,
                                maximum=0.7,
                                step=0.05,
                                value=DEFAULT_TEXT_TEMPERATURE,
                            )
                            vision_temperature = gr.Slider(
                                label="Image temperature",
                                minimum=0,
                                maximum=0.7,
                                step=0.05,
                                value=DEFAULT_VISION_TEMPERATURE,
                            )
                            text_max_tokens = gr.Slider(
                                label="Text max tokens",
                                minimum=64,
                                maximum=1200,
                                step=1,
                                value=DEFAULT_TEXT_MAX_TOKENS,
                            )
                            vision_max_tokens = gr.Slider(
                                label="Image max tokens",
                                minimum=64,
                                maximum=800,
                                step=1,
                                value=DEFAULT_VISION_MAX_TOKENS,
                            )
            with gr.Accordion(initial_copy["debug_title"], open=False, elem_classes=["dc-debug-panel"]) as debug_panel:
                debug_help_html = gr.HTML(_debug_help_html(DEFAULT_LANGUAGE))
                debug_json = gr.Code(
                    label=initial_copy["debug_state_label"],
                    value=json.dumps(initial.get("debug", {}), ensure_ascii=False, indent=2),
                    language="json",
                )

        outputs = [
            session_state,
            view_state,
            hero_html,
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
            inputs=[dream_text, image_input, audio_input, mood, language, text_backend, vision_backend] + settings_inputs,
            outputs=outputs,
        )
        answer_button.click(
            _answer,
            inputs=[session_state, answer_text, language, text_backend, vision_backend] + settings_inputs,
            outputs=outputs,
        )
        skip_button.click(
            _skip,
            inputs=[session_state, language, text_backend, vision_backend] + settings_inputs,
            outputs=outputs,
        )
        gentle_button.click(
            _revise,
            inputs=[session_state, gr.State("softer"), language, text_backend, vision_backend] + settings_inputs,
            outputs=outputs,
        )
        weird_button.click(
            _revise,
            inputs=[session_state, gr.State("stranger"), language, text_backend, vision_backend] + settings_inputs,
            outputs=outputs,
        )
        copy_button.click(lambda text: text, inputs=card_text, outputs=card_text)
        reset_button.click(
            _reset,
            inputs=[language, text_backend, vision_backend] + settings_inputs,
            outputs=outputs + [dream_text, answer_text, image_input, audio_input, mood],
        )

        def _example(selected_language):
            selected_language = normalize_language(selected_language)
            return EXAMPLE_DREAMS[selected_language], EXAMPLE_MOODS[selected_language]

        example_button.click(_example, inputs=language, outputs=[dream_text, mood])

        def _language_ui(selected_language):
            selected_language = normalize_language(selected_language)
            copy = copy_for(selected_language)
            moods = mood_options_for(selected_language)
            return (
                _hero_html(selected_language),
                _notice_html({"notice": copy["notice_record"], "status": "record"}),
                _section_title_html(1, copy["dream_label"]),
                gr.update(label=copy["dream_label"], placeholder=copy["dream_placeholder"]),
                _mic_html(selected_language),
                _attachment_html(selected_language),
                gr.update(label=copy["image_label"]),
                _field_tip_html(selected_language),
                gr.update(value=copy["example_button"]),
                gr.update(value=copy["submit_button"]),
                _processing_html(selected_language),
                _question_markdown({"question": ""}, selected_language),
                gr.update(label=copy["answer_label"], placeholder=copy["answer_placeholder"]),
                gr.update(value=copy["answer_button"]),
                gr.update(value=copy["skip_button"]),
                gr.update(value=copy["ask_again_button"]),
                gr.update(value=copy["angle_button"]),
                gr.update(value=copy["copy_button"]),
                gr.update(value=copy["reset_button"]),
                gr.update(label=copy["copy_label"]),
                gr.update(label=copy["language_label"]),
                _section_title_html(2, copy["side_title"]),
                gr.update(label=copy["mood_label"], choices=moods, value=moods[0]),
                _side_stamp_html(selected_language),
                _dev_help_html(selected_language),
                gr.update(label=copy["debug_title"]),
                _debug_help_html(selected_language),
                gr.update(label=copy["debug_state_label"]),
            )

        language.change(
            _language_ui,
            inputs=language,
            outputs=[
                hero_html,
                notice,
                dream_section_html,
                dream_text,
                mic_html,
                attachment_html,
                image_input,
                field_tip_html,
                example_button,
                submit_button,
                processing_html,
                question_markdown,
                answer_text,
                answer_button,
                skip_button,
                gentle_button,
                weird_button,
                copy_button,
                reset_button,
                card_text,
                language,
                mood_section_html,
                mood,
                side_stamp_html,
                dev_help_html,
                debug_panel,
                debug_help_html,
                debug_json,
            ],
        )

    return demo
