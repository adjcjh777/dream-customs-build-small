import json
from copy import deepcopy
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
    EXAMPLE_CHIPS,
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


def _make_media_api_info_client_safe(component):
    """Patch Gradio FileData schemas so gradio_client can parse the config."""

    original_api_info = component.api_info

    def api_info():
        schema = deepcopy(original_api_info())
        meta = schema.get("properties", {}).get("meta", {})
        if isinstance(meta.get("additionalProperties"), bool):
            meta["additionalProperties"] = {"type": "string"}
        return schema

    component.api_info = api_info


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
    let checkingTimer = null;

    const setStatus = (message, mode) => {
      if (mode !== "listening" && checkingTimer) {
        window.clearTimeout(checkingTimer);
        checkingTimer = null;
      }
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
      let latestTranscript = "";

      const recognition = new Recognition();
      recognition.lang = button.dataset.language === "zh" ? "zh-CN" : "en-US";
      recognition.interimResults = true;
      recognition.continuous = false;
      recognition.maxAlternatives = 1;
      checkingTimer = window.setTimeout(() => {
        if (button.dataset.mode === "listening" && !latestTranscript) {
          setStatus(messageFor("timeout", "Voice is taking too long here. You can keep typing the dream instead."), "error");
          try {
            recognition.stop();
          } catch (_error) {
            // Best-effort stop for browsers that leave speech recognition pending.
          }
          textarea.focus();
        }
      }, 3000);

      recognition.onstart = () => {
        if (checkingTimer) {
          window.clearTimeout(checkingTimer);
          checkingTimer = null;
        }
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
        if (checkingTimer) {
          window.clearTimeout(checkingTimer);
          checkingTimer = null;
        }
        const message = event.error === "not-allowed"
          ? messageFor("permission", "Microphone permission was denied. Allow recording and try again.")
          : messageFor("empty", "I did not catch that. Tap the microphone again if you want to retry.");
        setStatus(message, "error");
      };

      recognition.onend = () => {
        if (checkingTimer) {
          window.clearTimeout(checkingTimer);
          checkingTimer = null;
        }
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
    bindProcessingButtons();
  };

  const currentLanguage = () => {
    const micButton = document.querySelector(".dc-mic-button");
    if (micButton?.dataset.language) {
      return micButton.dataset.language;
    }
    return document.body.innerText.includes("梦境问答台") ? "zh" : "en";
  };

  const setProcessingCopy = (mode) => {
    const isZh = currentLanguage() === "zh";
    const copy = mode === "submit"
      ? {
          notice: isZh
            ? "正在整理梦境线索。下一步会生成一个贴着细节的温和追问。"
            : "Reading the dream details. Next, Dream QA will ask one grounded question.",
          note: isZh
            ? "正在提取人物、地点、情绪和具体物件；如果生成较慢，通常需要十几秒。"
            : "Extracting people, places, feelings, and concrete objects. A slower run can take several seconds.",
        }
      : mode === "question"
      ? {
          notice: isZh
            ? "正在换一个追问角度。"
            : "Asking from another angle.",
          note: isZh
            ? "正在保留你的回答和梦境锚点，只重新生成一个更贴近当下的追问。"
            : "Keeping your answer and dream anchors while writing one more grounded question.",
        }
      : {
          notice: isZh
            ? "正在把追问回答整理进今日小 Tips。"
            : "Folding the follow-up answer into the Today Tip.",
          note: isZh
            ? "正在检查梦境锚点、你的回答和安全边界，然后生成一个可复制结果。"
            : "Checking dream anchors, your answer, and safety boundaries before writing the copyable result.",
        };

    document.querySelectorAll(".dc-notice").forEach((el) => {
      el.textContent = copy.notice;
      el.classList.remove("is-error");
      el.classList.add("is-processing");
    });
    document.querySelectorAll(".dc-processing-note").forEach((el) => {
      el.textContent = copy.note;
      el.classList.add("is-active");
    });
  };

  const bindProcessingButtons = () => {
    const bindButton = (selector, mode) => {
      document.querySelectorAll(selector).forEach((root) => {
        const button = root.matches("button") ? root : root.querySelector("button");
        if (!button || button.dataset.processingBound === "true") {
          return;
        }
        button.dataset.processingBound = "true";
        button.addEventListener("click", () => setProcessingCopy(mode));
      });
    };

    bindButton(".dc-submit-button", "submit");
    bindButton(".dc-answer-button", "tip");
    bindButton(".dc-tip-button", "tip");
    bindButton(".dc-question-button", "question");
  };

  bindComposerControls();
  const observer = new MutationObserver(bindComposerControls);
  observer.observe(document.body, { childList: true, subtree: true });
}
"""


COPY_RESULT_JS = """
(text) => {
  const value = text || "";
  const showNotice = (message, isError = false) => {
    document.querySelectorAll(".dc-notice").forEach((el) => {
      el.textContent = message;
      el.classList.toggle("is-error", isError);
      el.classList.remove("is-processing");
    });
  };
  if (!value.trim()) {
    showNotice("Nothing to copy yet. Generate a Today Tip first. / 还没有可复制结果，请先生成今日小 Tips。", true);
    return value;
  }
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(value)
      .then(() => showNotice("Result copied. / 已复制结果。"))
      .catch(() => showNotice("Copy was blocked by the browser. Use the Copy button inside the text box. / 浏览器阻止复制时，请使用文本框内置 Copy。", true));
  } else {
    showNotice("This browser blocked direct copy. Use the Copy button inside the text box. / 浏览器阻止复制时，请使用文本框内置 Copy。", true);
  }
  return value;
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
    anchor_items = [str(anchor).strip() for anchor in view.get("dream_anchors", [])[:3] if str(anchor).strip()]
    anchor_label = "梦境锚点" if language == "zh" else "Dream anchors"
    anchor_chips = "".join(f"<span>{escape(anchor)}</span>" for anchor in anchor_items)
    anchor_strip = (
        "<div class='dc-question-anchor-wrap'>"
        f"<span class='dc-question-anchor-label'>{escape(copy['question_anchor_label'])}</span>"
        f"<div class='dc-question-anchor-strip' aria-label='{anchor_label}'>{anchor_chips}</div>"
        "</div>"
        if anchor_chips
        else ""
    )
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
  {anchor_strip}
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
        _field_tip_html(language, view),
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


def _agent_dream_qa(dream_text: str, mood: str = "", answer: str = "", language: str = DEFAULT_LANGUAGE) -> dict:
    """Text-only public API for external agents.

    The visual UI keeps image and voice inputs, but those components currently
    generate Gradio schemas that some agent clients cannot parse. This endpoint
    keeps the agent path simple and stable while still exercising the same
    Dream QA pipeline and configured Modal text backend.
    """

    language = normalize_language(language)
    contract = {
        "schema_version": "dream_qa.agent.v1",
        "route_mode": "text_only_queue",
        "api_name": "/agent_dream_qa",
        "expected_fields": ["dream_text", "mood", "answer", "language"],
        "media_note": "Image and voice clues are available in the Gradio UI path; this public agent endpoint is intentionally text-only.",
    }
    if not isinstance(dream_text, str) or not dream_text.strip():
        return {
            "status": "error",
            "phase": "error",
            "language": language,
            "error_code": "missing_dream_text",
            "error": "dream_text is required.",
            "notice": "Provide dream_text as a non-empty string, then call the queue endpoint again.",
            "dream_summary": "",
            "main_question": "",
            "dream_anchors": [],
            "followup_questions": [],
            "user_answers": [],
            "interpretation": "",
            "today_tip": "",
            "tiny_action": "",
            "caring_note": "",
            "safety_note": "",
            "api_contract": contract,
        }
    state, view_json = submit_dream_action(
        dream_text=dream_text,
        image_value=None,
        audio_value=None,
        mood=mood,
        text_backend=DEFAULT_TEXT_BACKEND,
        vision_backend=DEFAULT_VISION_BACKEND,
        language=language,
    )
    view = json.loads(view_json)
    if view.get("status") != "ask":
        view["api_contract"] = contract
        return view
    if answer and answer.strip():
        _state, view_json = answer_to_card_action(
            state,
            answer=answer,
            text_backend=DEFAULT_TEXT_BACKEND,
            vision_backend=DEFAULT_VISION_BACKEND,
            language=language,
        )
    else:
        _state, view_json = skip_to_card_action(
            state,
            text_backend=DEFAULT_TEXT_BACKEND,
            vision_backend=DEFAULT_VISION_BACKEND,
            language=language,
        )
    result = json.loads(view_json)
    result["api_contract"] = contract
    return result


def _active_step_for_status(status: str) -> int:
    return {"record": 1, "error": 1, "ask": 2, "drafting": 2, "tip": 3}.get(status, 1)


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
        <p class="dc-hero-kicker">{copy['hero_kicker']}</p>
        <h1>{copy['hero_title']}</h1>
        <p class="dc-brand-subtitle">{copy['subtitle']}</p>
      </div>
    </div>
    <div class="dc-sun-mark" aria-hidden="true"></div>
  </div>
  <p class="dc-hero-body">{copy['hero_body']}</p>
  <div class="dc-hero-ribbon" aria-label="{escape(copy['hero_badge'])}">
    <span>{escape(copy['hero_badge'])}</span>
    <small>{escape(copy['hero_mobile_note'])}</small>
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


def _demo_chip_intro_html(language: str = DEFAULT_LANGUAGE) -> str:
    copy = copy_for(language)
    return f"""
<div class="dc-demo-chip-intro">
  <span>{escape(copy['demo_intro_label'])}</span>
  <strong>{escape(copy['demo_intro_body'])}</strong>
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
    data-timeout="{escape('语音识别等待太久了。你可以先继续手动输入梦境。' if language == 'zh' else 'Voice is taking too long here. You can keep typing the dream instead.')}"
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


def _field_tip_html(language: str = DEFAULT_LANGUAGE, view=None) -> str:
    copy = copy_for(language)
    view = view or {}
    if view.get("status") == "error":
        message = (
            "Dream note needs at least one sentence, image, or voice clue before Continue."
            if normalize_language(language) == "en"
            else "梦境记录需要至少一句文字、图片或语音线索，然后再继续。"
        )
        return f'<p class="dc-field-tip is-error" role="alert">{escape(message)}</p>'
    return f"""
<div class="dc-field-tip">
  <span>{escape(copy['desk_rule_label'])}</span>
  <strong>{escape(copy['desk_rule_title'])}</strong>
  <p>{escape(copy['field_tip'])}</p>
</div>
""".strip()


def _processing_html(language: str = DEFAULT_LANGUAGE) -> str:
    return f"<p class='dc-processing-note'>{escape(copy_for(language)['processing_note'])}</p>"


def _side_stamp_html(language: str = DEFAULT_LANGUAGE) -> str:
    copy = copy_for(language)
    intake_items = "".join(f"<span>{escape(item)}</span>" for item in copy["intake_items"])
    return f"""
<div class="dc-side-stack">
  <div class="dc-side-stamp">
    <span>{escape(copy['side_stamp_label'])}</span>
    <strong>{escape(copy['side_stamp_title'])}</strong>
    <small>{escape(copy['side_stamp_body'])}</small>
  </div>
  <div class="dc-desk-rule">
    <span>{escape(copy['desk_rule_label'])}</span>
    <strong>{escape(copy['desk_rule_title'])}</strong>
    <p>{escape(copy['desk_rule_body'])}</p>
  </div>
  <div class="dc-intake-rail" aria-label="{escape(copy['intake_label'])}">
    <small>{escape(copy['intake_label'])}</small>
    <div>{intake_items}</div>
  </div>
</div>
""".strip()


def _example_chip(selected_language: str, chip_key: str):
    selected_language = normalize_language(selected_language)
    chip = EXAMPLE_CHIPS[selected_language].get(chip_key)
    if chip:
        return chip
    return EXAMPLE_DREAMS[selected_language], EXAMPLE_MOODS[selected_language]


def _example_elevator(selected_language: str):
    return _example_chip(selected_language, "elevator")


def _example_floor14(selected_language: str):
    return _example_chip(selected_language, "floor14")


def _example_melting(selected_language: str):
    return _example_chip(selected_language, "melting")


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
                            _make_media_api_info_client_safe(image_input)
                            audio_input = gr.Audio(
                                label=initial_copy["voice_label"],
                                sources=["upload"],
                                type="filepath",
                                format="wav",
                                elem_classes=["dc-voice-input"],
                                visible=False,
                            )
                            _make_media_api_info_client_safe(audio_input)
                        field_tip_html = gr.HTML(_field_tip_html(DEFAULT_LANGUAGE))
                        demo_chip_intro = gr.HTML(_demo_chip_intro_html(DEFAULT_LANGUAGE))
                        with gr.Row(elem_classes=["dc-submit-row"]):
                            submit_button = gr.Button(
                                initial_copy["submit_button"],
                                variant="primary",
                                elem_classes=["dc-submit-button"],
                            )
                            with gr.Row(elem_classes=["dc-demo-chip-row"]):
                                example_button = gr.Button(
                                    initial_copy["example_button"],
                                    variant="secondary",
                                    elem_classes=["dc-demo-chip"],
                                )
                                example_button_2 = gr.Button(
                                    initial_copy["example_button_2"],
                                    variant="secondary",
                                    elem_classes=["dc-demo-chip"],
                                )
                                example_button_3 = gr.Button(
                                    initial_copy["example_button_3"],
                                    variant="secondary",
                                    elem_classes=["dc-demo-chip"],
                                )
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
                            answer_button = gr.Button(
                                initial_copy["answer_button"],
                                variant="primary",
                                elem_classes=["dc-answer-button"],
                            )
                            skip_button = gr.Button(
                                initial_copy["skip_button"],
                                variant="secondary",
                                elem_classes=["dc-tip-button"],
                            )

                    with gr.Group(visible=False, elem_classes=["dc-stage", "dc-card"]) as card_group:
                        card_html = gr.HTML("")
                        with gr.Row(elem_classes=["dc-actions"]):
                            gentle_button = gr.Button(
                                initial_copy["ask_again_button"],
                                variant="secondary",
                                elem_classes=["dc-question-button"],
                            )
                            weird_button = gr.Button(
                                initial_copy["angle_button"],
                                variant="secondary",
                                elem_classes=["dc-question-button"],
                            )
                            copy_button = gr.Button(initial_copy["copy_button"], variant="secondary")
                            reset_button = gr.Button(initial_copy["reset_button"], variant="secondary")
                        card_text = gr.Textbox(
                            label=initial_copy["copy_label"],
                            value="",
                            lines=8,
                            show_copy_button=True,
                            elem_classes=["dc-hidden-text"],
                        )
                    with gr.Accordion(initial_copy["debug_title"], open=False, elem_classes=["dc-debug-panel"]) as debug_panel:
                        debug_help_html = gr.HTML(_debug_help_html(DEFAULT_LANGUAGE))
                        debug_json = gr.Code(
                            label=initial_copy["debug_state_label"],
                            value=json.dumps(initial.get("debug", {}), ensure_ascii=False, indent=2),
                            language="json",
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
                        with gr.Group(elem_classes=["dc-dev-tuning"]):
                            text_temperature = gr.Number(
                                label="Text temperature",
                                value=DEFAULT_TEXT_TEMPERATURE,
                                precision=2,
                            )
                            vision_temperature = gr.Number(
                                label="Image temperature",
                                value=DEFAULT_VISION_TEMPERATURE,
                                precision=2,
                            )
                            text_max_tokens = gr.Number(
                                label="Text max tokens",
                                value=DEFAULT_TEXT_MAX_TOKENS,
                                precision=0,
                            )
                            vision_max_tokens = gr.Number(
                                label="Image max tokens",
                                value=DEFAULT_VISION_MAX_TOKENS,
                                precision=0,
                            )
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

            with gr.Group(visible=False):
                agent_dream_text = gr.Textbox(label="Agent dream text")
                agent_mood = gr.Textbox(label="Agent mood", value=DEFAULT_MOOD)
                agent_answer = gr.Textbox(label="Agent answer")
                agent_language = gr.Textbox(label="Agent language", value=DEFAULT_LANGUAGE)
                agent_result = gr.JSON(label="Agent Dream QA result")
                agent_button = gr.Button("Agent Dream QA")

        outputs = [
            session_state,
            view_state,
            hero_html,
            notice,
            field_tip_html,
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
            api_name=False,
            scroll_to_output=True,
            show_api=False,
        )
        answer_button.click(
            _answer,
            inputs=[session_state, answer_text, language, text_backend, vision_backend] + settings_inputs,
            outputs=outputs,
            api_name=False,
            scroll_to_output=True,
            show_api=False,
        )
        skip_button.click(
            _skip,
            inputs=[session_state, language, text_backend, vision_backend] + settings_inputs,
            outputs=outputs,
            api_name=False,
            scroll_to_output=True,
            show_api=False,
        )
        gentle_button.click(
            _revise,
            inputs=[session_state, gr.State("softer"), language, text_backend, vision_backend] + settings_inputs,
            outputs=outputs,
            api_name=False,
            scroll_to_output=True,
            show_api=False,
        )
        weird_button.click(
            _revise,
            inputs=[session_state, gr.State("stranger"), language, text_backend, vision_backend] + settings_inputs,
            outputs=outputs,
            api_name=False,
            scroll_to_output=True,
            show_api=False,
        )
        copy_button.click(
            lambda text: text,
            inputs=card_text,
            outputs=card_text,
            api_name=False,
            js=COPY_RESULT_JS,
            show_api=False,
        )
        reset_button.click(
            _reset,
            inputs=[language, text_backend, vision_backend] + settings_inputs,
            outputs=outputs + [dream_text, answer_text, image_input, audio_input, mood],
            api_name=False,
            show_api=False,
        )

        example_button.click(
            _example_elevator,
            inputs=[language],
            outputs=[dream_text, mood],
            api_name=False,
            show_api=False,
        )
        example_button_2.click(
            _example_floor14,
            inputs=[language],
            outputs=[dream_text, mood],
            api_name=False,
            show_api=False,
        )
        example_button_3.click(
            _example_melting,
            inputs=[language],
            outputs=[dream_text, mood],
            api_name=False,
            show_api=False,
        )

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
                _demo_chip_intro_html(selected_language),
                gr.update(value=copy["example_button"]),
                gr.update(value=copy["example_button_2"]),
                gr.update(value=copy["example_button_3"]),
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
                demo_chip_intro,
                example_button,
                example_button_2,
                example_button_3,
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
            api_name=False,
            show_api=False,
        )
        agent_button.click(
            _agent_dream_qa,
            inputs=[agent_dream_text, agent_mood, agent_answer, agent_language],
            outputs=agent_result,
            api_name="agent_dream_qa",
            show_api=True,
        )

    return demo
