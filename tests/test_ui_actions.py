import json
import inspect
from datetime import date

from dream_customs.ui.actions import answer_to_card_action, initial_mobile_state, skip_to_card_action, submit_dream_action
import dream_customs.ui.app as ui_app
from dream_customs.ui.app import _reset
from dream_customs.ui.copy import DEFAULT_MOOD, PROCESSING_NOTE


def test_mobile_defaults_to_modal_backends():
    _state, view_json = initial_mobile_state()
    view = json.loads(view_json)

    assert view["debug"]["text_backend"] == "modal"
    assert view["debug"]["vision_backend"] == "modal"


def test_runtime_settings_are_collapsed_for_public_flow():
    source = inspect.getsource(ui_app.build_demo)

    assert 'gr.Accordion("Advanced", open=False' in source


def test_voice_input_removed_from_ui():
    source = inspect.getsource(ui_app.build_demo)

    assert "gr.Audio(" not in source
    assert 'sources=["microphone", "upload"]' not in source
    assert "audio_input = gr.State(None)" in source
    assert "dc-mic" not in source
    assert "voice_help" not in source
    assert "Voice input" not in source
    assert "ASR Endpoint" not in source
    assert "Voice note" not in source


def test_new_topbar_and_two_column_layout():
    source = inspect.getsource(ui_app.build_demo)
    topbar_source = inspect.getsource(ui_app._topbar_html)
    center_source = inspect.getsource(ui_app._center_flow_html)
    right_source = inspect.getsource(ui_app._right_sidebar_html)

    assert "dc-topbar" in topbar_source
    assert "dc-main-layout" in source
    assert "dc-center" in center_source
    assert "dc-right-sidebar" in right_source
    assert "topbar_title" in topbar_source
    assert "qa_flow_title" in center_source
    assert "draft_title" in right_source
    assert "today_tip_title" in right_source

    # Step pill bar replaces left sidebar
    assert "step_pill_bar" in source
    assert "dc-step-bar" in inspect.getsource(ui_app._step_pill_bar_html)


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
    assert view["card_title"] == "你的今日 Tip"
    assert "你的今日 Tip" in view["card_html"]


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


def test_fake_html_buttons_are_gone():
    topbar_source = inspect.getsource(ui_app._topbar_html)
    center_source = inspect.getsource(ui_app._center_flow_html)
    right_source = inspect.getsource(ui_app._right_sidebar_html)

    assert "dc-chip" not in center_source
    assert "dc-expand-btn" not in right_source
    assert "dc-save-btn" not in right_source
    assert "<button" not in center_source
    assert "<button" not in right_source


def test_real_gradio_buttons_for_interactions():
    source = inspect.getsource(ui_app.build_demo)

    assert "dc-chip-btn" in source
    assert "dc-expand-btn" in source
    assert "dc-save-btn" in source
    assert "dc-icon-btn" in source


def test_language_switch_is_visible_in_topbar():
    source = inspect.getsource(ui_app.build_demo)

    assert 'elem_classes=["dc-language-switch"]' in source
    assert 'with gr.Row(elem_classes=["dc-topbar-buttons"]):' in source
    topbar_index = source.index('with gr.Row(elem_classes=["dc-topbar-buttons"]):')
    language_index = source.index('language = gr.Radio(')
    assert topbar_index < language_index


def test_advanced_controls_are_visible_collapsed():
    source = inspect.getsource(ui_app.build_demo)

    assert 'with gr.Row(elem_classes=["dc-advanced-row"]):' in source
    assert 'with gr.Accordion("Advanced", open=False' in source
    assert 'with gr.Row(visible=False):' not in source


def test_draft_preview_from_text_updates_right_sidebar():
    html = ui_app._draft_sidebar_from_text(
        "我梦到一座桥，桥下是很急的水，我一个人往前走。",
        "zh",
    )

    assert "桥" in html
    assert "解读" in html
    assert "dc-skeleton-line" not in html


def test_dream_text_has_realtime_draft_handler():
    source = inspect.getsource(ui_app.build_demo)

    assert "dream_text.input(" in source
    assert "_draft_sidebar_from_text" in source


def test_input_stays_visible_when_tip_is_ready():
    source = inspect.getsource(ui_app._updates)

    assert 'visible=status in {"record", "ask", "tip", "error"}' in source


def test_all_new_buttons_have_click_wiring():
    source = inspect.getsource(ui_app.build_demo)

    assert "expand_button.click(" in source
    assert "save_button.click(" in source
    assert "chip_emotion.click(" in source
    assert "chip_scene.click(" in source
    assert "chip_character.click(" in source
    assert "chip_object.click(" in source


def test_new_state_variables_exist():
    source = inspect.getsource(ui_app.build_demo)

    assert "history_visible = gr.State(False)" in source
    assert "notifications_visible = gr.State(False)" in source
    assert "menu_visible = gr.State(False)" in source
    assert "expand_visible = gr.State(False)" in source
    assert "tip_saved = gr.State(False)" in source


def test_toggle_actions_exist():
    source = inspect.getsource(ui_app)
    assert "def _toggle_history(" in source
    assert "def _toggle_notifications(" in source
    assert "def _toggle_menu(" in source
    assert "def _append_chip(" in source
    assert "def _toggle_expand(" in source
    assert "def _save_tip(" in source


def test_chip_append_adds_prefix_to_dream_text():
    from dream_customs.ui.app import _append_chip

    result = _append_chip("", "情绪：")
    assert result == "情绪："

    result = _append_chip("I dreamed of flying", "场景：")
    assert result == "I dreamed of flying\n场景："

    result = _append_chip("some text\n", "人物：")
    assert result == "some text\n人物："


def test_notification_count_reflects_status():
    from dream_customs.ui.app import _notification_count
    import json

    assert _notification_count("") == 0
    assert _notification_count(json.dumps({"status": "declaration"})) == 0
    assert _notification_count(json.dumps({"status": "ask"})) == 1
    assert _notification_count(json.dumps({"status": "tip"})) == 0
    assert _notification_count(json.dumps({"status": "error"})) == 1


def test_no_voice_mic_asr_in_new_panels():
    history_src = inspect.getsource(ui_app._history_panel_html)
    notif_src = inspect.getsource(ui_app._notification_panel_html)
    menu_src = inspect.getsource(ui_app._menu_panel_html)

    for src in [history_src, notif_src, menu_src]:
        assert "voice" not in src.lower()
        assert "microphone" not in src.lower()
        assert "asr" not in src.lower()


# ── Case 1: No fake interactive HTML buttons ──

def test_no_fake_interactive_html_button_attributes():
    """Ensure no HTML elements have onclick, role=button, tabindex, or cursor:pointer style."""
    source = inspect.getsource(ui_app.build_demo)
    topbar_src = inspect.getsource(ui_app._topbar_html)
    center_src = inspect.getsource(ui_app._center_flow_html)
    right_src = inspect.getsource(ui_app._right_sidebar_html)

    for src in [topbar_src, center_src, right_src]:
        assert "onclick=" not in src
        assert "role='button'" not in src
        assert 'role="button"' not in src
        assert "tabindex=" not in src
        assert "cursor:pointer" not in src.replace(" ", "")
        assert "cursor: pointer" not in src


def test_no_html_button_elements_in_panels():
    """History, notification, and menu panels must not contain raw <button> tags."""
    history_src = inspect.getsource(ui_app._history_panel_html)
    notif_src = inspect.getsource(ui_app._notification_panel_html)
    menu_src = inspect.getsource(ui_app._menu_panel_html)

    for src in [history_src, notif_src, menu_src]:
        assert "<button" not in src
        assert "</button>" not in src


# ── Case 2: History / notification / menu toggle ──

def test_toggle_history_returns_new_visible_and_html():
    from dream_customs.ui.app import _toggle_history
    import json

    # Initially not visible
    result = _toggle_history(False, "", "en")
    panel_update, new_visible, html = result
    assert new_visible is True
    assert isinstance(html, str)
    assert "Session History" in html
    assert "No dreams recorded" in html

    # Toggle again: visible -> not visible
    result = _toggle_history(True, "", "en")
    _, new_visible, _ = result
    assert new_visible is False


def test_toggle_history_with_session_data():
    from dream_customs.ui.app import _toggle_history
    import json

    session = json.dumps({
        "intake": {"dream_text": "I dreamed of flying over mountains."}
    })
    result = _toggle_history(False, session, "en")
    _, new_visible, html = result
    assert new_visible is True
    assert "flying over mountains" in html


def test_toggle_history_zh_language():
    from dream_customs.ui.app import _toggle_history

    result = _toggle_history(False, "", "zh")
    _, new_visible, html = result
    assert new_visible is True
    assert "会话历史" in html


def test_toggle_notifications_returns_new_visible_and_html():
    from dream_customs.ui.app import _toggle_notifications

    # Status "declaration" -> empty notification
    view_json = json.dumps({"status": "declaration"})
    result = _toggle_notifications(False, view_json, "en")
    panel_update, new_visible, html = result
    assert new_visible is True
    assert "Notifications" in html
    assert "No new notifications" in html

    # Toggle again
    result = _toggle_notifications(True, view_json, "en")
    _, new_visible, _ = result
    assert new_visible is False


def test_toggle_notifications_tip_status():
    from dream_customs.ui.app import _toggle_notifications

    view_json = json.dumps({"status": "tip"})
    result = _toggle_notifications(False, view_json, "en")
    _, new_visible, html = result
    assert new_visible is True
    assert "Your Today Tip is ready" in html


def test_toggle_notifications_error_status():
    from dream_customs.ui.app import _toggle_notifications

    view_json = json.dumps({"status": "error"})
    result = _toggle_notifications(False, view_json, "en")
    _, new_visible, html = result
    assert new_visible is True
    assert "Something went wrong" in html


def test_toggle_notifications_zh_language():
    from dream_customs.ui.app import _toggle_notifications

    view_json = json.dumps({"status": "tip"})
    result = _toggle_notifications(False, view_json, "zh")
    _, new_visible, html = result
    assert new_visible is True
    assert "今日小 Tips 已生成" in html


def test_toggle_menu_returns_new_visible_and_html():
    from dream_customs.ui.app import _toggle_menu

    result = _toggle_menu(False, "en")
    panel_update, new_visible, html, lang_update, restart_update = result
    assert new_visible is True
    assert "Current mode" in html
    assert "Text-only" in html

    # Toggle again
    result = _toggle_menu(True, "en")
    _, new_visible, _, _, _ = result
    assert new_visible is False


def test_toggle_menu_zh_language():
    from dream_customs.ui.app import _toggle_menu

    result = _toggle_menu(False, "zh")
    _, new_visible, html, _, _ = result
    assert new_visible is True
    assert "当前模式" in html
    assert "纯文本" in html


# ── Case 3: Chip appends prefix to dream_text ──

def test_chip_append_empty_text():
    from dream_customs.ui.app import _append_chip

    result = _append_chip("", "Emotion: ")
    assert result == "Emotion: "


def test_chip_append_nonempty_text():
    from dream_customs.ui.app import _append_chip

    result = _append_chip("I dreamed of flying", "Scene: ")
    assert result == "I dreamed of flying\nScene: "


def test_chip_append_text_already_ends_with_newline():
    from dream_customs.ui.app import _append_chip

    result = _append_chip("some text\n", "Character: ")
    assert result == "some text\nCharacter: "


def test_chip_append_none_input():
    from dream_customs.ui.app import _append_chip

    result = _append_chip(None, "Object: ")
    assert result == "Object: "


def test_chip_append_multiple_times():
    from dream_customs.ui.app import _append_chip

    result = _append_chip("", "Emotion: ")
    result = _append_chip(result, "Scene: ")
    result = _append_chip(result, "Character: ")
    assert result == "Emotion: \nScene: \nCharacter: "


def test_chip_prefixes_match_copy_keys():
    """Ensure chip prefix keys exist in both en and zh copy."""
    from dream_customs.ui.copy import APP_COPY

    for lang in ("en", "zh"):
        copy = APP_COPY[lang]
        for key in ["chip_emotion_prefix", "chip_scene_prefix", "chip_character_prefix", "chip_object_prefix"]:
            assert key in copy
            assert copy[key]  # non-empty


# ── Case 4: Expand draft ──

def test_toggle_expand_with_card_html():
    from dream_customs.ui.app import _toggle_expand

    card_html = "<div class='tip-card'>Today Tip: Be gentle with yourself.</div>"
    result = _toggle_expand(False, card_html, "en")
    panel_update, new_visible, content = result
    assert new_visible is True
    assert "Be gentle with yourself" in content

    # Toggle again to collapse
    result = _toggle_expand(True, card_html, "en")
    _, new_visible, _ = result
    assert new_visible is False


def test_toggle_expand_without_card_html():
    from dream_customs.ui.app import _toggle_expand

    result = _toggle_expand(False, "", "en")
    _, new_visible, content = result
    assert new_visible is True
    assert "Interpretation will appear here" in content


def test_toggle_expand_zh_language():
    from dream_customs.ui.app import _toggle_expand

    result = _toggle_expand(False, "", "zh")
    _, new_visible, content = result
    assert new_visible is True
    assert "提交梦境后" in content


# ── Case 5: Save favorite ──

def test_save_tip_toggles_state():
    from dream_customs.ui.app import _save_tip

    # First save
    new_saved, button_update = _save_tip(False, "en")
    assert new_saved is True
    assert "Saved" in button_update["value"]
    assert "♥" in button_update["value"]

    # Unsave
    new_saved, button_update = _save_tip(True, "en")
    assert new_saved is False
    assert "Save" in button_update["value"]
    assert "♡" in button_update["value"]


def test_save_tip_zh_language():
    from dream_customs.ui.app import _save_tip

    new_saved, button_update = _save_tip(False, "zh")
    assert new_saved is True
    assert "已收藏" in button_update["value"]

    new_saved, button_update = _save_tip(True, "zh")
    assert new_saved is False
    assert "收藏" in button_update["value"]


# ── Case 6: No visible voice/mic/audio/ASR ──

def test_no_voice_mic_audio_asr_in_build_demo():
    """build_demo source must not reference voice input, mic, audio, or ASR UI elements."""
    source = inspect.getsource(ui_app.build_demo)

    # gr.Audio should not appear (audio is a hidden gr.State)
    assert "gr.Audio(" not in source
    assert 'sources=["microphone"' not in source
    assert "dc-mic" not in source
    assert "voice_help" not in source
    assert "Voice input" not in source
    assert "ASR Endpoint" not in source
    assert "Voice note" not in source


def test_no_voice_mic_asr_in_css():
    """CSS should not have mic/voice styling (dc-mic was removed)."""
    from dream_customs.ui.styles import CSS

    assert "dc-mic" not in CSS
    assert "voice-help" not in CSS


def test_audio_input_is_gr_state_not_gr_audio():
    """audio_input must be a gr.State(None), not a gr.Audio component."""
    source = inspect.getsource(ui_app.build_demo)
    assert "audio_input = gr.State(None)" in source


def test_no_mic_recorder_in_hidden_panels():
    """Hidden panels must not contain microphone or ASR references."""
    source = inspect.getsource(ui_app.build_demo)
    assert 'sources=["microphone", "upload"]' not in source


# ── Case 7: New layout classes in config ──

def test_layout_classes_in_css():
    """Verify all expected layout CSS classes are defined."""
    from dream_customs.ui.styles import CSS

    expected_classes = [
        ".dc-topbar",
        ".dc-app-shell",
        ".dc-main-layout",
        ".dc-flow-column",
        ".dc-center",
        ".dc-right-sidebar",
        ".dc-topbar-buttons",
        ".dc-chip-btn",
        ".dc-expand-btn",
        ".dc-save-btn",
        ".dc-step-bar",
        ".dc-welcome-greeting",
    ]
    for cls in expected_classes:
        assert cls in CSS, f"Missing CSS class: {cls}"


def test_two_column_grid_layout():
    """Main layout should use a 2-column grid."""
    from dream_customs.ui.styles import CSS

    assert "grid-template-columns" in CSS
    assert "2.2fr" in CSS
    assert "280px" in CSS
    assert "1080px" in CSS


def test_elem_classes_present_in_build_demo():
    """Verify new elem_classes are used in Gradio components."""
    source = inspect.getsource(ui_app.build_demo)

    expected_classes = [
        "dc-chip-btn",
        "dc-expand-btn",
        "dc-save-btn",
        "dc-topbar-buttons",
        "dc-main-layout",
        "dc-flow-column",
        "dc-center",
        "dc-right-sidebar",
    ]
    for cls in expected_classes:
        assert cls in source, f"Missing elem_class: {cls}"


# ── Case 8: Gradio click dependencies exist ──

def test_topbar_buttons_have_click_handlers():
    """Reset button must have .click() wiring."""
    source = inspect.getsource(ui_app.build_demo)

    assert "reset_button_top.click(" in source


def test_chip_buttons_have_click_handlers():
    """All four chip buttons must have .click() wiring."""
    source = inspect.getsource(ui_app.build_demo)

    assert "chip_emotion.click(" in source
    assert "chip_scene.click(" in source
    assert "chip_character.click(" in source
    assert "chip_object.click(" in source


def test_expand_and_save_buttons_have_click_handlers():
    """Expand and save buttons must have .click() wiring."""
    source = inspect.getsource(ui_app.build_demo)

    assert "expand_button.click(" in source
    assert "save_button.click(" in source


def test_main_flow_buttons_have_click_handlers():
    """Submit, answer, skip, gentle, weird, copy, reset buttons must have .click() wiring."""
    source = inspect.getsource(ui_app.build_demo)

    assert "submit_button.click(" in source
    assert "answer_button.click(" in source
    assert "skip_button.click(" in source
    assert "gentle_button.click(" in source
    assert "weird_button.click(" in source
    assert "copy_button.click(" in source
    assert "reset_button.click(" in source


def test_click_handlers_use_correct_output_components():
    """Toggle handlers must output to their respective panels."""
    source = inspect.getsource(ui_app.build_demo)

    # notification -> notification_panel
    assert "notification_panel" in source
    assert "notifications_visible" in source

    # history -> history_panel
    assert "history_panel" in source
    assert "history_visible" in source

    # menu -> menu_panel
    assert "menu_panel" in source
    assert "menu_visible" in source

    # expand -> interpretation_panel
    assert "interpretation_panel" in source
    assert "expand_visible" in source

    # save -> tip_saved, save_button
    assert "tip_saved" in source


def test_language_change_updates_all_panels():
    """Language change should update topbar, step bar, center flow, and button labels."""
    source = inspect.getsource(ui_app.build_demo)

    assert "language.change(" in source
    # Verify it updates key components
    assert "topbar_html" in source
    assert "step_pill_bar" in source
    assert "center_flow_html" in source
    assert "right_sidebar_html" in source


# ── P0-1: copy_button has real clipboard wiring ──

def test_copy_button_has_js_clipboard_wiring():
    """copy_button must use JavaScript to copy to clipboard, not a no-op lambda."""
    source = inspect.getsource(ui_app.build_demo)

    # Must NOT be a no-op lambda
    assert "lambda text: text" not in source
    # Must use JavaScript callback for clipboard
    assert "navigator.clipboard" in source
    # Must wire copy_button.click
    assert "copy_button.click(" in source


def test_copy_button_has_elem_id():
    """copy_button must have elem_id for JS targeting."""
    source = inspect.getsource(ui_app.build_demo)
    assert 'elem_id="dc-copy-btn"' in source


# ── P0-2: Right sidebar uses dynamic data ──

def test_right_sidebar_accepts_dynamic_params():
    """_right_sidebar_html must accept clues, tip_text, and has_interpretation params."""
    sig = inspect.signature(ui_app._right_sidebar_html)
    param_names = list(sig.parameters.keys())
    assert "clues" in param_names
    assert "tip_text" in param_names
    assert "has_interpretation" in param_names


def test_right_sidebar_dynamic_with_clues():
    """_right_sidebar_html should render custom clues when provided."""
    html = ui_app._right_sidebar_html("en", clues=["Flying", "Ocean"], tip_text="Be calm", has_interpretation=True)
    assert "Flying" in html
    assert "Ocean" in html
    assert "Be calm" in html


def test_right_sidebar_defaults_to_copy_when_empty():
    """_right_sidebar_html should show empty state when no clues given."""
    from dream_customs.ui.copy import copy_for
    html = ui_app._right_sidebar_html("en")
    copy = copy_for("en")
    assert copy["clues_empty"] in html
    assert copy["today_tip_text"] in html


def test_updates_returns_right_sidebar_and_center_flow():
    """_updates must return right_sidebar_html and center_flow_html."""
    result = ui_app._updates("{}", json.dumps({"status": "record", "language": "en"}))
    # 13 total: state, view_json, notice, question_md, card_html, card_text,
    # declaration, question, card, debug, right_sidebar, center_flow, step_pill_bar
    assert len(result) == 13
    assert isinstance(result[10], str)  # right_sidebar_html
    assert isinstance(result[11], str)  # center_flow_html
    assert isinstance(result[12], str)  # step_pill_bar


def test_right_sidebar_included_in_outputs():
    """right_sidebar_html and center_flow_html must be in the outputs list."""
    source = inspect.getsource(ui_app.build_demo)
    # Verify right_sidebar_html appears in the outputs list
    assert "right_sidebar_html," in source
    assert "center_flow_html," in source


# ── P0-3: Skeleton lines conditionally rendered ──

def test_skeleton_hidden_when_interpretation_present():
    """Skeleton lines should disappear when has_interpretation=True."""
    html = ui_app._right_sidebar_html("en", has_interpretation=True)
    assert "dc-skeleton-line" not in html


def test_skeleton_shown_when_no_interpretation():
    """Empty state message should show when has_interpretation=False."""
    html = ui_app._right_sidebar_html("en", has_interpretation=False)
    assert "record more" in html.lower() or "interpretation_empty" in html.lower() or "dc-muted" in html


# ── P1-1: Step card hover removed ──

def test_step_pill_bar_exists():
    """Step pill bar function must exist and return HTML."""
    assert hasattr(ui_app, "_step_pill_bar_html")
    html = ui_app._step_pill_bar_html("en", 1)
    assert "dc-step-bar" in html
    assert "Record" in html


def test_step_pill_bar_has_active_dot():
    """Step pill bar should mark the active step."""
    html = ui_app._step_pill_bar_html("en", 2)
    assert "active" in html
    assert "Ask" in html


# ── P1-2: No mixed language copy ──

def test_zh_copy_has_no_english_in_notice():
    """zh notice_record must not contain English 'Text-only'."""
    from dream_customs.ui.copy import APP_COPY
    assert "Text-only" not in APP_COPY["zh"]["notice_record"]


def test_en_sidebar_tip_label_is_not_tips():
    """en sidebar_tip_label should be 'Tip', not 'Tips'."""
    from dream_customs.ui.copy import APP_COPY
    assert APP_COPY["en"]["sidebar_tip_label"] == "Tip"


# ── P1-3: Avatar menu has language switch and restart ──

def test_menu_panel_includes_language_and_restart():
    """_menu_panel_html must include language selector and restart button placeholders."""
    html = ui_app._menu_panel_html("en")
    assert "Language" in html
    assert "Start over" in html
    assert "dc-menu-language-wrap" in html
    assert "dc-menu-restart-wrap" in html


def test_menu_panel_zh_includes_language_and_restart():
    """_menu_panel_html zh must include language selector and restart button placeholders."""
    html = ui_app._menu_panel_html("zh")
    assert "语言" in html
    assert "重新开始" in html


def test_menu_has_language_dropdown_and_restart_button():
    """build_demo must create menu_language_dropdown and menu_restart_button components."""
    source = inspect.getsource(ui_app.build_demo)
    assert "menu_language_dropdown" in source
    assert "menu_restart_button" in source
    assert 'elem_id="dc-menu-language"' in source
    assert 'elem_id="dc-menu-restart"' in source


def test_reset_button_top_has_click_wiring():
    """reset_button_top must have .click() wiring."""
    source = inspect.getsource(ui_app.build_demo)
    assert "reset_button_top.click(" in source


# ── P1-4: clue-tag has default cursor ──

def test_clue_tag_has_cursor_default():
    """dc-clue-tag should have cursor:default (read-only indicator)."""
    from dream_customs.ui.styles import CSS

    import re
    clue_block = re.search(r'\.dc-clue-tag\s*\{[^}]+\}', CSS)
    assert clue_block is not None
    assert "cursor: default" in clue_block.group()


# ── P2-4: Status label is dynamic ──

def test_status_label_helper_exists():
    """_status_label function must exist and derive labels from status."""
    assert hasattr(ui_app, "_status_label")
    label = ui_app._status_label("en", "tip")
    assert isinstance(label, str)
    assert len(label) > 0


def test_status_label_varies_by_status():
    """_status_label should return different labels for different statuses."""
    label_record = ui_app._status_label("en", "record")
    label_tip = ui_app._status_label("en", "tip")
    label_error = ui_app._status_label("en", "error")
    # At minimum, tip and error should differ from default
    assert label_tip != label_record or label_error != label_record


def test_center_flow_accepts_status_param():
    """_center_flow_html must accept a status parameter."""
    sig = inspect.signature(ui_app._center_flow_html)
    assert "status" in sig.parameters


def test_center_flow_dynamic_status():
    """_center_flow_html should render the provided status text."""
    html = ui_app._center_flow_html("en", status="Custom Status")
    assert "Custom Status" in html


def test_center_flow_defaults_when_no_status():
    """_center_flow_html should use copy default when status is empty."""
    from dream_customs.ui.copy import copy_for
    html = ui_app._center_flow_html("en", status="")
    copy = copy_for("en")
    assert copy["qa_flow_status"] in html


def test_status_label_zh():
    """_status_label should work for zh language."""
    label = ui_app._status_label("zh", "tip")
    assert isinstance(label, str)
    assert len(label) > 0


# ── Issue A: Language switch visible in topbar ──

def test_language_switch_visible_in_topbar_area():
    """Language radio must be in the topbar-buttons row, not hidden."""
    source = inspect.getsource(ui_app.build_demo)
    assert 'dc-topbar-buttons' in source
    assert 'dc-language-switch' in source
    assert "gr.Radio(" in source


# ── Issue B: Advanced debug module visible ──

def test_advanced_row_visible_not_hidden():
    """Advanced row must be visible (collapsed by default, not display:none)."""
    from dream_customs.ui.styles import CSS
    import re
    adv_block = re.search(r'\.dc-advanced-row\s*\{[^}]+\}', CSS)
    assert adv_block is not None
    assert "display: none" not in adv_block.group()
    assert "visibility: hidden" not in adv_block.group()


def test_advanced_accordion_has_debug_controls():
    """Advanced accordion must contain text_backend, vision_backend, etc."""
    source = inspect.getsource(ui_app.build_demo)
    assert 'text_backend' in source
    assert 'vision_backend' in source
    assert 'text_temperature' in source
    assert 'vision_max_tokens' in source


# ── Issue C: No gray backgrounds ──

def test_no_gray_backgrounds_in_product_areas():
    """Product areas should not have突兀 gray backgrounds."""
    from dream_customs.ui.styles import CSS
    import re
    stage_block = re.search(r'\.dc-stage[^{]*\{[^}]+\}', CSS)
    assert stage_block is not None
    stage_css = stage_block.group()
    assert "#ccc" not in stage_css
    assert "#ddd" not in stage_css
    assert "#eee" not in stage_css


# ── Issue D: Real-time draft preview ──

def test_draft_sidebar_helper_exists():
    """_draft_sidebar_from_text helper must exist."""
    assert hasattr(ui_app, '_draft_sidebar_from_text')


def test_draft_sidebar_generates_clues_for_chinese_dream():
    """Draft sidebar should extract clues from Chinese dream text."""
    html = ui_app._draft_sidebar_from_text("我梦到在一座很长的桥上走，下面是很急的水流", "zh")
    assert "桥" in html
    assert "水" in html or "急" in html


def test_draft_sidebar_empty_state():
    """Draft sidebar should show empty state when no text."""
    html = ui_app._draft_sidebar_from_text("", "zh")
    assert "线索" in html or "clue" in html.lower() or "描述" in html


def test_dream_text_triggers_draft_update():
    """dream_text.input must be wired to update right sidebar."""
    source = inspect.getsource(ui_app.build_demo)
    assert "dream_text.input(" in source or "dream_text.change(" in source


# ── Issue E: Center full interpretation ──

def test_card_html_shows_in_center_column():
    """card_html (full interpretation) must be in the center column."""
    source = inspect.getsource(ui_app.build_demo)
    center_section = source[source.index("dc-center"):source.index("dc-right-sidebar")]
    assert "card_html" in center_section or "card_group" in center_section


def test_tip_stage_shows_center_input():
    """In tip stage, center input should remain visible."""
    source = inspect.getsource(ui_app._updates)
    assert "declaration" in source
