DEFAULT_LANGUAGE = "en"

LANGUAGE_OPTIONS = [
    ("English", "en"),
    ("中文", "zh"),
]

APP_COPY = {
    "en": {
        "title": "Dream QA",
        "subtitle": "Record a dream, answer or skip one gentle question, and leave with one grounded Today Tip.",
        "brand_subtitle": "Dream Customs",
        "steps": ["Record", "Question", "Interpret", "Today Tip"],
        "notice_record": "Write a sentence, a few lines, or add image/voice clues. Text-only always works.",
        "notice_ask": "Answer this question, or skip it and generate a Today Tip from the clues already here.",
        "notice_tip": "Your Today Tip is ready. Treat it as gentle reflection, not diagnosis or prophecy.",
        "notice_error": "Dream QA needs a dream fragment before it can continue.",
        "dream_label": "Dream note",
        "dream_placeholder": "Write your dream here...\nSpecific details help, but a fragment is enough.",
        "mic_idle": "Tap the microphone to dictate",
        "mic_unsupported": "This browser cannot transcribe voice here. You can still type the dream.",
        "mic_permission": "Microphone permission was not granted. Allow recording and try again.",
        "mic_listening": "Listening. Say the dream fragment when you are ready.",
        "mic_done": "Added to the dream note.",
        "mic_empty": "No speech detected. Tap again if you want to retry.",
        "voice_label": "Voice note",
        "voice_help": "Record or upload a short voice note. It is transcribed by the ASR adapter when you continue.",
        "field_tip": "People, places, feelings, colors, or the question you woke up with are all useful.",
        "example_button": "Try example",
        "submit_button": "Continue",
        "processing_note": (
            "After submission, Dream QA asks one grounded question, then turns the dream into a small Today Tip."
        ),
        "image_accordion": "＋",
        "image_label": "Image clue",
        "image_upload": "Upload image",
        "image_paste": "Paste from Clipboard",
        "question_kicker": "Question",
        "question_title": "What do you most want to understand in this dream?",
        "question_body": "Answer in one or two lines, or skip and get a Today Tip from the clues already here.",
        "question_speaker": "Dream QA",
        "question_note": "This step makes the tip more specific. It is not diagnosis.",
        "answer_label": "Your answer",
        "answer_placeholder": "Write one answer, or leave it blank and skip.",
        "answer_button": "Send answer",
        "skip_button": "Skip and generate tip",
        "ask_again_button": "Ask another question",
        "angle_button": "Try another angle",
        "copy_button": "Copy result",
        "reset_button": "Start over",
        "copy_label": "Copyable result",
        "side_title": "Waking mood",
        "mood_label": "Mood",
        "side_stamp_label": "Tip",
        "side_stamp_title": "Add one concrete detail",
        "side_stamp_body": "It helps the final suggestion stay grounded in your dream.",
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
        "subtitle": "一步步整理梦境疑惑，回答或跳过温和追问，最后得到一个引用梦境细节的今日小 Tips。",
        "brand_subtitle": "Dream Customs",
        "steps": ["记录", "追问", "解读", "今日 Tip"],
        "notice_record": "写一句、几行，或上传图片/语音。Text-only 路径始终可用。",
        "notice_ask": "可以回答这个追问，也可以跳过，直接生成今日小 Tips。",
        "notice_tip": "今日小 Tips 已生成。把它当作温和参考，不是诊断或预言。",
        "notice_error": "梦境问答台还没有收到片段。",
        "dream_label": "梦境记录",
        "dream_placeholder": "继续写下你的梦...\n越具体，越有助于理解（可选）",
        "mic_idle": "点击麦克风录音",
        "mic_unsupported": "这个浏览器暂时不能直接转写语音，你仍然可以手动输入梦境。",
        "mic_permission": "没有获得麦克风权限。允许浏览器录音后可以再试一次。",
        "mic_listening": "正在听。准备好后说出梦境片段。",
        "mic_done": "已加入梦境记录。",
        "mic_empty": "没有检测到语音。想重试的话，再点一次麦克风。",
        "voice_label": "语音片段",
        "voice_help": "可以录音或上传一小段语音。点击继续后，ASR 适配器会先转写它。",
        "field_tip": "可以补充人物、地点、情绪、颜色，或醒来后最在意的疑问。",
        "example_button": "试试示例",
        "submit_button": "继续解梦  →",
        "processing_note": (
            "提交后，梦境助手会先追问一个关键细节，再把梦境整理成一个今日小 Tips。"
        ),
        "image_accordion": "＋",
        "image_label": "图片线索",
        "image_upload": "上传图片",
        "image_paste": "从剪贴板粘贴",
        "question_kicker": "追问",
        "question_title": "在这个梦里，你最想理解的是什么呢？",
        "question_body": "回答一两句就好；也可以跳过，直接得到一个基于现有线索的今日小 Tips。",
        "question_speaker": "梦境助手",
        "question_note": "这个步骤是为了让最终建议更贴近你的梦，不是问诊。",
        "answer_label": "你的回答",
        "answer_placeholder": "写一句回答，或留空后选择跳过。",
        "answer_button": "发送回答",
        "skip_button": "跳过，生成 Tips",
        "ask_again_button": "再问一个问题",
        "angle_button": "换个角度",
        "copy_button": "复制结果",
        "reset_button": "重新开始",
        "copy_label": "可复制结果",
        "side_title": "醒来后的心情",
        "mood_label": "心情",
        "side_stamp_label": "小贴士",
        "side_stamp_title": "尽量回忆更多细节",
        "side_stamp_body": "有助于更准确地理解梦境。",
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
    "en": "I dreamed I was in an old apartment building. The elevator button melted like wax, and the floor number stayed on 14. I woke up anxious.",
    "zh": "我梦到在一栋老楼里，电梯按钮融化了，按下去黏黏的。醒来有点焦虑。",
}

EXAMPLE_MOODS = {"en": "Uneasy", "zh": "焦虑"}

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
