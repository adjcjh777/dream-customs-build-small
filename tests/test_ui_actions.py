import json
import inspect
from datetime import date

from dream_customs.ui.actions import answer_to_card_action, initial_mobile_state, skip_to_card_action, submit_dream_action
import dream_customs.ui.app as ui_app
from dream_customs.ui.app import _reset
from dream_customs.ui.copy import DEFAULT_MOOD, PROCESSING_NOTE
from dream_customs.ui.styles import CSS


def test_mobile_defaults_to_modal_backends():
    _state, view_json = initial_mobile_state()
    view = json.loads(view_json)

    assert view["debug"]["text_backend"] == "modal"
    assert view["debug"]["vision_backend"] == "modal"


def test_runtime_settings_are_collapsed_for_public_flow():
    source = inspect.getsource(ui_app.build_demo)

    assert 'gr.Accordion("Advanced", open=False' in source
    assert 'with gr.Accordion(initial_copy["debug_title"], open=False' in source


def test_voice_input_keeps_modal_asr_component_but_uses_inline_mic_button():
    source = inspect.getsource(ui_app.build_demo)

    assert "audio_input = gr.Audio(" in source
    assert 'sources=["upload"]' in source
    assert 'sources=["microphone", "upload"]' not in source
    assert 'type="filepath"' in source
    assert "visible=False" in source
    assert "mic_html = gr.HTML(_mic_html(DEFAULT_LANGUAGE))" in source
    assert "audio_input = gr.State(None)" not in source
    assert 'value=DEFAULT_ASR_BACKEND' in source


def test_image_upload_is_composer_plus_drawer():
    source = inspect.getsource(ui_app.build_demo)

    assert "attachment_html = gr.HTML(_attachment_html(DEFAULT_LANGUAGE))" in source
    assert 'elem_classes=["dc-image-popover"]' in source
    assert 'image_input = gr.Image(' in source
    assert 'sources=["upload", "clipboard"]' in source
    assert "gr.Accordion(" not in source.split("image_input = gr.Image(")[0].split("with gr.Group(elem_classes=[\"dc-composer\"]):")[-1]


def test_image_popover_uses_unified_upload_clipboard_ui():
    assert "data-upload" in ui_app._attachment_html("en")
    assert "data-paste" in ui_app._attachment_html("zh")
    assert "上传图片" in ui_app._attachment_html("zh")
    assert ".dc-image-popover [data-testid=\"source-select\"]" in CSS
    assert "border-top: 0 !important;" in CSS
    assert '[aria-label="Capture from camera"]' in CSS
    assert "display: none !important;" in CSS
    assert ".dc-image-upload-copy" in CSS
    assert ".dc-image-label-copy" in inspect.getsource(ui_app)
    assert "clipboardSelected ? copy.paste : copy.upload" in inspect.getsource(ui_app)


def test_composer_scripts_are_attached_to_blocks():
    source = inspect.getsource(ui_app.build_demo)

    assert "with gr.Blocks(css=CSS, js=VOICE_JS, title=APP_TITLE)" in source
    assert "mic_html = gr.HTML(_mic_html(DEFAULT_LANGUAGE))" in source
    assert "attachment_html = gr.HTML(_attachment_html(DEFAULT_LANGUAGE))" in source


def test_hero_stepper_tracks_app_status():
    ask_html = ui_app._hero_html(status="ask")
    tip_html = ui_app._hero_html(status="tip")

    assert '<span class="dc-step is-complete"><strong>1</strong>' in ask_html
    assert '<i class="dc-stepper-line is-complete" aria-hidden="true"></i>' in ask_html
    assert '<span class="dc-step is-active" aria-current="step"><strong>2</strong>' in ask_html
    assert '<span class="dc-step is-complete"><strong>3</strong>' in tip_html
    assert '<span class="dc-step is-active" aria-current="step"><strong>4</strong>' in tip_html
    assert tip_html.count("dc-stepper-line is-complete") == 3


def test_hero_subtitle_explains_app_instead_of_legacy_name():
    hero_html = ui_app._hero_html()

    assert "grounded Today Tip" in hero_html
    assert "Dream Customs" not in hero_html


def test_side_panel_dropdown_hover_stays_readable():
    assert '.dc-side-panel .dc-section-title strong' in CSS
    assert '.gradio-container [role="option"]:hover' in CSS
    assert 'background: var(--dqa-sage-soft) !important;' in CSS
    assert 'color: var(--dqa-ink) !important;' in CSS
    assert '.dc-side-panel .block:has(input[role="listbox"])' in CSS
    assert 'resize: none !important;' in CSS
    assert 'pointer-events: none !important;' in CSS
    assert '[aria-expanded="true"]) .dropdown-arrow' in CSS
    assert '.wrap-inner.show_options' in CSS
    assert 'transform: rotate(180deg) !important;' in CSS
    assert '.dc-side-panel .block:has(input[role="listbox"]) .wrap-inner' in CSS
    assert '.dc-side-panel .block:has(input[role="listbox"]) .secondary-wrap' in CSS
    assert '--input-border-width: 0px;' in CSS
    assert '--block-border-width: 0px;' in CSS


def test_advanced_panel_uses_compact_readable_controls():
    assert '.dc-side-panel .dc-dev-help span' in CSS
    assert 'color: #60717a !important;' in CSS
    assert '.dc-side-panel .dc-dev .block:has(input[role="listbox"])' in CSS
    assert 'padding: 12px 14px !important;' in CSS
    assert '.dc-side-panel .dc-dev .block:has(input[role="listbox"]) input[role="listbox"]' in CSS
    assert 'font-size: 0.94rem !important;' in CSS
    assert '.dc-side-panel .dc-dev > button' in CSS
    assert 'min-height: 46px !important;' in CSS


def test_processing_note_is_story_copy_not_backend_jargon():
    lowered = PROCESSING_NOTE.lower()

    assert "grounded question" in lowered
    assert "today tip" in lowered
    assert "model routes" not in lowered
    assert "fallback" not in lowered
    assert "token" not in lowered
    assert "endpoint" not in lowered
    assert "debug" not in lowered


def test_mobile_reset_restores_calm_mood():
    settings_values = [
        "",
        "",
        "",
        "http://localhost:11434",
        "hf.co/openbmb/MiniCPM5-1B-GGUF:Q8_0",
        "openbmb/minicpm-v4.6",
        60,
        60,
        0.2,
        0.1,
        780,
        320,
        "demo",
        "",
        45,
        3500,
        6500,
        2500,
    ]
    result = _reset("demo", "demo", *settings_values)

    assert result[-1] == DEFAULT_MOOD


def test_zerogpu_probe_is_importable_without_local_gpu():
    from dream_customs.zerogpu import zerogpu_startup_probe

    assert zerogpu_startup_probe() == {"status": "ok", "purpose": "zerogpu-startup-detection"}


def test_mobile_mvp_submit_then_skip_generates_today_tip():
    state, view_json = submit_dream_action(
        dream_text="I dreamed of a late elevator.",
        mood="Uneasy",
        text_backend="demo",
        vision_backend="demo",
    )
    view = json.loads(view_json)

    assert view["status"] == "ask"
    assert view["question"]
    assert len(view["questions"]) == 1
    assert "DC-DEMO-014" not in view["card_text"]

    state, view_json = skip_to_card_action(state)
    view = json.loads(view_json)

    assert view["status"] == "tip"
    assert view["phase"] == "tip"
    assert "Today Tip" in view["card_title"]
    assert "电梯" in view["card_text"] or "elevator" in view["card_text"].lower()
    assert "DC-DEMO-014" not in view["card_text"]
    assert "Today Tip" in view["card_html"]


def test_mobile_mvp_zh_language_switch_keeps_chinese_today_tip():
    state, _view_json = submit_dream_action(
        dream_text="我梦到电梯按钮融化，楼层数字停在 14。",
        mood="焦虑",
        text_backend="demo",
        vision_backend="demo",
        language="zh",
    )
    _state, view_json = skip_to_card_action(
        state,
        text_backend="demo",
        vision_backend="demo",
        language="zh",
    )
    view = json.loads(view_json)

    assert view["language"] == "zh"
    assert view["card_title"] == "今日小 Tips"
    assert "今日小 Tips" in view["card_html"]


def test_mobile_mvp_answer_to_card_generates_today_tip():
    state, _view_json = submit_dream_action(
        dream_text="I dreamed the elevator buttons melted and the elevator never came.",
        mood="Foggy",
        text_backend="demo",
        vision_backend="demo",
    )

    state, view_json = answer_to_card_action(
        state,
        "It may be asking me to slow down.",
        text_backend="demo",
        vision_backend="demo",
    )
    view = json.loads(view_json)

    assert view["status"] == "tip"
    assert view["phase"] == "tip"
    assert "It may be asking me to slow down." in view["debug"]["session"]["answer_history"]


def test_english_today_tip_has_no_chinese_anchor_leakage():
    state, _view_json = submit_dream_action(
        dream_text=(
            "I dreamed I was in an elevator where the floor buttons melted like wax. "
            "The number 14 kept blinking, and I felt late but strangely calm."
        ),
        mood="Uneasy",
        text_backend="demo",
        vision_backend="demo",
        language="en",
    )

    _state, view_json = answer_to_card_action(
        state,
        "I want to make starting my overdue email easier without feeling trapped by it.",
        text_backend="demo",
        vision_backend="demo",
        language="en",
    )
    view = json.loads(view_json)
    combined = "\n".join([view["card_text"], view["card_html"]])

    for leaked in ["数字", "电梯", "按钮", "楼层", "融化"]:
        assert leaked not in combined
    assert "overdue email" in combined.lower()
    assert "first sentence" in combined.lower()
    assert "immediately" not in combined.lower()


def test_english_interpretation_uses_user_answer_before_tip():
    state, _view_json = submit_dream_action(
        dream_text=(
            "I dreamed I was in an elevator where the floor buttons melted like wax. "
            "The number 14 kept blinking, and I felt late but strangely calm."
        ),
        mood="Uneasy",
        text_backend="demo",
        vision_backend="demo",
        language="en",
    )

    _state, view_json = answer_to_card_action(
        state,
        "I want to make starting my overdue email easier without feeling trapped by it.",
        text_backend="demo",
        vision_backend="demo",
        language="en",
    )
    view = json.loads(view_json)
    interpretation_line = next(line for line in view["card_text"].splitlines() if line.startswith("Interpretation:"))

    assert "overdue email" in interpretation_line.lower()
    assert "floor 14" in interpretation_line.lower()
