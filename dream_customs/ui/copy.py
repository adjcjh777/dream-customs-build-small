DEFAULT_LANGUAGE = "en"

LANGUAGE_OPTIONS = [
    ("English", "en"),
    ("中文", "zh"),
]

APP_COPY = {
    "en": {
        "title": "Dream QA",
        "hero_kicker": "Dream QA / The Morning Question Desk",
        "hero_title": "What did the dream leave you asking?",
        "subtitle": "Record the dream, answer one gentle question, and leave with a grounded Morning Ticket.",
        "hero_body": "A small-model dream desk for the first few minutes after waking. It gathers concrete details, asks before interpreting, and writes one note for today.",
        "hero_badge": "Text + image + voice intake",
        "hero_mobile_note": "Made for the half-awake minute",
        "brand_subtitle": "Dream Customs",
        "steps": ["Record", "One Question", "Today Tip"],
        "notice_record": "Write one dream fragment, then use a demo chip if you want the 90-second judge path.",
        "notice_ask": "Answer this one question, or skip it and turn the existing clues into a Morning Ticket.",
        "notice_tip": "Your Morning Ticket is ready. Treat it as gentle reflection, not diagnosis or prophecy.",
        "notice_error": "Dream QA needs a dream fragment before it can continue.",
        "dream_label": "Dream note",
        "dream_placeholder": "Write the dream while it is still foggy...\nExample: I kept missing an elevator. The button for floor 14 melted like wax.",
        "mic_idle": "Tap the microphone to dictate",
        "mic_unsupported": "This browser cannot transcribe voice here. You can still type the dream.",
        "mic_permission": "Microphone permission was not granted. Allow recording and try again.",
        "mic_listening": "Listening. Say the dream fragment when you are ready.",
        "mic_done": "Added to the dream note.",
        "mic_empty": "No speech detected. Tap again if you want to retry.",
        "voice_label": "Voice note",
        "voice_help": "Record or upload a short voice note. It is transcribed by the ASR adapter when you continue.",
        "field_tip": "The desk looks for three anchors: a place, an object, and the question the dream left behind.",
        "example_button": "elevator",
        "example_button_2": "floor 14",
        "example_button_3": "melting buttons",
        "submit_button": "Ask one question",
        "processing_note": (
            "After submission, the desk extracts dream anchors, asks one grounded question, then writes a Morning Ticket with one Today Tip."
        ),
        "image_accordion": "＋",
        "image_label": "Image clue",
        "image_upload": "Upload image",
        "image_paste": "Paste from Clipboard",
        "demo_intro_label": "Dream slips",
        "demo_intro_body": "Pick one if you want the fast judge path.",
        "question_kicker": "Question",
        "question_title": "One question before the ticket",
        "question_body": "Answer in one or two lines, or skip and let the existing anchors carry the ticket.",
        "question_speaker": "Morning Question Desk",
        "question_note": "This step makes the tip more specific. It is not diagnosis.",
        "question_anchor_label": "Sticky details already on the desk",
        "answer_label": "Your answer",
        "answer_placeholder": "Write one answer, or leave it blank and skip.",
        "answer_button": "Send answer",
        "skip_button": "Skip and generate tip",
        "ask_again_button": "Ask one more question",
        "angle_button": "Ask from another angle",
        "copy_button": "Copy result",
        "reset_button": "Start over",
        "copy_label": "Copyable result",
        "side_title": "Waking mood",
        "mood_label": "Mood",
        "side_stamp_label": "90-second demo",
        "side_stamp_title": "Elevator, floor 14, first sentence",
        "side_stamp_body": "The strongest path ends with a tiny action tied to a real overdue email.",
        "desk_rule_label": "Morning desk rule",
        "desk_rule_title": "Do not solve the whole dream.",
        "desk_rule_body": "Catch the strange object, name the feeling, ask one useful question.",
        "intake_label": "One intake",
        "intake_items": ["Text", "Image", "Voice"],
        "language_label": "Language",
        "runtime_help": "Advanced controls for demos and development. Most visitors can leave these unchanged.",
        "debug_title": "Debug",
        "debug_help": "Inspect the current session, backend route, latency budgets, and Space/Modal status without exposing secrets.",
        "debug_state_label": "Runtime state",
        "card_title": "Today Tip",
        "error_state": "The interface state could not be read. Please start over.",
    },
    "zh": {
        "title": "梦境问答台",
        "hero_kicker": "梦境问答台 / 清晨问讯室",
        "hero_title": "这个梦，醒来后把什么问题留给了你？",
        "subtitle": "记录梦境，回答一个温和追问，最后拿到一张贴着梦境细节的清晨小票。",
        "hero_body": "一个适合刚醒来几分钟使用的小模型问讯台：先捡起具体细节，再问一个好问题，最后只给今天的一张小纸条。",
        "hero_badge": "文字 + 图片 + 语音统一入口",
        "hero_mobile_note": "适合半醒时的一分钟",
        "brand_subtitle": "Dream Customs",
        "steps": ["记录", "一个追问", "清晨小票"],
        "notice_record": "写一个梦境片段；想走 90 秒演示路径，也可以直接点示例 chip。",
        "notice_ask": "回答这一个追问，或跳过，用已有梦境线索生成清晨小票。",
        "notice_tip": "清晨小票已生成。把它当作温和参考，不是诊断或预言。",
        "notice_error": "梦境问答台还没有收到片段。",
        "dream_label": "梦境记录",
        "dream_placeholder": "趁梦还带着雾气，先写下来...\n例如：我一直赶不上电梯，14 楼按钮像蜡一样融化。",
        "mic_idle": "点击麦克风录音",
        "mic_unsupported": "这个浏览器暂时不能直接转写语音，你仍然可以手动输入梦境。",
        "mic_permission": "没有获得麦克风权限。允许浏览器录音后可以再试一次。",
        "mic_listening": "正在听。准备好后说出梦境片段。",
        "mic_done": "已加入梦境记录。",
        "mic_empty": "没有检测到语音。想重试的话，再点一次麦克风。",
        "voice_label": "语音片段",
        "voice_help": "可以录音或上传一小段语音。点击继续后，ASR 适配器会先转写它。",
        "field_tip": "问讯室会优先寻找三个锚点：地点、物件、以及梦醒后留下的问题。",
        "example_button": "电梯",
        "example_button_2": "14 楼",
        "example_button_3": "融化按钮",
        "submit_button": "问一个问题",
        "processing_note": (
            "提交后，问讯室会提取梦境锚点，问一个关键问题，再写成一张清晨小票。"
        ),
        "image_accordion": "＋",
        "image_label": "图片线索",
        "image_upload": "上传图片",
        "image_paste": "从剪贴板粘贴",
        "demo_intro_label": "梦境纸片",
        "demo_intro_body": "想快速演示，可以先抽一张。",
        "question_kicker": "追问",
        "question_title": "出票前，只问这一个问题",
        "question_body": "回答一两句就好；也可以跳过，让已有锚点直接生成小票。",
        "question_speaker": "清晨问讯室",
        "question_note": "这个步骤是为了让最终建议更贴近你的梦，不是问诊。",
        "question_anchor_label": "桌面上已经留下的细节",
        "answer_label": "你的回答",
        "answer_placeholder": "写一句回答，或留空后选择跳过。",
        "answer_button": "发送回答",
        "skip_button": "跳过，生成 Tips",
        "ask_again_button": "再追问一下",
        "angle_button": "换个追问角度",
        "copy_button": "复制结果",
        "reset_button": "重新开始",
        "copy_label": "可复制结果",
        "side_title": "醒来后的心情",
        "mood_label": "心情",
        "side_stamp_label": "90 秒演示",
        "side_stamp_title": "电梯、14 楼、第一句话",
        "side_stamp_body": "最稳的演示路径会把梦境锚点落到一封迟迟没写的邮件。",
        "desk_rule_label": "清晨桌面规则",
        "desk_rule_title": "不要解完整个梦。",
        "desk_rule_body": "先抓住奇怪的物件，说出醒来的感受，再问一个今天能用的问题。",
        "intake_label": "同一个入口",
        "intake_items": ["文字", "图片", "语音"],
        "language_label": "语言",
        "runtime_help": "高级演示与开发控制。普通体验保持默认即可。",
        "debug_title": "调试",
        "debug_help": "查看当前会话、后端路由、延迟预算和 Space/Modal 状态；不会暴露密钥。",
        "debug_state_label": "运行状态",
        "card_title": "今日小 Tips",
        "error_state": "界面状态读取失败，请重新开始。",
    },
}

EXAMPLE_DREAMS = {
    "en": "I dreamed I kept missing an elevator. The button for floor 14 melted like wax. I woke up anxious because it reminded me of an overdue email.",
    "zh": "我梦到自己一直赶不上电梯，14 楼按钮像蜡一样融化。醒来有点焦虑，因为它让我想到一封迟迟没写的邮件。",
}

EXAMPLE_MOODS = {"en": "Uneasy", "zh": "焦虑"}

EXAMPLE_CHIPS = {
    "en": {
        "elevator": (
            "I dreamed I kept missing an elevator. The doors opened, closed, and left me behind.",
            "Uneasy",
        ),
        "floor14": (
            "I dreamed I kept missing an elevator, and the floor number stayed on 14.",
            "Uneasy",
        ),
        "melting": (
            "I dreamed I kept missing an elevator. The button for floor 14 melted like wax. I woke up anxious because it reminded me of an overdue email.",
            "Uneasy",
        ),
    },
    "zh": {
        "elevator": (
            "我梦到自己一直赶不上电梯，门开了又关，好像总是把我留在外面。",
            "焦虑",
        ),
        "floor14": (
            "我梦到自己一直赶不上电梯，楼层数字一直停在 14。",
            "焦虑",
        ),
        "melting": (
            "我梦到自己一直赶不上电梯，14 楼按钮像蜡一样融化。醒来有点焦虑，因为它让我想到一封迟迟没写的邮件。",
            "焦虑",
        ),
    },
}

MOOD_OPTIONS_BY_LANGUAGE = {
    "en": ["Neutral", "Uneasy", "Foggy", "Curious", "Tired", "A little amused"],
    "zh": ["一般", "焦虑", "迷糊", "好奇", "疲惫", "有点好笑"],
}


def normalize_language(language: str = DEFAULT_LANGUAGE) -> str:
    return language if language in APP_COPY else DEFAULT_LANGUAGE


def copy_for(language: str = DEFAULT_LANGUAGE) -> dict:
    return APP_COPY[normalize_language(language)]


def mood_options_for(language: str = DEFAULT_LANGUAGE) -> list[str]:
    return MOOD_OPTIONS_BY_LANGUAGE[normalize_language(language)]


def default_mood_for(language: str = DEFAULT_LANGUAGE) -> str:
    return mood_options_for(language)[0]


APP_TITLE = APP_COPY[DEFAULT_LANGUAGE]["title"]
APP_SUBTITLE = APP_COPY[DEFAULT_LANGUAGE]["subtitle"]
PROCESSING_NOTE = APP_COPY[DEFAULT_LANGUAGE]["processing_note"]
DREAM_PLACEHOLDER = APP_COPY[DEFAULT_LANGUAGE]["dream_placeholder"]
ANSWER_PLACEHOLDER = APP_COPY[DEFAULT_LANGUAGE]["answer_placeholder"]
EXAMPLE_DREAM = EXAMPLE_DREAMS[DEFAULT_LANGUAGE]
EXAMPLE_MOOD = EXAMPLE_MOODS[DEFAULT_LANGUAGE]
DEFAULT_MOOD = default_mood_for(DEFAULT_LANGUAGE)
DEFAULT_MOOD_OPTIONS = mood_options_for(DEFAULT_LANGUAGE)
MOOD_OPTIONS = DEFAULT_MOOD_OPTIONS
