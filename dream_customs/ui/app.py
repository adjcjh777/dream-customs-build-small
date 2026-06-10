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


def _extract_clues(view: dict) -> list:
    debug = view.get("debug", {})
    session = debug.get("session", {})
    clues = session.get("clues", [])
    if not clues and view.get("card_text"):
        for line in view["card_text"].splitlines():
            if line.startswith("Dream anchors:"):
                clues = [c.strip() for c in line.split(":", 1)[1].split(",")]
                break
    return clues


def _extract_tip_text(view: dict) -> str:
    if view.get("card_text"):
        for line in view["card_text"].splitlines():
            if line.startswith("Today Tip:"):
                return line.split(":", 1)[1].strip()
    return ""


# Real-time draft clue extraction keywords
_CLUE_KEYWORDS_ZH = {
    "桥": "过渡、连接",
    "水": "情绪、潜意识",
    "河": "情绪流动",
    "海": "深层潜意识",
    "雨": "情感释放",
    "雪": "冷静、纯净",
    "火": "激情、愤怒",
    "山": "挑战、目标",
    "路": "人生方向",
    "门": "机会、选择",
    "窗": "视角、希望",
    "梦": "内心探索",
    "飞": "自由、逃避",
    "掉": "失控、焦虑",
    "追": "追求、压力",
    "跑": "逃避、急迫",
    "哭": "情感释放",
    "笑": "喜悦、释然",
    "怕": "恐惧、不安",
    "急": "焦虑、紧迫",
    "暗": "未知、困惑",
    "亮": "希望、觉醒",
    "旧": "过去、回忆",
    "新": "转变、开始",
    "人": "人际关系",
    "家": "归属感",
    "学校": "成长、学习",
    "医院": "健康、疗愈",
    "车": "方向、控制",
    "电梯": "升降、压力",
    "天空": "自由、广阔",
    "树": "成长、生命力",
    "花": "美好、短暂",
    "猫": "独立、直觉",
    "狗": "忠诚、陪伴",
    "蛇": "转化、恐惧",
    "鱼": "潜意识、机遇",
}

_CLUE_KEYWORDS_EN = {
    "bridge": "transition, connection",
    "water": "emotion, subconscious",
    "river": "emotional flow",
    "ocean": "deep subconscious",
    "rain": "emotional release",
    "fire": "passion, anger",
    "mountain": "challenge, goal",
    "road": "life direction",
    "door": "opportunity, choice",
    "window": "perspective, hope",
    "fly": "freedom, escape",
    "fall": "loss of control, anxiety",
    "chase": "pursuit, pressure",
    "run": "escape, urgency",
    "cry": "emotional release",
    "laugh": "joy, relief",
    "dark": "unknown, confusion",
    "light": "hope, awakening",
    "old": "past, memory",
    "new": "transformation, beginning",
    "person": "interpersonal relationship",
    "home": "belonging",
    "school": "growth, learning",
    "hospital": "health, healing",
    "car": "direction, control",
    "elevator": "pressure, status change",
    "sky": "freedom, vastness",
    "tree": "growth, vitality",
    "flower": "beauty, impermanence",
    "cat": "independence, intuition",
    "dog": "loyalty, companionship",
    "snake": "transformation, fear",
    "fish": "subconscious, opportunity",
}


def _extract_interpretation_text(view: dict) -> str:
    if view.get("card_text"):
        for line in view["card_text"].splitlines():
            if line.startswith("Interpretation:"):
                return line.split(":", 1)[1].strip()
            if line.startswith("解读："):
                return line.split("：", 1)[1].strip()
    return ""


def _extract_dream_text(view: dict) -> str:
    debug = view.get("debug", {})
    session = debug.get("session", {})
    intake = session.get("intake", {})
    return intake.get("dream_text", "")


def _updates(state: str, view_json: str):
    view = _load_view(view_json)
    status = view.get("status", "declaration")
    language = normalize_language(view.get("language", DEFAULT_LANGUAGE))
    clues = _extract_clues(view)
    tip_text = _extract_tip_text(view)
    draft_text = _extract_interpretation_text(view)
    if not draft_text:
        draft_text = _draft_preview_text(_extract_dream_text(view), language)
    has_interp = bool(view.get("card_html"))
    status_label = _status_label(language, status)
    step_map = {"declaration": 1, "record": 1, "ask": 2, "interpret": 3, "tip": 4, "error": 1}
    active_step = step_map.get(status, 1)
    return (
        state,
        view_json,
        _notice_html(view),
        _question_markdown(view, language),
        view.get("card_html", ""),
        view.get("card_text", ""),
        gr.update(visible=status in {"record", "ask", "tip", "error"}),
        gr.update(visible=status == "ask"),
        gr.update(visible=status == "tip"),
        json.dumps(view.get("debug", {}), ensure_ascii=False, indent=2),
        _right_sidebar_html(language, clues, tip_text, has_interp, draft_text),
        _center_flow_html(language, status_label),
        _step_pill_bar_html(language, active_step),
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


def _topbar_html(language: str = DEFAULT_LANGUAGE, notification_count: int = 0) -> str:
    copy = copy_for(language)
    return f"""
<div class="dc-app-topbar dc-topbar">
  <div class="dc-topbar-left">
    <div class="dc-leaf-icon" aria-hidden="true">🌿</div>
    <div class="dc-topbar-brand">
      <span class="dc-topbar-title">{escape(copy['topbar_title'])}</span>
    </div>
  </div>
</div>
""".strip()


def _step_pill_bar_html(language: str = DEFAULT_LANGUAGE, active_step: int = 1) -> str:
    copy = copy_for(language)
    steps = copy["steps"]
    parts = []
    for i, step in enumerate(steps, 1):
        dot_class = "dc-step-dot active" if i == active_step else ("dc-step-dot done" if i < active_step else "dc-step-dot")
        label_class = "dc-step-label active" if i == active_step else "dc-step-label"
        parts.append(f'<span class="{dot_class}"></span> <span class="{label_class}">{escape(step)}</span>')
        if i < len(steps):
            parts.append('<span class="dc-step-sep">—</span>')
    return f'<div class="dc-step-bar">{"".join(parts)}</div>'


def _section_title_html(number: int, text: str) -> str:
    return f"""
<div class="dc-section-title">
  <span class="dc-title-icon">{number}</span>
  <strong>{escape(text)}</strong>
</div>
""".strip()


def _left_sidebar_html(language: str = DEFAULT_LANGUAGE, active_step: int = 1) -> str:
    copy = copy_for(language)
    steps = copy["steps"]
    subtitles = copy.get("step_subtitles", ["", "", "", ""])
    cards = ""
    for i, step in enumerate(steps, 1):
        active_class = " is-active" if i == active_step else ""
        subtitle = escape(subtitles[i - 1]) if i <= len(subtitles) else ""
        subtitle_html = f'<span class="dc-step-subtitle">{subtitle}</span>' if subtitle else ""
        cards += f'<div class="dc-step-card{active_class}"><span class="dc-step-num">{i}</span><div class="dc-step-content"><span class="dc-step-title">{escape(step)}</span>{subtitle_html}</div></div>\n'
    return f"""
<div class="dc-left-sidebar">
  {cards}
  <div class="dc-left-tip"><strong>{escape(copy['sidebar_tip_label'])}</strong><br>{escape(copy['sidebar_tip_text'])}</div>
</div>
""".strip()


def _center_flow_html(language: str = DEFAULT_LANGUAGE, status: str = "") -> str:
    copy = copy_for(language)
    resolved_status = status if status else copy["qa_flow_status"]
    return f"""
<div class="dc-center-preview">
  <div class="dc-center-header">
    <h2>{escape(copy['qa_flow_title'])}</h2>
    <span class="dc-status-pill">{escape(resolved_status)}</span>
  </div>
</div>
""".strip()


def _welcome_bubble_html(language: str = DEFAULT_LANGUAGE) -> str:
    copy = copy_for(language)
    title = copy.get('welcome_title', '昨晚梦到了什么？')
    message = copy.get('welcome_message', '想到什么就写什么——一种感觉、一个画面、一句话都行。')
    return f"""
<div class="dc-welcome-greeting">
  <h2>{escape(title)}</h2>
  <p>{escape(message)}</p>
</div>
""".strip()


def _right_sidebar_html(
    language: str = DEFAULT_LANGUAGE,
    clues=None,
    tip_text: str = "",
    has_interpretation: bool = False,
    draft_text: str = "",
) -> str:
    copy = copy_for(language)
    if clues:
        clues_html = "".join(f'<span class="dc-clue-tag" title="点击查看线索详情">{escape(c)}</span>' for c in clues)
        clues_section = f'<p style="font-size:0.82rem;color:var(--dc-muted);margin:0 0 8px;">{escape(copy["draft_clues_title"])}</p><div class="dc-clue-list">{clues_html}</div><p style="font-size:0.78rem;color:var(--dc-green-deep);margin:0 0 6px;font-style:italic;">以上线索已用于生成下方解读</p>'
    else:
        clues_section = f'<p style="color:var(--dc-muted);font-size:0.82rem;font-style:italic;">{escape(copy.get("clues_empty", "描述梦境后，线索会自动提取"))}</p>'
    resolved_tip = tip_text if tip_text else copy["today_tip_text"]
    if draft_text:
        draft_html = f'<p class="dc-draft-preview">{escape(draft_text)}</p>'
        skeleton_html = ""
    elif has_interpretation:
        draft_html = f'<p class="dc-draft-preview">{escape(copy["interpretation_empty"])}</p>'
        skeleton_html = ""
    else:
        draft_html = ""
        skeleton_html = """<div class="dc-skeleton-wrap">
      <div class="dc-skeleton-line" style="width:90%"></div>
      <div class="dc-skeleton-line" style="width:75%"></div>
      <div class="dc-skeleton-line" style="width:60%"></div>
    </div>"""
    return f"""
<div class="dc-right-sidebar">
  <div class="dc-right-card">
    <h3>{escape(copy['draft_title'])}</h3>
    {clues_section}
    <p style="font-size:0.82rem;color:var(--dc-muted);margin:0 0 6px;">{escape(copy['draft_interpretation_title'])}</p>
    {draft_html}
    {skeleton_html}
  </div>
  <div class="dc-right-card dc-tip-card">
    <h3>{escape(copy['today_tip_title'])}</h3>
    <p>{escape(resolved_tip)}</p>
  </div>
</div>
""".strip()


def _preview_clues_from_text(dream_text: str, language: str = DEFAULT_LANGUAGE) -> list[str]:
    text = (dream_text or "").strip()
    if not text:
        return []
    if normalize_language(language) == "zh":
        keywords = ["桥", "水", "电梯", "按钮", "老楼", "房间", "雨", "鞋", "考试", "火车", "手机", "一个人", "阴天"]
        found = [word for word in keywords if word in text]
        if found:
            return found[:4]
        chunks = [part.strip(" ，。！？；、\n") for part in text.replace("\n", "，").split("，")]
        return [part for part in chunks if len(part) >= 2][:4]
    words = [w.strip(".,!?;:()[]{}\"'").lower() for w in text.split()]
    stop = {"the", "and", "that", "with", "from", "into", "was", "were", "dream", "dreamed", "i", "me", "my", "a", "an", "of", "to", "in"}
    clues = []
    for word in words:
        if len(word) > 3 and word not in stop and word not in clues:
            clues.append(word)
        if len(clues) >= 4:
            break
    return clues


def _draft_preview_text(dream_text: str, language: str = DEFAULT_LANGUAGE) -> str:
    clues = _preview_clues_from_text(dream_text, language)
    if not clues:
        return ""
    if normalize_language(language) == "zh":
        joined = "、".join(clues)
        return f"目前可以先把「{joined}」当作梦里的锚点。它们可能在提示一种情绪、关系或正在面对的变化，继续补充细节后会生成更完整的解读。"
    joined = ", ".join(clues)
    return f"Draft: {joined} can already act as anchors in this dream. They may point to a feeling, relationship, or change you are working through. Add a little more detail for a fuller interpretation."


def _draft_sidebar_from_text(dream_text: str, language: str = DEFAULT_LANGUAGE) -> str:
    language = normalize_language(language)
    text = (dream_text or "").strip()
    if not text:
        return _right_sidebar_html(language)
    clues = _preview_clues_from_text(text, language)
    draft_text = _draft_preview_text(text, language)
    return _right_sidebar_html(language, clues=clues, draft_text=draft_text)


def _history_panel_html(language: str = DEFAULT_LANGUAGE, session_json: str = "") -> str:
    copy = copy_for(language)
    try:
        session = json.loads(session_json) if session_json else {}
    except json.JSONDecodeError:
        session = {}
    intake = session.get("intake", {})
    history = intake.get("dream_text", "")
    if not history:
        return f'<div class="dc-history-panel"><h4>{escape(copy["history_title"])}</h4><p style="color:var(--dc-muted);font-size:0.85rem;">{escape(copy["history_empty"])}</p></div>'
    return f'<div class="dc-history-panel"><h4>{escape(copy["history_title"])}</h4><div class="dc-history-item"><strong>{escape(copy["history_dream_label"])}</strong><p>{escape(history[:200])}</p></div></div>'


def _notification_panel_html(language: str = DEFAULT_LANGUAGE, view_json: str = "") -> str:
    copy = copy_for(language)
    view = _load_view(view_json)
    status = view.get("status", "declaration")
    messages = []
    if status == "tip":
        messages.append(copy["notification_tip_ready"])
    elif status == "error":
        messages.append(copy["notification_error"])
    if not messages:
        messages.append(copy["notification_empty"])
    items = "".join(f"<p>{escape(m)}</p>" for m in messages)
    return f'<div class="dc-notification-panel"><h4>{escape(copy["notification_title"])}</h4>{items}</div>'


def _status_label(language: str, status: str) -> str:
    copy = copy_for(language)
    status_map = {
        "declaration": copy["qa_flow_status"],
        "record": copy["qa_flow_status"],
        "ask": copy["qa_flow_status"],
        "tip": copy.get("qa_flow_tip_status", copy["qa_flow_status"]),
        "error": copy.get("qa_flow_error_status", copy["qa_flow_status"]),
    }
    return status_map.get(status, copy["qa_flow_status"])


def _menu_panel_html(language: str = DEFAULT_LANGUAGE, current_backend: str = "modal") -> str:
    copy = copy_for(language)
    mode_text = copy["menu_mode_text"]
    return f"""<div class="dc-menu-panel">
  <p><strong>{escape(copy['menu_mode_label'])}:</strong> {escape(mode_text)}</p>
  <div style="margin-top:12px;border-top:1px solid var(--dc-line);padding-top:12px;">
    <label style="font-size:0.82rem;font-weight:600;color:var(--dc-ink);display:block;margin-bottom:6px;">{escape(copy['menu_language'])}</label>
    <div id="dc-menu-language-wrap"></div>
  </div>
  <div style="margin-top:12px;border-top:1px solid var(--dc-line);padding-top:12px;">
    <p style="font-size:0.85rem;color:var(--dc-ink);margin:0 0 4px;font-weight:600;">{escape(copy['menu_restart'])}</p>
    <p style="font-size:0.78rem;color:var(--dc-muted);margin:0 0 8px;">{escape(copy['menu_restart_desc'])}</p>
    <div id="dc-menu-restart-wrap"></div>
  </div>
</div>"""


def _notification_count(view_json: str = "") -> int:
    view = _load_view(view_json)
    status = view.get("status", "declaration")
    return 1 if status in {"ask", "error"} else 0


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


def _toggle_history(history_visible, session_json, language):
    language = normalize_language(language)
    copy = copy_for(language)
    new_visible = not history_visible
    return (
        gr.update(visible=new_visible),
        new_visible,
        _history_panel_html(language, session_json),
    )


def _toggle_notifications(notifications_visible, view_json, language):
    language = normalize_language(language)
    copy = copy_for(language)
    new_visible = not notifications_visible
    return (
        gr.update(visible=new_visible),
        new_visible,
        _notification_panel_html(language, view_json),
    )


def _toggle_menu(menu_visible, language):
    language = normalize_language(language)
    copy = copy_for(language)
    new_visible = not menu_visible
    return (
        gr.update(visible=new_visible),
        new_visible,
        _menu_panel_html(language),
        gr.update(value=language),
        gr.update(value=copy["menu_restart"]),
    )


def _append_chip(dream_text, prefix):
    current = dream_text or ""
    if current and not current.endswith("\n"):
        current += "\n"
    return current + prefix


def _toggle_expand(expand_visible, card_html, language):
    language = normalize_language(language)
    copy = copy_for(language)
    new_visible = not expand_visible
    if not card_html:
        content = f"<p style='color:var(--dc-muted);font-size:0.88rem;'>{escape(copy['interpretation_empty'])}</p>"
    else:
        content = card_html
    return (
        gr.update(visible=new_visible),
        new_visible,
        content,
    )


def _save_tip(tip_saved, language):
    language = normalize_language(language)
    copy = copy_for(language)
    new_saved = not tip_saved
    label = copy["tip_saved"] if new_saved else copy["tip_save"]
    icon = "♥" if new_saved else "♡"
    return (
        new_saved,
        gr.update(value=f"{icon} {label}"),
    )


def build_demo() -> gr.Blocks:
    initial_language = "zh"
    initial_state, initial_view = initial_mobile_state(language=initial_language)
    initial = _load_view(initial_view)
    initial_copy = copy_for(initial_language)

    with gr.Blocks(css=CSS, title=APP_TITLE) as demo:
        with gr.Column(elem_classes=["dc-app-shell"]):
            session_state = gr.State(initial_state)
            view_state = gr.State(initial_view)
            audio_input = gr.State(None)
            history_visible = gr.State(False)
            notifications_visible = gr.State(False)
            menu_visible = gr.State(False)
            expand_visible = gr.State(False)
            tip_saved = gr.State(False)

            topbar_html = gr.HTML(_topbar_html(initial_language, _notification_count(initial_view)))
            with gr.Row(elem_classes=["dc-topbar-buttons"]):
                language = gr.Radio(
                    label=initial_copy["language_label"],
                    choices=LANGUAGE_OPTIONS,
                    value=initial_language,
                    elem_classes=["dc-language-switch"],
                )
                reset_button_top = gr.Button(
                    initial_copy["reset_button"],
                    elem_classes=["dc-icon-btn"],
                    size="sm",
                    variant="secondary",
                )

            with gr.Row(elem_classes=["dc-main-layout"]):
                with gr.Column(elem_classes=["dc-flow-column", "dc-center"]):
                    step_pill_bar = gr.HTML(_step_pill_bar_html(initial_language, 1))
                    center_flow_html = gr.HTML(_center_flow_html(initial_language))
                    notice = gr.HTML(_notice_html(initial), visible=False)
                    with gr.Group(visible=True, elem_classes=["dc-stage"]) as declaration_group:
                        welcome_html = gr.HTML(_welcome_bubble_html(initial_language))
                        with gr.Row(elem_classes=["dc-chat-input-row"]):
                            dream_text = gr.Textbox(
                                label=initial_copy["dream_label"],
                                placeholder=initial_copy["dream_placeholder"],
                                lines=3,
                                value="",
                                elem_classes=["dc-dream-text"],
                                show_label=False,
                                container=False,
                            )
                            submit_button = gr.Button(
                                initial_copy["submit_button"],
                                variant="primary",
                                elem_classes=["dc-send-btn"],
                                min_width=80,
                            )
                        with gr.Row(elem_classes=["dc-chip-row"]):
                            chip_emotion = gr.Button(
                                initial_copy["qa_flow_chip_emotion"],
                                elem_classes=["dc-chip-btn"],
                                size="sm",
                                variant="secondary",
                            )
                            chip_scene = gr.Button(
                                initial_copy["qa_flow_chip_scene"],
                                elem_classes=["dc-chip-btn"],
                                size="sm",
                                variant="secondary",
                            )
                            chip_character = gr.Button(
                                initial_copy["qa_flow_chip_character"],
                                elem_classes=["dc-chip-btn"],
                                size="sm",
                                variant="secondary",
                            )
                            chip_object = gr.Button(
                                initial_copy["qa_flow_chip_object"],
                                elem_classes=["dc-chip-btn"],
                                size="sm",
                                variant="secondary",
                            )
                            example_button = gr.Button(
                                initial_copy["example_button"],
                                elem_classes=["dc-chip-btn"],
                                size="sm",
                                variant="secondary",
                            )
                        image_input = gr.Image(
                            label=initial_copy["image_label"],
                            type="filepath",
                            height=80,
                            visible=True,
                            elem_classes=["dc-image-upload"],
                        )

                    with gr.Group(visible=False, elem_classes=["dc-stage", "dc-question"]) as question_group:
                        question_markdown = gr.HTML(_question_markdown(initial, initial_language))
                        answer_text = gr.Textbox(
                            label=initial_copy["answer_label"],
                            placeholder=initial_copy["answer_placeholder"],
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
                            copy_button = gr.Button(initial_copy["copy_button"], variant="secondary", elem_id="dc-copy-btn")
                            reset_button = gr.Button(initial_copy["reset_button"], variant="secondary")
                        card_text = gr.Textbox(
                            label=initial_copy["copy_label"],
                            value="",
                            lines=8,
                            show_copy_button=True,
                            elem_classes=["dc-hidden-text"],
                            elem_id="dc-card-text",
                        )

                with gr.Column(elem_classes=["dc-right-sidebar"]):
                    right_sidebar_html = gr.HTML(_right_sidebar_html(initial_language))
                    expand_button = gr.Button(
                        initial_copy["draft_expand_button"],
                        elem_classes=["dc-expand-btn"],
                        variant="secondary",
                    )
                    with gr.Group(visible=False, elem_classes=["dc-interpretation-panel"]) as interpretation_panel:
                        interpretation_html = gr.HTML("")
                    save_button = gr.Button(
                        f"♡ {initial_copy['today_tip_save']}",
                        elem_classes=["dc-save-btn"],
                        variant="secondary",
                    )
                    with gr.Group(visible=False, elem_classes=["dc-history-panel-group"]) as history_panel:
                        history_html = gr.HTML(_history_panel_html(initial_language))
                    with gr.Group(visible=False, elem_classes=["dc-notification-panel-group"]) as notification_panel:
                        notification_html = gr.HTML(_notification_panel_html(initial_language))
                    with gr.Group(visible=False, elem_classes=["dc-menu-panel-group"]) as menu_panel:
                        menu_html = gr.HTML(_menu_panel_html(initial_language))
                        menu_language_dropdown = gr.Dropdown(
                            label=initial_copy["menu_language"],
                            choices=LANGUAGE_OPTIONS,
                            value=initial_language,
                            elem_id="dc-menu-language",
                        )
                        menu_restart_button = gr.Button(
                            initial_copy["menu_restart"],
                            variant="secondary",
                            elem_id="dc-menu-restart",
                        )

        with gr.Row(elem_classes=["dc-advanced-row"]):
            with gr.Column(elem_classes=["dc-side-panel"]):
                mood_section_html = gr.HTML(_section_title_html(2, initial_copy["side_title"]))
                mood = gr.Dropdown(
                    label=initial_copy["mood_label"],
                    choices=mood_options_for(initial_language),
                    value=default_mood_for(initial_language),
                )
                side_stamp_html = gr.HTML(_side_stamp_html(initial_language))
                with gr.Accordion("Advanced", open=False, elem_classes=["dc-dev"]):
                    dev_help_html = gr.HTML(_dev_help_html(initial_language))
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
                    asr_backend = gr.State(DEFAULT_ASR_BACKEND)
                    with gr.Accordion("Advanced endpoints", open=False, elem_classes=["dc-dev-advanced"]):
                        text_endpoint = gr.Textbox(label="Text endpoint", value="")
                        vision_endpoint = gr.Textbox(label="Image endpoint", value="")
                        asr_endpoint = gr.State("")
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
                        asr_timeout_seconds = gr.State(DEFAULT_ASR_TIMEOUT_SECONDS)
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
                        asr_latency_budget_ms = gr.State(DEFAULT_ASR_LATENCY_BUDGET_MS)
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
                    debug_json = gr.Code(
                        label="Current state",
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
            right_sidebar_html,
            center_flow_html,
            step_pill_bar,
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
        copy_button.click(
            None,
            inputs=[card_text],
            outputs=[copy_button],
            js="""(text) => {
                const btn = document.querySelector('.dc-copy-feedback') || document.querySelector('.dc-actions button:nth-child(3)');
                const orig = btn ? btn.textContent : '';
                if (text && navigator.clipboard) {
                    navigator.clipboard.writeText(text).then(() => {
                        if (btn) { btn.textContent = '✓ 已复制'; setTimeout(() => btn.textContent = orig, 1500); }
                    }).catch(() => {
                        if (btn) { btn.textContent = '✓ 已复制'; setTimeout(() => btn.textContent = orig, 1500); }
                    });
                } else if (text) {
                    const tmp = document.createElement('textarea');
                    tmp.value = text;
                    document.body.appendChild(tmp);
                    tmp.select();
                    document.execCommand('copy');
                    document.body.removeChild(tmp);
                    if (btn) { btn.textContent = '✓ 已复制'; setTimeout(() => btn.textContent = orig, 1500); }
                }
                return [gr.update()];
            }""",
        )
        reset_button.click(
            _reset,
            inputs=[language, text_backend, vision_backend] + settings_inputs,
            outputs=outputs + [dream_text, answer_text, image_input, audio_input, mood],
        )
        reset_button_top.click(
            _reset,
            inputs=[language, text_backend, vision_backend] + settings_inputs,
            outputs=outputs + [dream_text, answer_text, image_input, audio_input, mood],
        )

        def _example(selected_language):
            selected_language = normalize_language(selected_language)
            return EXAMPLE_DREAMS[selected_language], EXAMPLE_MOODS[selected_language]

        example_button.click(_example, inputs=language, outputs=[dream_text, mood])
        dream_text.input(_draft_sidebar_from_text, inputs=[dream_text, language], outputs=[right_sidebar_html])

        expand_button.click(
            _toggle_expand,
            inputs=[expand_visible, card_html, language],
            outputs=[interpretation_panel, expand_visible, interpretation_html],
        )
        save_button.click(
            _save_tip,
            inputs=[tip_saved, language],
            outputs=[tip_saved, save_button],
        )

        def _make_chip_handler(prefix_key):
            def handler(text, lang):
                lang = normalize_language(lang)
                prefix = copy_for(lang)[prefix_key]
                return _append_chip(text, prefix)
            return handler

        chip_emotion.click(
            _make_chip_handler("chip_emotion_prefix"),
            inputs=[dream_text, language],
            outputs=[dream_text],
        )
        chip_scene.click(
            _make_chip_handler("chip_scene_prefix"),
            inputs=[dream_text, language],
            outputs=[dream_text],
        )
        chip_character.click(
            _make_chip_handler("chip_character_prefix"),
            inputs=[dream_text, language],
            outputs=[dream_text],
        )
        chip_object.click(
            _make_chip_handler("chip_object_prefix"),
            inputs=[dream_text, language],
            outputs=[dream_text],
        )

        def _language_ui(selected_language, current_view_json):
            selected_language = normalize_language(selected_language)
            copy = copy_for(selected_language)
            moods = mood_options_for(selected_language)
            view = _load_view(current_view_json)
            status = view.get("status", "declaration")
            clues = _extract_clues(view)
            tip_text = _extract_tip_text(view)
            has_interp = bool(view.get("card_html"))
            status_label = _status_label(selected_language, status)
            return (
                _topbar_html(selected_language, _notification_count(current_view_json)),
                _step_pill_bar_html(selected_language),
                _center_flow_html(selected_language, status_label),
                _right_sidebar_html(selected_language, clues, tip_text, has_interp),
                gr.update(visible=False),
                _welcome_bubble_html(selected_language),
                gr.update(label=copy["dream_label"], placeholder=copy["dream_placeholder"]),
                gr.update(value=copy["submit_button"]),
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
                gr.update(value=copy["qa_flow_chip_emotion"]),
                gr.update(value=copy["qa_flow_chip_scene"]),
                gr.update(value=copy["qa_flow_chip_character"]),
                gr.update(value=copy["qa_flow_chip_object"]),
                gr.update(value=copy["draft_expand_button"]),
                gr.update(value=f"♡ {copy['today_tip_save']}"),
                gr.update(value=copy["reset_button"]),
            )

        language.change(
            _language_ui,
            inputs=[language, view_state],
            outputs=[
                topbar_html,
                step_pill_bar,
                center_flow_html,
                right_sidebar_html,
                notice,
                welcome_html,
                dream_text,
                submit_button,
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
                chip_emotion,
                chip_scene,
                chip_character,
                chip_object,
                expand_button,
                save_button,
                reset_button_top,
            ],
        )

    return demo
