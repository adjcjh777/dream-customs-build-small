import re
from datetime import date

import pytest

from dream_customs.models import FakeASRClient, FakeTextClient, FakeVisionClient
from dream_customs.pipeline import (
    add_evidence,
    answer_question,
    ask_questions,
    build_qa_state,
    build_intake,
    create_session,
    dated_permit_id,
    draft_pact,
    finish_today_tip,
    generate_negotiation,
    generate_pact,
    generate_today_tip,
    intake_from_modalities,
    revise_pact,
    seal_pact,
    skip_question,
)
from dream_customs.prompts import pact_prompt, today_tip_prompt
from dream_customs.schema import PactCard, TodayTipCard, VisionWitness


def _today_tip_public_text(card: TodayTipCard) -> str:
    return "\n".join(
        [
            card.dream_summary,
            card.main_question,
            ",".join(card.dream_anchors),
            card.interpretation,
            card.today_tip,
            card.tiny_action,
            card.caring_note,
            card.safety_note,
        ]
    )


def test_dated_permit_id_uses_runtime_date_and_preserves_serial():
    assert dated_permit_id("DREAM2024-001", today=date(2026, 6, 6)) == "DREAM20260606-001"
    assert dated_permit_id("DC-DEMO-014", today=date(2026, 6, 6)) == "DREAM20260606-014"


def test_build_intake_merges_modalities():
    intake = build_intake(
        dream_text="I missed an elevator.",
        voice_transcript="The buttons melted.",
        visual_clues=["blue hallway"],
        mood="anxious",
    )
    assert "elevator" in intake.merged_text()
    assert "blue hallway" in intake.merged_text()


def test_intake_from_modalities_uses_adapters():
    intake = intake_from_modalities(
        dream_text="",
        image_path="demo.png",
        audio_path="demo.wav",
        mood="foggy",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
    )
    merged = intake.merged_text()
    assert "The buttons melted" in merged
    assert "blue hallway" in merged
    assert "Mood: foggy" in merged


def test_generate_negotiation_returns_questions():
    intake = build_intake(dream_text="I missed an elevator.", mood="anxious")
    negotiation = generate_negotiation(intake, FakeTextClient())
    assert negotiation["visitor_name"]
    assert len(negotiation["questions"]) == 3


def test_ask_questions_grounds_generic_question_in_dream_detail():
    session = add_evidence(
        create_session(),
        dream_text=(
            "I dreamed I was at a customs window carrying a suitcase full of wet paper. "
            "The clerk asked me to declare every unfinished promise before sunrise."
        ),
        mood="Uneasy",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
    )

    session = ask_questions(session, FakeTextClient())

    assert "customs window" in session.question_history[0].lower() or "wet paper" in session.question_history[0].lower()


def test_elevator_floor14_demo_anchors_are_clean_for_question_stage():
    intake = build_intake(
        dream_text=(
            "I dreamed I kept missing an elevator. The button for floor 14 melted like wax. "
            "I woke up anxious because it reminded me of an overdue email."
        ),
        mood="Uneasy",
    )
    state = build_qa_state(intake, language="en")

    assert state.dream_anchors[:3] == ["elevator", "floor 14", "melted button"]
    assert "for floor" not in state.dream_anchors


def test_zh_company_nap_splashed_water_keeps_real_anchors():
    session = add_evidence(
        create_session(language="zh"),
        dream_text="我在公司午觉的时候被人泼了一盆水。",
        mood="",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
        language="zh",
    )

    assert any("公司" in anchor for anchor in session.qa_state.dream_anchors)
    assert any("午觉" in anchor or "午休" in anchor for anchor in session.qa_state.dream_anchors)
    assert any("泼" in anchor or "水" in anchor for anchor in session.qa_state.dream_anchors)

    session = ask_questions(session, FakeTextClient(), language="zh")
    first_response = session.question_history[0]

    assert "公司" in first_response or "午觉" in first_response or "泼" in first_response
    assert "夜晚的海" not in first_response
    assert "海浪" not in first_response
    assert "月牙" not in first_response
    assert "小人" not in first_response


def test_zh_plain_water_fragment_does_not_invent_sea_scene():
    session = add_evidence(
        create_session(language="zh"),
        dream_text="水",
        mood="",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
        language="zh",
    )
    session = ask_questions(session, FakeTextClient(), language="zh")

    first_response = session.question_history[0]

    assert "水" in first_response
    assert "夜晚的海" not in first_response
    assert "海浪" not in first_response
    assert "月牙" not in first_response
    assert "小人" not in first_response


def test_today_tip_removes_unsupported_clinical_frame_for_company_water_dream():
    class ClinicalHostedTextClient:
        def generate_today_tip(self, prompt):
            return TodayTipCard(
                dream_summary="你梦见在公司午觉时被人泼水。",
                main_question="这个梦里的水可能在提醒我什么？",
                dream_anchors=["水"],
                followup_questions=[],
                user_answers=[],
                interpretation="「被人泼水」可能是睡眠剥夺或压力过大的信号。",
                today_tip="围绕「公司午觉」留意睡眠问题，必要时寻求专业帮助。",
                tiny_action="把一杯水放在桌上，提醒自己尽快寻求专业帮助。",
                caring_note="如果你持续焦虑或有睡眠问题，建议寻求专业帮助。",
                safety_note="建议寻求专业帮助。",
            )

    intake = build_intake(dream_text="我在公司午觉的时候被人泼了一盆水。")

    card = generate_today_tip(intake, "", ClinicalHostedTextClient(), language="zh")
    combined = card.to_plain_text()

    assert any("公司" in anchor for anchor in card.dream_anchors)
    assert any("午觉" in anchor or "午休" in anchor for anchor in card.dream_anchors)
    assert any("泼" in anchor or "水" in anchor for anchor in card.dream_anchors)
    assert "睡眠剥夺" not in combined
    assert "压力过大" not in combined
    assert "睡眠问题" not in combined
    assert "专业帮助" not in combined
    assert card.safety_note == ""


def test_today_tip_removes_unsupported_emotion_and_generic_wellness_for_company_water_dream():
    class OverreachingHostedTextClient:
        def generate_today_tip(self, prompt):
            return TodayTipCard(
                dream_summary="你梦见在公司午觉时被人泼水。",
                main_question="这个梦里的水可能在提醒我什么？",
                dream_anchors=["公司午觉", "被人泼水"],
                followup_questions=["在「公司、午觉、被人泼水」里，醒来后最强烈的感受是什么？"],
                user_answers=["用户选择跳过这个追问。"],
                interpretation=(
                    "你选择跳过这个追问。梦中的公司可能是在提醒你注意工作与休息的平衡，"
                    "或者暗示你今天需要处理一些工作压力。午觉时被泼水可能象征着突如其来的挑战。"
                ),
                today_tip="明天上班前，先喝一杯温水，或者听一首轻松的音乐。",
                tiny_action="把一杯温水放在桌上提醒自己保持积极。",
                caring_note="如果你感到害怕或孤独，不必过度自责。保持积极心态，明天会更好。",
                safety_note="",
            )

    intake = build_intake(dream_text="我在公司午觉的时候被人泼了一盆水。")

    card = generate_today_tip(
        intake,
        "用户选择跳过这个追问。",
        OverreachingHostedTextClient(),
        language="zh",
        followup_questions=["在「公司、午觉、被人泼水」里，醒来后最强烈的感受是什么？"],
    )
    combined = card.to_plain_text()

    assert "公司" in combined
    assert "被人泼水" in combined or "被人泼了一盆水" in combined
    assert "工作压力" not in combined
    assert "害怕" not in combined
    assert "孤独" not in combined
    assert "保持积极" not in combined
    assert "明天会更好" not in combined
    assert "温水" not in combined
    assert "轻松的音乐" not in combined


def test_generate_pact_returns_card_and_html():
    intake = build_intake(dream_text="I missed an elevator.", mood="anxious")
    card, html = generate_pact(intake, "I want a small start.", FakeTextClient())
    assert card.visitor_name
    assert "Today's Pact" in html


def test_generate_pact_adds_safety_note_for_distress():
    intake = build_intake(dream_text="I might hurt myself if I cannot sleep.")
    card, _html = generate_pact(intake, "", FakeTextClient())
    assert card.safety_note


def test_generate_today_tip_repairs_placeholder_and_stale_model_anchors():
    class StaleHostedTextClient:
        def generate_today_tip(self, prompt):
            return TodayTipCard(
                dream_summary="I dreamed the elevator button melted and the floor number stayed on 14.",
                main_question="What might that dream detail be asking me to notice today?",
                dream_anchors=["that dream detail"],
                followup_questions=["What did the elevator feel like?"],
                user_answers=[],
                interpretation="Maybe that dream detail points to a stuck point.",
                today_tip="For today, borrow one action from that dream detail and write one line.",
                tiny_action="Spend five minutes with that dream detail.",
                caring_note="Noticing one dream detail is enough.",
                safety_note="",
            )

    intake = build_intake(
        dream_text="昨晚我梦见自己在一片大雪地里找不到出口，反复回头看到一扇红色的门却打不开。",
        mood="Neutral",
    )

    card = generate_today_tip(intake, "", StaleHostedTextClient(), language="zh")
    combined = "\n".join(
        [
            card.dream_summary,
            card.main_question,
            ",".join(card.dream_anchors),
            card.interpretation,
            card.today_tip,
            card.tiny_action,
        ]
    )

    assert "梦里的那个细节" not in combined
    assert "that dream detail" not in combined
    assert "电梯" not in combined
    assert "红色" in combined or "雪地" in combined
    assert card.dream_anchors[0] in {"红色的门", "红色门", "大雪地", "雪地"}


def test_generate_today_tip_keeps_answer_history_and_removes_placeholder_text():
    class PlaceholderTextClient:
        def generate_today_tip(self, prompt):
            return TodayTipCard(
                dream_summary="You dreamed about that dream detail.",
                main_question="What might the that dream detail be asking me to notice today?",
                dream_anchors=["that dream detail"],
                followup_questions=[],
                user_answers=[],
                interpretation="Maybe that dream detail points to a stuck point.",
                today_tip="For today, borrow one action from the that dream detail.",
                tiny_action="Spend five minutes with that dream detail.",
                caring_note="This dream detail does not indicate any real-life concerns.",
                safety_note="",
            )

    intake = build_intake(
        dream_text="I dreamed I was in a white hallway looking for a classroom while the teacher kept asking for homework.",
        mood="Uneasy",
    )

    card = generate_today_tip(
        intake,
        "I should message my group lead and send a rough draft tonight.",
        PlaceholderTextClient(),
        language="en",
    )
    combined = "\n".join(
        [
            card.dream_summary,
            card.main_question,
            ",".join(card.dream_anchors),
            "\n".join(card.user_answers),
            card.interpretation,
            card.today_tip,
            card.tiny_action,
            card.caring_note,
        ]
    ).lower()

    assert "that dream detail" not in combined
    assert "white hallway" in combined or "classroom" in combined or "teacher" in combined
    assert "group lead" in combined
    assert "message" in combined
    assert "does not indicate any real-life concerns" not in combined


def test_elevator_floor_14_without_melted_button_does_not_invent_example_detail():
    class ContaminatedElevatorClient:
        def generate_today_tip(self, prompt):
            return TodayTipCard(
                dream_summary="你梦见电梯按钮像蜡一样融化，楼层数字停在 14。",
                main_question="为什么梦里总是卡在电梯口？",
                dream_anchors=["电梯", "融化的按钮", "数字 14"],
                followup_questions=["电梯、融化的按钮和数字 14 里，哪一个最像你最近卡住的感觉？"],
                user_answers=[],
                interpretation="第二层，梦里的「电梯、融化的按钮和数字 14」也许把这种感受变成了画面。",
                today_tip="今天不要逼自己抵达所有楼层；先把「电梯、融化的按钮和数字 14」变成一个只按一次的按钮。",
                tiny_action="用 5 分钟写一个只按这一层的按钮。",
                caring_note="不用解决所有楼层。",
                safety_note="",
            )

    dream_text = (
        "昨晚梦见我在一栋很高的办公楼14层找一封迟迟没发出去的邮件。"
        "电梯一直停在黑暗的走廊，我手里拿着一盏小台灯，感觉有点焦急。"
        "醒来最想知道为什么梦里总是卡在电梯口。"
    )
    session = add_evidence(
        create_session(language="zh"),
        dream_text=dream_text,
        mood="焦急",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
        language="zh",
    )
    session = ask_questions(session, FakeTextClient(), language="zh")

    card = generate_today_tip(
        session.intake,
        "我觉得那封邮件像是我一直拖着的一次工作沟通。",
        ContaminatedElevatorClient(),
        language="zh",
        followup_questions=session.question_history,
    )
    combined = "\n".join(
        [
            session.question_history[0],
            card.dream_summary,
            card.main_question,
            ",".join(card.dream_anchors),
            "\n".join(card.followup_questions),
            card.interpretation,
            card.today_tip,
            card.tiny_action,
            card.caring_note,
        ]
    )

    assert "融化" not in combined
    assert "像蜡" not in combined
    assert "电梯" in combined
    assert "14" in combined
    assert "邮件" in combined or "办公楼" in combined or "台灯" in combined


def test_elevator_melted_button_stays_when_user_supplies_it():
    intake = build_intake(dream_text="我梦见电梯按钮融化，数字停在 14。", mood="焦虑")

    card = generate_today_tip(intake, "用户选择跳过这个追问。", FakeTextClient(), language="zh")
    combined = "\n".join([card.dream_summary, ",".join(card.dream_anchors), card.interpretation, card.today_tip])

    assert "融化" in combined
    assert "电梯" in combined


def test_generate_today_tip_uses_chinese_concrete_answer_in_visible_tip():
    intake = build_intake(
        dream_text=(
            "昨晚梦见我在一栋很高的办公楼14层找一封迟迟没发出去的邮件。"
            "电梯一直停在黑暗的走廊，我手里拿着一盏小台灯，感觉有点焦急。"
            "醒来最想知道为什么梦里总是卡在电梯口。"
        ),
        mood="焦急",
    )

    card = generate_today_tip(
        intake,
        "我觉得那封邮件像是我一直拖着的一次工作沟通，也可能有一点道歉。今天可以先写第一句，不一定马上发出去。",
        FakeTextClient(),
        language="zh",
    )
    visible = "\n".join([card.interpretation, card.today_tip, card.tiny_action])

    assert "邮件" in visible
    assert "第一句" in visible or "第一句话" in visible
    assert "不要求立刻发出" in visible or "不一定马上发" in visible
    assert "融化" not in visible


def test_chinese_email_tip_becomes_real_world_suggestions_and_weird_action():
    intake = build_intake(
        dream_text=(
            "昨晚梦见我在一栋很高的办公楼14层找一封迟迟没发出去的邮件。"
            "电梯一直停在黑暗的走廊，我手里拿着一盏小台灯，感觉有点焦急。"
            "醒来最想知道为什么梦里总是卡在电梯口。"
        ),
        mood="焦急",
    )

    card = generate_today_tip(
        intake,
        "我觉得那封邮件其实是在提醒我有一件事一直没有开始。今天可以先写第一句话，不一定马上发出去。",
        FakeTextClient(),
        language="zh",
    )

    assert "办公楼」当成允许慢慢开始的按钮" not in card.today_tip
    assert "现实" in card.today_tip
    assert "1." not in card.today_tip and "2." not in card.today_tip
    assert "邮件" in card.today_tip
    assert "第一句" in card.today_tip or "第一句话" in card.today_tip
    assert "便利贴" in card.tiny_action or "纸" in card.tiny_action
    assert "按钮" in card.tiny_action or "电梯" in card.tiny_action
    assert "按一下" in card.tiny_action or "画" in card.tiny_action
    assert "给自己 5 分钟，只打开那封邮件" not in card.tiny_action
    assert "这份这个感受" not in card.caring_note


def test_generate_today_tip_follows_user_question_and_comfort_need_in_chinese():
    intake = build_intake(
        dream_text="我梦到自己掉进海里，醒来很害怕。我想知道这是不是说明我快撑不住了？",
        mood="害怕",
    )

    card = generate_today_tip(intake, "我最近工作压力很大，真的很想被安慰一下。", FakeTextClient(), language="zh")
    combined = "\n".join(
        [
            card.main_question,
            card.interpretation,
            card.today_tip,
            card.tiny_action,
            card.caring_note,
        ]
    )

    assert "撑不住" in card.main_question
    assert "海" in combined
    assert "压力" in combined or "害怕" in combined
    assert "第一层" in card.interpretation and "第二层" in card.interpretation
    assert "太脆弱" in card.caring_note
    assert "电梯" not in combined
    assert "只打开那件事" not in combined


def test_generate_today_tip_answers_sad_relationship_question_without_productivity_template():
    intake = build_intake(
        dream_text="我梦到前任发消息又消失了，我醒来很难过，想知道是不是我还没走出来。",
        mood="难过",
    )

    card = generate_today_tip(intake, "我不想要鸡汤，只想知道为什么这么难受。", FakeTextClient(), language="zh")
    combined = "\n".join([card.main_question, card.interpretation, card.today_tip, card.caring_note])

    assert "为什么这么难受" in card.main_question or "没走出来" in card.main_question
    assert "难受" in combined or "难过" in combined
    assert "消息" in combined
    assert "第一句话" not in combined
    assert "打开任务" not in combined


def test_generate_today_tip_keeps_english_emotional_question_from_becoming_task_advice():
    intake = build_intake(
        dream_text="I dreamed I was drowning in dark water and woke scared. Does this mean I am not coping?",
        mood="scared",
    )

    card = generate_today_tip(intake, "I need comfort, not productivity advice.", FakeTextClient(), language="en")
    combined = "\n".join(
        [
            card.main_question,
            card.interpretation,
            card.today_tip,
            card.tiny_action,
            card.caring_note,
        ]
    ).lower()

    assert "not coping" in card.main_question.lower()
    assert "water" in combined
    assert "first" in card.interpretation.lower() and "second" in card.interpretation.lower()
    assert "not weak" in combined or "comforted" in combined
    assert "open the task" not in combined
    assert "first line" not in combined


def test_today_tip_rejects_hollow_productivity_advice_even_when_it_mentions_anchor():
    class HollowProductivityClient:
        def generate_today_tip(self, prompt):
            return TodayTipCard(
                dream_summary="你梦见旧图书馆里有一把打不开的钥匙。",
                main_question="这个梦在提醒我什么？",
                dream_anchors=["旧图书馆", "钥匙"],
                followup_questions=["旧图书馆和钥匙里，哪个细节最抓住你？"],
                user_answers=[],
                interpretation="「旧图书馆」说明你需要优化效率，整理待办清单。",
                today_tip="今天把「旧图书馆」当作提高效率的提醒，整理待办清单并保持专注。",
                tiny_action="写三项待办事项，按优先级排序。",
                caring_note="保持专注就会更好。",
                safety_note="",
            )

    intake = build_intake(
        dream_text="我梦见自己在旧图书馆里拿着一把旧钥匙，却找不到它能打开哪扇门。",
        mood="困惑",
    )

    card = generate_today_tip(intake, "用户选择跳过这个追问。", HollowProductivityClient(), language="zh")
    combined = "\n".join([card.interpretation, card.today_tip, card.tiny_action, card.caring_note])

    assert "旧图书馆" in combined or "钥匙" in combined
    assert "效率" not in combined
    assert "待办" not in combined
    assert "专注" not in combined
    assert "优先级" not in combined
    assert "保持积极" not in combined


def test_today_tip_absorbs_non_template_followup_answer_as_real_life_cue():
    class AnchorOnlyClient:
        def generate_today_tip(self, prompt):
            return TodayTipCard(
                dream_summary="You dreamed of a locked green room and a warm key.",
                main_question="What is the locked room asking me to notice?",
                dream_anchors=["locked green room", "warm key"],
                followup_questions=["What does the locked room feel closest to in waking life?"],
                user_answers=[],
                interpretation="Maybe the locked green room is a private threshold.",
                today_tip="For today, treat the locked green room as a small threshold and take one careful step.",
                tiny_action="Draw the warm key and move it one inch.",
                caring_note="One small threshold is enough.",
                safety_note="",
            )

    intake = build_intake(
        dream_text="I found a locked green room behind my kitchen. The key was warm but would not turn.",
        mood="uneasy",
        main_question="Why does it feel like I cannot ask for what I need?",
    )
    answer = "In real life it is probably the leave request I keep avoiding because I feel guilty."

    card = generate_today_tip(intake, answer, AnchorOnlyClient(), language="en")
    combined = "\n".join([card.main_question, card.interpretation, card.today_tip, card.tiny_action, card.caring_note]).lower()

    assert "locked green room" in combined or "warm key" in combined
    assert "leave request" in combined
    assert "guilty" in combined or "guilt" in combined
    assert "one careful step" not in card.today_tip.lower()


def test_today_tip_filters_absent_office_email_and_repairs_question_summary_and_numbered_tip():
    class PollutedOfficeEmailClient:
        def generate_today_tip(self, prompt):
            return TodayTipCard(
                dream_summary="I dreamed I was rushing to catch an elevator, but my phone was dead a",
                main_question="My question: does this mean I have been too anxious lately",
                dream_anchors=["office building", "elevator", "email"],
                followup_questions=["Which detail felt closest?"],
                user_answers=[],
                interpretation=(
                    "Maybe the office building is asking you to open one thread and draft one first sentence."
                ),
                today_tip=(
                    "1. Translate office building into a real-world communication question: what does the "
                    "overdue email need? 2. Open the draft and write the first sentence of the email. "
                    "3. Save it."
                ),
                tiny_action="Draw the office building and write only the first sentence of the email.",
                caring_note="The office building can wait.",
                safety_note="",
            )

    intake = build_intake(
        dream_text=(
            "I dreamed I was rushing to catch an elevator, but my phone was dead and I was late for something "
            "important. I kept pressing the elevator button and worrying I had already missed my chance. "
            "My question: does this mean I have been too anxious lately?"
        ),
        mood="Anxious",
    )
    answer = "The phone with no battery feels closest. I keep avoiding a work message, so I feel behind before I even start."

    card = generate_today_tip(intake, answer, PollutedOfficeEmailClient(), language="en")
    combined = _today_tip_public_text(card).lower()

    assert "office building" not in combined
    assert "overdue email" not in combined
    assert "first sentence of the email" not in combined
    assert "elevator" in combined or "phone" in combined
    assert "work message" in combined or "message" in combined
    assert "my question:" not in card.main_question.lower()
    assert card.main_question == "Does this mean I have been too anxious lately?"
    assert not card.dream_summary.rstrip(".").endswith("phone was dead a")
    assert not re.search(r"\b[123]\.", card.today_tip)


def test_today_tip_keeps_friend_misunderstanding_emotional_instead_of_email_draft_template():
    class PollutedFriendClient:
        def generate_today_tip(self, prompt):
            return TodayTipCard(
                dream_summary="I dreamed my close friend misunderstood me in front of everyone. I ke",
                main_question="My question: why did I wake up feeling so wronged and hurt",
                dream_anchors=["room"],
                followup_questions=["What felt closest?"],
                user_answers=[],
                interpretation=(
                    "Maybe the room is not asking you to answer every message at once; it points to opening "
                    "one thread and drafting one first sentence."
                ),
                today_tip=(
                    "1. Translate room into a real-world communication question: what does the overdue email "
                    "need? 2. Open the draft and write one sentence."
                ),
                tiny_action="Open the message thread and draft the first sentence of the email.",
                caring_note="One thread at a time.",
                safety_note="",
            )

    intake = build_intake(
        dream_text=(
            "I dreamed my close friend misunderstood me in front of everyone. I kept explaining, but nobody "
            "listened, and the room got louder every time I tried. My question: why did I wake up feeling so "
            "wronged and hurt?"
        ),
        mood="Hurt and confused",
    )
    answer = "It felt like I was invisible, not angry. Yesterday I worried that a friend read my message in the worst possible way."

    card = generate_today_tip(intake, answer, PollutedFriendClient(), language="en")
    combined = _today_tip_public_text(card).lower()

    assert "overdue email" not in combined
    assert "first sentence of the email" not in combined
    assert "draft the first sentence" not in combined
    assert "wronged" in combined or "hurt" in combined or "invisible" in combined or "not listened" in combined
    assert "friend" in combined or "message" in combined
    assert "my question:" not in card.main_question.lower()
    assert card.main_question == "Why did I wake up feeling so wronged and hurt?"
    assert not re.search(r"\b[123]\.", card.today_tip)


def test_friend_misunderstanding_skip_path_keeps_relationship_emotion_anchors():
    dream_text = (
        "I dreamed my close friend misunderstood me. I kept explaining, but nobody heard me, "
        "and I woke up feeling hurt and invisible."
    )
    session = add_evidence(
        create_session(),
        dream_text=dream_text,
        mood="Hurt and invisible",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
        language="en",
    )

    assert "close friend" in session.qa_state.dream_anchors
    assert "being misunderstood" in session.qa_state.dream_anchors
    assert "nobody heard me" in session.qa_state.dream_anchors
    assert "feeling invisible" in session.qa_state.dream_anchors
    assert "feeling hurt" in session.qa_state.dream_anchors

    session = ask_questions(session, FakeTextClient(), language="en")
    question_text = session.question_history[0].lower()

    assert "friend" in question_text
    assert "misunderstood" in question_text or "heard" in question_text or "hurt" in question_text
    assert "former partner" not in question_text
    assert "disappearance" not in question_text
    assert "dream clues" not in question_text

    session = skip_question(session, language="en")
    session = finish_today_tip(session, FakeTextClient(), language="en")
    card = session.sealed_tip
    combined = _today_tip_public_text(card).lower()

    assert "friend" in combined
    assert "misunderstood" in combined or "heard" in combined
    assert "invisible" in combined or "hurt" in combined
    assert "former partner" not in combined
    assert "disappearance" not in combined
    assert "dream clues" not in combined
    assert "stuck before starting" not in combined
    assert "overdue email" not in combined
    assert "first sentence of the email" not in combined
    assert not re.search(r"\b[123]\.", card.today_tip)


def test_today_tip_skip_path_uses_original_anchors_without_default_email_or_broken_caring_note():
    class PollutedSkipClient:
        def generate_today_tip(self, prompt):
            return TodayTipCard(
                dream_summary="I dreamed I was late, my phone battery died, and the elevator never a",
                main_question="What might the elevator mean?",
                dream_anchors=["office building", "elevator", "email"],
                followup_questions=["Which detail felt closest?"],
                user_answers=[],
                interpretation="Maybe the office building, elevator, and email point to a draft you need to open.",
                today_tip=(
                    "1. Use elevator, my phone, and phone. 2. Choose one waking-life doorway action today: "
                    "open the draft."
                ),
                tiny_action="Draw an elevator button and write only the first sentence of the email.",
                caring_note="dream fragment , dream fragment floor.",
                safety_note="",
            )

    intake = build_intake(
        dream_text=(
            "I dreamed I was late, my phone battery died, and the elevator never arrived. I want a quick tip, "
            "but I want to skip the follow-up."
        ),
        mood="Anxious",
    )

    card = generate_today_tip(intake, "", PollutedSkipClient(), language="en")
    combined = _today_tip_public_text(card).lower()

    assert "office building" not in combined
    assert "email" not in combined
    assert "open the draft" not in combined
    assert "first sentence" not in combined
    assert "dream fragment" not in combined
    assert "elevator" in combined
    assert "phone" in combined or "late" in combined
    assert not re.search(r"\b[123]\.", card.today_tip)


def test_today_tip_skip_path_repairs_generic_calming_and_tiny_action_inside_tip():
    class GenericCalmingClient:
        def generate_today_tip(self, prompt):
            return TodayTipCard(
                dream_summary="I dreamed I was late, my phone battery died, and the elevator never arrived.",
                main_question="What might the elevator be asking me to notice today?",
                dream_anchors=["elevator", "phone"],
                followup_questions=[],
                user_answers=[],
                interpretation="Maybe the elevator and phone point to the pressure of waiting.",
                today_tip=(
                    "Connect your phone's battery to your anxious morning. If the elevator voice persists, "
                    "listen to a short, calming song. For the tiny action, hold a cold glass of water for one minute "
                    "so you feel more grounded."
                ),
                tiny_action="Name one elevator button you can press today.",
                caring_note="One small detail is enough.",
                safety_note="",
            )

    intake = build_intake(
        dream_text="I dreamed I was late, my phone battery died, and the elevator never arrived.",
        mood="Anxious",
    )

    card = generate_today_tip(intake, "", GenericCalmingClient(), language="en")
    combined = _today_tip_public_text(card).lower()

    assert "elevator" in card.today_tip.lower() or "phone" in card.today_tip.lower()
    assert "calming song" not in combined
    assert "cold glass of water" not in combined
    assert "for the tiny action" not in card.today_tip.lower()
    assert not re.search(r"\b[123]\.", card.today_tip)


def test_today_tip_distress_repairs_polluted_surrounding_fields_while_keeping_safety_note():
    class PollutedDistressClient:
        def generate_today_tip(self, prompt):
            return TodayTipCard(
                dream_summary="I keep having the same frightening dream and I have barely slept for",
                main_question="What is wrong with me?",
                dream_anchors=["office building", "elevator", "email"],
                followup_questions=["What help would feel possible?"],
                user_answers=[],
                interpretation=(
                    "Second, the office building, elevator, and email may be the dream's concrete shape."
                ),
                today_tip=(
                    "1. Treat office building, elevator, and email as an unfinished contact. "
                    "2. Write one private unsent reply."
                ),
                tiny_action="Write one word from office building, elevator, and email.",
                caring_note="Start with the email contact.",
                safety_note="Seek support.",
            )

    intake = build_intake(
        dream_text=(
            "I keep having the same frightening dream and I have barely slept for many nights. I feel like I "
            "cannot function during the day and I am scared something is wrong with me."
        ),
        mood="Scared and exhausted",
    )
    answer = "I do not feel unsafe right now, but I cannot keep going like this without help."

    card = generate_today_tip(intake, answer, PollutedDistressClient(), language="en")
    combined = _today_tip_public_text(card).lower()

    assert card.safety_note
    assert "office building" not in combined
    assert "elevator" not in combined
    assert "email" not in combined
    assert "unsent reply" not in combined
    assert "dream clues" not in combined
    assert any(anchor in card.dream_anchors for anchor in ["frightening dream", "lost sleep"])
    assert "frightening" in combined or "sleep" in combined or "scared" in combined or "help" in combined
    assert "trusted" in card.safety_note.lower() or "professional" in card.safety_note.lower()
    assert not re.search(r"\b[123]\.", card.today_tip)


def test_generate_today_tip_adds_safety_note_for_repeated_insomnia_without_self_harm():
    intake = build_intake(
        dream_text="我昨晚反复梦见自己在一条漆黑的走廊里走，醒来后心跳很快，已经连续3晚都睡不好。",
        mood="焦虑",
    )

    card = generate_today_tip(intake, "我想知道今晚能不能睡好一点。", FakeTextClient(), language="zh")

    assert card.safety_note
    assert "可信任的人" in card.safety_note


def test_generate_today_tip_adds_chinese_safety_note_for_hopeless_text():
    intake = build_intake(dream_text="我梦到站在高楼边缘，醒来后不想醒来，很绝望。")

    card = generate_today_tip(intake, "", FakeTextClient(), language="zh")

    assert card.safety_note
    assert "可信任的人" in card.safety_note


def test_chinese_short_and_sensitive_fragments_keep_real_anchors():
    cases = [
        ("昨晚梦见掉进海里。", ["海", "掉进海里"]),
        ("昨晚梦到一个小孩找不到家。", ["小孩", "找不到家"]),
        ("我总是自责，梦里不断重演过去犯的错误。", ["自责", "错误", "重演"]),
        ("梦见有很多追逐场景，醒来心率很快。", ["追逐", "心率"]),
    ]

    for dream_text, expected_markers in cases:
        card = generate_today_tip(
            build_intake(dream_text=dream_text, mood="焦虑"),
            "用户选择跳过这个追问。",
            FakeTextClient(),
            language="zh",
        )
        combined = "\n".join(
            [
                card.dream_summary,
                ",".join(card.dream_anchors),
                card.interpretation,
                card.today_tip,
                card.tiny_action,
            ]
        )

        assert any(marker in combined for marker in expected_markers)
        assert "梦里的那个细节" not in combined
        assert "that dream detail" not in combined


def test_generate_pact_polishes_unclear_model_output_into_daily_tip():
    class UnclearTextClient:
        def generate_pact(self, prompt):
            return PactCard(
                visitor_name="Dreamer",
                permit_id="DC-001",
                contraband=["融化蜡", "数字14"],
                risk_level="中",
                alliance_reading="联盟成员",
                practical_suggestion="明天早起观察电梯运行情况，若未超速可尝试模拟操作以熟悉流程。",
                weird_task="把今天最小的任务写在纸上，给它盖一个看不见的放行章。",
                bedtime_release="06:30",
                safety_note="梦境内容无医疗价值，建议保持冷静观察。",
            )

    intake = build_intake(dream_text="我梦见电梯按钮融化，数字停在 14。", mood="焦虑")
    card, html = generate_pact(intake, "", UnclearTextClient())

    assert card.visitor_name
    assert "drink water" in card.practical_suggestion
    assert "电梯运行" not in card.practical_suggestion
    assert card.safety_note == ""
    assert "Life tip" in html


def test_generate_pact_repairs_generic_hosted_output_with_dream_details():
    class GenericHostedTextClient:
        def generate_pact(self, prompt):
            return PactCard(
                visitor_name="Elena",
                permit_id="DC-015",
                contraband=["unfiled worry", "one stamp asking to be noticed"],
                risk_level="medium",
                alliance_reading=(
                    "You can treat this as a small signal from last night's feelings, not a prophecy. "
                    "Today, protect a realistic pace."
                ),
                practical_suggestion=(
                    "Hydrate and eat a piece of fruit to support your morning routine, as dehydration "
                    "can affect cognitive function."
                ),
                weird_task=(
                    "Count the number of birds in the sky before bed, as it is a harmless and playful "
                    "activity that requires no special skills."
                ),
                bedtime_release="7:00 PM",
                safety_note="",
            )

    intake = build_intake(
        dream_text=(
            "I dreamed I was at a customs window carrying a suitcase full of wet paper. "
            "The clerk asked me to declare every unfinished promise before sunrise."
        ),
        mood="Uneasy",
    )

    card, html = generate_pact(intake, "", GenericHostedTextClient())
    joined = "\n".join(
        [
            card.visitor_name,
            card.alliance_reading,
            card.practical_suggestion,
            card.weird_task,
            card.bedtime_release,
        ]
    ).lower()

    assert "wet paper" in joined or "unfinished promise" in joined
    assert "customs window" in card.alliance_reading.lower() or "wet paper" in card.alliance_reading.lower()
    assert "promise" in card.practical_suggestion.lower() or "first step" in card.practical_suggestion.lower()
    assert any(anchor in card.weird_task.lower() for anchor in ["paper", "promise", "suitcase", "customs"])
    assert card.bedtime_release != "7:00 PM"
    assert "Hydrate and eat a piece of fruit" not in html


def test_pact_prompt_requires_dream_grounded_card():
    intake = build_intake(
        dream_text="I carried wet paper through a customs window before sunrise.",
        mood="Uneasy",
    )
    prompt = pact_prompt(intake, "I want to keep one promise small today.")

    assert "reuse at least two concrete dream details" in prompt
    assert "avoid generic wellness filler" in prompt
    assert "bedtime_release must be a sentence" in prompt
    assert "not a human name unless a person appears" in prompt


def test_today_tip_prompt_requires_waking_life_suggestions_and_weird_action():
    intake = build_intake(
        dream_text="我梦见办公楼里的电梯停在 14 层，一封邮件一直发不出去。",
        mood="焦急",
    )
    state = build_qa_state(
        intake,
        answers=["我觉得那封邮件是在提醒我有一件现实工作沟通还没开始。"],
        language="zh",
    )

    prompt = today_tip_prompt(state, language="zh")

    assert "waking-life" in prompt
    assert "single grounded tip" in prompt
    assert "weird little thing" in prompt
    assert "real-world physics" in prompt
    assert "古怪的小事" in prompt


def test_add_evidence_updates_session_with_text_image_audio_and_mood():
    session = add_evidence(
        create_session(),
        dream_text="I dreamed the elevator buttons melted.",
        image_path="demo.png",
        audio_path="demo.wav",
        mood="anxious",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
    )
    assert session.phase == "record"
    assert "elevator" in session.intake.dream_text
    assert any("blue hallway" in clue for clue in session.intake.visual_clues)
    assert "The buttons melted" in session.intake.voice_transcript
    assert session.intake.mood == "anxious"
    assert {item.type for item in session.evidence_items} == {"text", "image", "audio", "mood"}


def test_ask_answer_skip_draft_revise_and_seal_actions():
    session = add_evidence(
        create_session(),
        dream_text="I missed an elevator.",
        mood="restless",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
    )
    session = ask_questions(session, FakeTextClient())
    assert session.phase == "ask"
    assert len(session.question_history) == 1
    assert "three layers" in session.question_history[0]

    session = answer_question(session, "I want one small start.")
    assert session.answer_history[-1] == "I want one small start."

    session = ask_questions(session, FakeTextClient(), force_another=True)
    assert len(session.question_history) == 2
    assert "For this round" in session.question_history[-1]

    session = ask_questions(session, FakeTextClient(), force_another=True)
    assert len(session.question_history) == 3

    session = ask_questions(session, FakeTextClient(), force_another=True)
    assert len(session.question_history) == 3

    session = skip_question(session)
    assert "skip" in session.answer_history[-1].lower()

    zh_session = skip_question(session, language="zh")
    assert "跳过" in zh_session.answer_history[-1]

    session = draft_pact(session, FakeTextClient())
    assert session.phase == "drafting"
    assert session.draft_pact is not None

    original_task = session.draft_pact.weird_task
    session = revise_pact(session, "make it stranger", FakeTextClient())
    assert session.draft_pact is not None
    assert session.draft_pact.weird_task != original_task

    session = seal_pact(session)
    assert session.phase == "sealed"
    assert session.sealed_pact == session.draft_pact


def test_force_another_question_keeps_chinese_answer_snippet_readable():
    session = add_evidence(
        create_session(language="zh"),
        dream_text="我梦见自己卡在电梯口，14 层的灯一直亮着。",
        mood="焦急",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
        language="zh",
    )
    session = ask_questions(session, FakeTextClient(), language="zh")
    session = answer_question(
        session,
        "我觉得那封邮件像是我一直拖着的一次工作沟通，也可能有一点道歉。今天可以先写第一句，不一定马上发出去。",
        language="zh",
    )
    session = ask_questions(session, FakeTextClient(), force_another=True, language="zh")

    latest = session.question_history[-1]
    assert "今天可。" not in latest
    assert "第一句" in latest or "工作沟通" in latest
    assert "我把你的回答也放进来了" in latest


def test_draft_pact_falls_back_to_legacy_generate_pact_client():
    class LegacyPactOnlyClient:
        def generate_pact(self, prompt):
            return PactCard(
                visitor_name="Legacy Elevator",
                permit_id="DC-014",
                contraband=["melted buttons"],
                risk_level="medium: handle gently, without treating it as a warning sign",
                alliance_reading="The elevator can be treated as a request for one smaller move.",
                practical_suggestion="Write one next step before touching the bigger task.",
                weird_task="Draw a tiny elevator button and press it once.",
                bedtime_release="Tonight, the elevator can wait quietly outside the room.",
            )

    session = add_evidence(
        create_session(),
        dream_text="I missed an elevator and the buttons melted.",
        mood="Uneasy",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
    )

    session = draft_pact(session, LegacyPactOnlyClient())

    assert session.phase == "drafting"
    assert session.draft_pact is not None
    assert session.draft_pact.visitor_name == "Legacy Elevator"


def test_draft_pact_exposes_internal_model_led_attribute_errors():
    class BrokenModelLedClient:
        def generate_brief(self, prompt):
            raise AttributeError("internal model-led bug")

        def generate_pact_draft(self, prompt):
            raise AssertionError("generate_pact_draft should not run")

        def critique_pact(self, prompt):
            raise AssertionError("critique_pact should not run")

        def rewrite_pact(self, prompt):
            raise AssertionError("rewrite_pact should not run")

        def generate_pact(self, prompt):
            return PactCard(
                visitor_name="Hidden Legacy Fallback",
                permit_id="DC-999",
                contraband=["hidden bug"],
                risk_level="medium: handle gently, without treating it as a warning sign",
                alliance_reading="This should not be generated when model-led internals fail.",
                practical_suggestion="This fallback should stay unreachable.",
                weird_task="This fallback should stay unreachable.",
                bedtime_release="This fallback should stay unreachable.",
            )

    session = add_evidence(
        create_session(),
        dream_text="I missed an elevator and the buttons melted.",
        mood="Uneasy",
        vision_client=FakeVisionClient(),
        asr_client=FakeASRClient(),
    )

    with pytest.raises(AttributeError, match="internal model-led bug"):
        draft_pact(session, BrokenModelLedClient())


def test_image_audio_failures_keep_text_path_alive():
    class FailingVision:
        def extract_clues(self, image_path):
            raise RuntimeError("offline")

    class EmptyASR:
        def transcribe(self, audio_path):
            return ""

    session = add_evidence(
        create_session(),
        dream_text="Text still works.",
        image_path="missing.png",
        audio_path="missing.wav",
        mood="foggy",
        vision_client=FailingVision(),
        asr_client=EmptyASR(),
    )
    session = ask_questions(session, FakeTextClient())
    session = draft_pact(session, FakeTextClient())
    assert session.draft_pact is not None
    assert any(item.status == "failed" for item in session.evidence_items)
    assert "Text still works." in session.intake.dream_text


def test_add_evidence_prefers_vision_witness_report():
    class WitnessPreferredVision:
        def extract_witness(self, image_path):
            return VisionWitness(
                scene_summary="Witness scene",
                visible_text=["14"],
                surprising_detail="Witness detail",
            )

        def extract_clues(self, image_path):
            return ["flat clue should not win"]

    session = add_evidence(
        create_session(),
        dream_text="I saw an elevator.",
        image_path="demo.png",
        mood="Uneasy",
        vision_client=WitnessPreferredVision(),
        asr_client=FakeASRClient(),
    )

    assert "Scene: Witness scene" in session.intake.visual_clues
    assert "Visible text: 14" in session.intake.visual_clues
    assert "Surprising detail: Witness detail" in session.intake.visual_clues
    assert "flat clue should not win" not in session.intake.visual_clues


def test_visual_witness_clues_drive_questions_and_today_tip():
    class RedStairVision:
        def extract_witness(self, image_path):
            return VisionWitness(
                scene_summary="A red staircase inside an old library.",
                objects=["red staircase", "yellow sticky note"],
                visible_text=["CALL HOME"],
                surprising_detail="Rain is drawn outside the window.",
            )

        def extract_clues(self, image_path):
            return ["flat fallback should not win"]

    session = add_evidence(
        create_session(),
        dream_text="I only remember a dream fragment.",
        image_path="note.png",
        mood="Uneasy",
        vision_client=RedStairVision(),
        asr_client=FakeASRClient(),
        language="en",
    )
    session = ask_questions(session, FakeTextClient(), language="en")
    session = answer_question(session, "The sticky note felt urgent.", language="en")
    session = skip_question(session, language="en")
    text = "\n".join([session.question_history[0], ",".join(session.qa_state.dream_anchors)]).lower()

    assert "red staircase" in text or "old library" in text or "yellow sticky note" in text

    card = generate_today_tip(
        session.intake,
        session.answers_text(),
        FakeTextClient(),
        language="en",
        followup_questions=session.question_history,
    )
    combined = "\n".join([card.dream_summary, ",".join(card.dream_anchors), card.today_tip]).lower()

    assert "red staircase" in combined or "old library" in combined or "yellow sticky note" in combined
    assert "scene_summary" not in combined
    assert "objects" not in combined


def test_zh_text_and_image_keep_user_question_while_using_visual_anchors():
    class SeaDreamVision:
        def extract_witness(self, image_path):
            return VisionWitness(
                scene_summary=(
                    "A simple sketch of a person standing on wavy lines under a crescent moon, "
                    "with the text 'dark sea dream' above."
                ),
                objects=["stick figure", "wavy lines representing water", "crescent moon"],
                visible_text=["dark sea dream"],
                mood_cues=["small figure in a large dark place"],
            )

        def extract_clues(self, image_path):
            return ["flat fallback should not win"]

    session = add_evidence(
        create_session(language="zh"),
        dream_text="我醒来很害怕，这张草图是梦里最清楚的画面。我想知道为什么它让我这么慌。",
        image_path="sea.png",
        mood="害怕",
        vision_client=SeaDreamVision(),
        asr_client=FakeASRClient(),
        language="zh",
    )
    card = generate_today_tip(session.intake, "", FakeTextClient(), language="zh")
    combined = "\n".join([card.main_question, ",".join(card.dream_anchors), card.interpretation, card.today_tip])

    assert "为什么它让我这么慌？" in card.main_question
    assert any(anchor in card.dream_anchors for anchor in ["夜晚的海", "海浪", "月牙", "漆黑的海"])
    assert "blue hallway" not in combined
    assert "a simple sketch" not in combined.lower()
    assert "dreamlike representation" not in combined.lower()
    assert "这么难受不是你反应过度" in card.interpretation


def test_zh_first_response_and_tip_follow_story_and_image_not_template():
    class LostChildVision:
        def extract_witness(self, image_path):
            return VisionWitness(
                scene_summary="A child figure stands inside a subway station with arrows pointing toward HOME.",
                objects=["child figure", "subway station", "arrows"],
                visible_text=["HOME"],
                mood_cues=["lost", "small figure in a large station"],
            )

        def extract_clues(self, image_path):
            return ["flat fallback should not win"]

    session = add_evidence(
        create_session(language="zh"),
        dream_text="我梦见一个小孩在地铁站找不到家，我醒来很害怕，想知道为什么这个画面让我这么难受。",
        image_path="lost-child.png",
        mood="害怕",
        vision_client=LostChildVision(),
        asr_client=FakeASRClient(),
        language="zh",
    )
    session = ask_questions(session, FakeTextClient(), language="zh")
    first_response = session.question_history[0]

    assert "我先听到的是" in first_response
    assert "三层" in first_response
    assert "小孩" in first_response
    assert "回家" in first_response or "地铁" in first_response

    session = answer_question(session, "更像我自己最近不知道该往哪里走，也很想有人带一下。", language="zh")
    card = generate_today_tip(
        session.intake,
        session.answers_text(),
        FakeTextClient(),
        language="zh",
        followup_questions=session.question_history,
    )
    combined = "\n".join([card.interpretation, card.today_tip, card.tiny_action, card.caring_note])

    assert "小孩" in combined
    assert "回家" in combined or "地铁" in combined or "路标" in combined
    assert "需要被带路" in card.today_tip or "路标" in card.today_tip
    assert "写两行" not in combined
    assert "当作害怕的形状" not in combined


def test_witness_failure_keeps_text_path_alive():
    class BrokenWitnessVision:
        def extract_witness(self, image_path):
            raise RuntimeError("vision offline")

        def extract_clues(self, image_path):
            return ["fallback clue"]

    intake = intake_from_modalities(
        dream_text="Text still works.",
        image_path="demo.png",
        audio_path=None,
        mood="Foggy",
        vision_client=BrokenWitnessVision(),
        asr_client=FakeASRClient(),
    )

    assert "Text still works." in intake.merged_text()
    assert "fallback clue" in intake.merged_text()
