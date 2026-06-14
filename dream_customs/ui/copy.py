DEFAULT_LANGUAGE = "en"

LANGUAGE_OPTIONS = [
    ("English", "en"),
    ("中文", "zh"),
]

APP_COPY = {
    "en": {
        "title": "Dream QA",
        "hero_kicker": "Dream QA / The Morning Question Desk",
        "hero_title": "What did the dream ask?",
        "subtitle": "One fragment. One gentle question. One Morning Ticket.",
        "hero_body": "",
        "hero_badge": "Text · image · voice",
        "hero_mobile_note": "Half-awake friendly",
        "brand_subtitle": "Dream Customs",
        "steps": ["Record", "Clarify", "Answer", "Tip"],
        "notice_record": "Write one dream fragment, or choose a sample dream slip if you want the 90-second judge path.",
        "notice_ask": "Answer this one question, or skip it and turn the existing clues into a Morning Ticket.",
        "notice_tip": "Your Morning Ticket is ready. Treat it as gentle reflection, not diagnosis or prophecy.",
        "notice_error": "Dream QA needs a dream fragment before it can continue.",
        "dream_label": "Dream note",
        "dream_placeholder": "Write the dream while it is still foggy...\nExample: I kept missing an elevator. The button for floor 14 melted like wax.",
        "mic_idle": "Add a voice note",
        "mic_unsupported": "This browser cannot transcribe voice here. You can still type the dream.",
        "mic_permission": "Microphone permission was not granted. Allow recording and try again.",
        "mic_listening": "Recording. Tap again to stop, or pause and MiMo ASR will transcribe.",
        "mic_transcribing": "Transcribing with MiMo ASR...",
        "mic_waking": "MiMo ASR is waking on Modal. This first pass can take a moment.",
        "mic_done": "Added the ASR transcript to the dream note.",
        "mic_empty": "No speech detected. Tap again if you want to retry.",
        "mic_error": "Voice transcription failed. You can type this fragment instead.",
        "mic_timeout": "MiMo ASR timed out. Tap the mic to try once more.",
        "voice_label": "Voice note",
        "voice_help": "Record or upload a short voice note. It is sent to MiMo ASR when you continue.",
        "field_tip": "The desk looks for three anchors: a place, an object, and the question the dream left behind.",
        "example_select_label": "Sample dream",
        "example_select_placeholder": "Choose a dream slip...",
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
        "question_kicker": "Step 3 of 4 · Answer or skip",
        "question_title": "One useful question",
        "question_body": "Answer in one or two lines, or skip and let the existing anchors carry the ticket.",
        "question_speaker": "Morning Question Desk",
        "question_note": "This step makes the tip more specific. It is not diagnosis.",
        "question_anchor_label": "Sticky details already on the desk",
        "question_context_label": "Why this question",
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
        "side_stamp_label": "Quick demo path",
        "side_stamp_title": "Pick a slip, answer or skip",
        "side_stamp_body": "The strongest path shows one grounded question and one Today Tip.",
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
        "hero_title": "这个梦在问什么？",
        "subtitle": "一个片段，一个追问，一张清晨小票。",
        "hero_body": "",
        "hero_badge": "文字 · 图片 · 语音",
        "hero_mobile_note": "适合半醒时使用",
        "brand_subtitle": "Dream Customs",
        "steps": ["记录", "明确问题", "回答追问", "Tips"],
        "notice_record": "写一个梦境片段；想走 90 秒演示路径，也可以从示例梦境里选一条。",
        "notice_ask": "回答这一个追问，或跳过，用已有梦境线索生成清晨小票。",
        "notice_tip": "清晨小票已生成。把它当作温和参考，不是诊断或预言。",
        "notice_error": "梦境问答台还没有收到片段。",
        "dream_label": "梦境记录",
        "dream_placeholder": "趁梦还带着雾气，先写下来...\n例如：我一直赶不上电梯，14 楼按钮像蜡一样融化。",
        "mic_idle": "添加语音片段",
        "mic_unsupported": "这个浏览器暂时不能直接转写语音，你仍然可以手动输入梦境。",
        "mic_permission": "没有获得麦克风权限。允许浏览器录音后可以再试一次。",
        "mic_listening": "正在录音。再次点击可停止，停顿后会交给 MiMo ASR 转写。",
        "mic_transcribing": "正在用 MiMo ASR 转写...",
        "mic_waking": "Modal 上的 MiMo ASR 正在唤醒，首次转写可能需要等一下。",
        "mic_done": "已把 ASR 转写加入梦境记录。",
        "mic_empty": "没有检测到语音。想重试的话，再点一次麦克风。",
        "mic_error": "语音转写失败。你也可以先手动输入这一段。",
        "mic_timeout": "MiMo ASR 转写超时了。可以再点一次麦克风重试。",
        "voice_label": "语音片段",
        "voice_help": "可以录音或上传一小段语音。点击继续后，会直接发送给 MiMo ASR 转写。",
        "field_tip": "问讯室会优先寻找三个锚点：地点、物件、以及梦醒后留下的问题。",
        "example_select_label": "示例梦境",
        "example_select_placeholder": "选择一张梦境纸片...",
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
        "question_kicker": "第 3 / 4 步 · 回答或跳过",
        "question_title": "一个有用的追问",
        "question_body": "回答一两句就好；也可以跳过，让已有锚点直接生成小票。",
        "question_speaker": "清晨问讯室",
        "question_note": "这个步骤是为了让最终建议更贴近你的梦，不是问诊。",
        "question_anchor_label": "桌面上已经留下的细节",
        "question_context_label": "为什么问这个",
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
        "side_stamp_label": "快速演示路径",
        "side_stamp_title": "选一张纸片，回答或跳过",
        "side_stamp_body": "最稳的演示会展示一个贴着细节的追问和一个今日小 Tips。",
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
    "en": "I dreamed I was late, my phone battery died, and the elevator never arrived. I wanted a quick tip and felt stuck at the entrance.",
    "zh": "我梦到自己快迟到了，手机没电，电梯一直没来。我想要一个很快能用的小建议，但梦里像被卡在入口。",
}

EXAMPLE_MOODS = {"en": "Uneasy", "zh": "焦虑"}

EXAMPLE_SLIPS = {
    "en": {
        "late_elevator": (
            "Late elevator and dead phone",
            "I dreamed I was late, my phone battery died, and the elevator never arrived. I wanted a quick tip and felt stuck at the entrance.",
            "Uneasy",
        ),
        "friend_misread": (
            "A friend misunderstood me",
            "I dreamed I sent a message to a friend, but every reply bubble turned into fog. I woke up worried I had been misunderstood.",
            "Uneasy",
        ),
        "sleepless_loop": (
            "The same sleepless room",
            "I dreamed I kept waking up inside the same room, checking the clock each time, but morning never arrived.",
            "Tired",
        ),
    },
    "zh": {
        "late_elevator": (
            "迟到的电梯和没电手机",
            "我梦到自己快迟到了，手机没电，电梯一直没来。我想要一个很快能用的小建议，但梦里像被卡在入口。",
            "焦虑",
        ),
        "friend_misread": (
            "朋友误解了我",
            "我梦到自己给朋友发消息，但每个回复气泡都变成雾。醒来后担心自己是不是被误解了。",
            "焦虑",
        ),
        "sleepless_loop": (
            "反复醒来的房间",
            "我梦到自己一次次在同一个房间醒来，每次都看钟，可早晨一直没有到。",
            "疲惫",
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
