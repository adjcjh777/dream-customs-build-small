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
        "topbar_title": "Dream QA",
        "topbar_greeting": "",
        "topbar_subtitle": "",
        "welcome_title": "What did you dream last night?",
        "welcome_message": "Start with whatever you remember — a feeling, a face, a scene. Details help, but a fragment is enough.",
        "steps": ["Record", "Ask", "Interpret", "Tip"],
        "step_subtitles": ["Write your dream", "Answer or skip", "Read draft", "Get grounded tip"],
        "notice_record": "Write a sentence, a few lines, or add an image. Text-only path is always available.",
        "notice_ask": "Answer this question, or skip it and get a Today Tip from the clues already here.",
        "notice_tip": "Your Today Tip is ready. Treat it as gentle reflection, not diagnosis or prophecy.",
        "notice_error": "Dream QA needs a dream fragment before it can continue.",
        "dream_label": "Dream note",
        "dream_placeholder": "I dreamed that...",
        "field_tip": "People, places, feelings, colors, or the question you woke up with are all useful.",
        "example_button": "Try example",
        "submit_button": "Continue",
        "processing_note": (
            "After submission, Dream QA asks one grounded question, then turns the dream into a small Today Tip."
        ),
        "image_accordion": "Add image",
        "image_label": "Upload a sketch, note, or screenshot",
        "question_kicker": "Question",
        "question_title": "What part of this dream stayed with you?",
        "question_body": "A few words are fine. Or skip — I'll work with what you've given me.",
        "question_speaker": "Dream QA",
        "question_note": "This step makes the tip more specific. It is not diagnosis.",
        "answer_label": "Your answer",
        "answer_placeholder": "Write one answer, or leave it blank and skip.",
        "answer_button": "Send answer",
        "skip_button": "Skip for now",
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
        "card_title": "Your Today Tip",
        "error_state": "The interface state could not be read. Please start over.",
        "qa_flow_title": "Dream QA Flow",
        "qa_flow_status": "In progress",
        "qa_flow_tip_status": "Tip ready",
        "qa_flow_error_status": "Error",
        "qa_flow_input_placeholder": "Continue describing your dream details...",
        "qa_flow_send": "Send",
        "qa_flow_chip_emotion": "I felt anxious",
        "qa_flow_chip_scene": "There was a building",
        "qa_flow_chip_character": "Someone was there",
        "qa_flow_chip_object": "I saw an object",
        "draft_title": "Interpretation",
        "draft_clues_title": "Dream clues",
        "draft_clues": ["Bridge", "Rushing water", "Walking alone", "Overcast sky"],
        "clues_empty": "Clues will appear after you describe your dream",
        "clues_hint": "These clues are based on your input",
        "draft_interpretation_title": "Interpretation",
        "draft_expand_button": "Read full interpretation",
        "today_tip_title": "Your Today Tip",
        "today_tip_text": "Give yourself some time and space. Allow emotions to be seen, and allow yourself to move forward slowly.",
        "today_tip_save": "Save",
        "sidebar_tip_label": "Tip",
        "sidebar_tip_text": "Your dream details help me ask better questions.",
        "notification_button": "Notifications",
        "notification_title": "Notifications",
        "notification_empty": "No new notifications.",
        "notification_tip_ready": "Your Today Tip is ready.",
        "notification_error": "Something went wrong. Try again.",
        "history_button": "History",
        "history_title": "Session History",
        "history_empty": "No dreams recorded this session.",
        "history_dream_label": "Dream",
        "menu_button": "Menu",
        "menu_language": "Language",
        "menu_restart": "Start over",
        "menu_restart_desc": "Clear all data and start a new session",
        "menu_mode_label": "Current mode",
        "menu_mode_text": "Text-only mode",
        "interpretation_content_title": "Full interpretation",
        "interpretation_empty": "Interpretation will appear here after you submit a dream.",
        "tip_saved": "Saved",
        "tip_save": "Save",
        "chip_emotion_prefix": "Emotion: ",
        "chip_scene_prefix": "Scene: ",
        "chip_character_prefix": "Character: ",
        "chip_object_prefix": "Object: ",
    },
    "zh": {
        "title": "梦境问答",
        "subtitle": "一步步整理梦境疑惑，回答或跳过温和追问，最后得到一个引用梦境细节的今日小 Tips。",
        "brand_subtitle": "Dream Customs",
        "topbar_title": "梦境问答",
        "topbar_greeting": "",
        "topbar_subtitle": "",
        "welcome_title": "昨晚梦到了什么？",
        "welcome_message": "想到什么就写什么——一种感觉、一个画面、一句话都行。细节有用，但片段也够了。",
        "steps": ["记录", "追问", "解读", "Tip"],
        "step_subtitles": ["说说你昨晚的梦", "再聊聊梦里的小细节？", "我帮你拆解梦的含义", "给你一点小启发"],
        "notice_record": "写几句，或上传图片都行。",
        "notice_ask": "可以回答这个追问，也可以跳过，直接生成今日小 Tips。",
        "notice_tip": "今日小 Tips 已生成。把它当作温和参考，不是诊断或预言。",
        "notice_error": "梦境问答还没有收到片段。",
        "dream_label": "记录梦境",
        "dream_placeholder": "我梦到...",
        "field_tip": "醒了最记得什么就写什么。",
        "example_button": "试试示例",
        "submit_button": "发送",
        "processing_note": (
            "提交后，梦境助手会先追问一个关键细节，再把梦境整理成一个今日小 Tips。"
        ),
        "image_accordion": "添加图片",
        "image_label": "上传草图、便签或截图",
        "question_kicker": "追问",
        "question_title": "梦里哪个部分让你印象最深？",
        "question_body": "说几个字就好。也可以跳过——我已经记住了你说的。",
        "question_speaker": "梦境助手",
        "question_note": "这个步骤是为了让最终建议更贴近你的梦，不是问诊。",
        "answer_label": "你的回答",
        "answer_placeholder": "写一句回答，或留空后选择跳过。",
        "answer_button": "发送回答",
        "skip_button": "先跳过",
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
        "card_title": "你的今日 Tip",
        "error_state": "界面状态读取失败，请重新开始。",
        "qa_flow_title": "梦境问答流程",
        "qa_flow_status": "进行中",
        "qa_flow_tip_status": "Tip 已生成",
        "qa_flow_error_status": "出错了",
        "qa_flow_input_placeholder": "继续描述你的梦境细节...",
        "qa_flow_send": "发送",
        "qa_flow_chip_emotion": "我感到焦虑",
        "qa_flow_chip_scene": "有一个场景",
        "qa_flow_chip_character": "有人出现",
        "qa_flow_chip_object": "我看到一个东西",
        "draft_title": "解读",
        "draft_clues_title": "梦境线索",
        "draft_clues": ["桥", "湍急的水", "独自前行", "阴天"],
        "clues_empty": "描述梦境后，线索会出现",
        "clues_hint": "以上线索基于你的输入提取",
        "draft_interpretation_title": "解读",
        "draft_expand_button": "阅读完整解读",
        "today_tip_title": "你的今日 Tip",
        "today_tip_text": "给自己一点时间和空间，允许情绪被看见，也允许自己慢慢前行。",
        "today_tip_save": "收藏",
        "sidebar_tip_label": "小贴士",
        "sidebar_tip_text": "你的梦境细节会帮助我问出更好的问题。",
        "notification_button": "通知",
        "notification_title": "通知",
        "notification_empty": "暂无新通知。",
        "notification_tip_ready": "今日小 Tips 已生成。",
        "notification_error": "出了点问题，请重试。",
        "history_button": "历史记录",
        "history_title": "会话历史",
        "history_empty": "本次会话暂无梦境记录。",
        "history_dream_label": "梦境",
        "menu_button": "菜单",
        "menu_language": "语言",
        "menu_restart": "重新开始",
        "menu_restart_desc": "清除所有数据，开始新会话",
        "menu_mode_label": "当前模式",
        "menu_mode_text": "纯文本模式",
        "interpretation_content_title": "完整解读",
        "interpretation_empty": "提交梦境后，解读内容将显示在这里。",
        "tip_saved": "已收藏",
        "tip_save": "收藏",
        "chip_emotion_prefix": "情绪：",
        "chip_scene_prefix": "场景：",
        "chip_character_prefix": "人物：",
        "chip_object_prefix": "物品：",
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
