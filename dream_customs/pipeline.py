import json
import re
from datetime import date
from typing import Dict, List, Optional, Tuple

from dream_customs.prompts import (
    dream_brief_prompt,
    dream_qa_state_prompt,
    followup_question_prompt,
    negotiation_prompt,
    pact_critique_prompt,
    pact_draft_prompt,
    pact_prompt,
    pact_revision_prompt,
    pact_rewrite_prompt,
    today_tip_prompt,
)
from dream_customs.render import render_pact_card, render_today_tip_card
from dream_customs.safety import needs_escalation, safety_note
from dream_customs.schema import CustomsSession, DreamIntake, DreamQAState, EvidenceItem, PactCard, TimelineEvent, TodayTipCard

MAX_DREAM_DECOMPOSITION_QUESTIONS = 3


def _normalize_language(language: str = "en") -> str:
    return "zh" if language == "zh" else "en"


def _is_zh(language: str = "en") -> bool:
    return _normalize_language(language) == "zh"


def build_intake(
    dream_text: str = "",
    voice_transcript: str = "",
    visual_clues: Optional[List[str]] = None,
    mood: str = "",
    main_question: str = "",
    recurring_symbols: Optional[List[str]] = None,
    uncertainty: str = "",
    user_context: str = "",
) -> DreamIntake:
    return DreamIntake(
        dream_text=dream_text,
        voice_transcript=voice_transcript,
        visual_clues=visual_clues or [],
        mood=mood,
        main_question=main_question,
        recurring_symbols=recurring_symbols or [],
        uncertainty=uncertainty,
        user_context=user_context,
    )


def dated_permit_id(permit_id: str, today: Optional[date] = None) -> str:
    today = today or date.today()
    text = (permit_id or "").strip()
    serial_match = re.search(r"(?:^|[-_#])(\d{1,6})\s*$", text) or re.search(
        r"(\d+)(?!.*\d)",
        text,
    )
    serial = serial_match.group(1)[-3:].zfill(3) if serial_match else "001"
    return f"DREAM{today:%Y%m%d}-{serial}"


def _stamp_card_for_today(card: PactCard) -> PactCard:
    stamped = card.model_copy(deep=True)
    stamped.permit_id = dated_permit_id(stamped.permit_id)
    return stamped


_ANCHOR_STOPWORDS = {
    "about",
    "after",
    "again",
    "an",
    "asked",
    "a",
    "before",
    "behind",
    "being",
    "carrying",
    "declare",
    "dream",
    "dreamed",
    "dreamt",
    "every",
    "feeling",
    "fragment",
    "from",
    "full",
    "into",
    "last",
    "left",
    "night",
    "paper",
    "promise",
    "through",
    "today",
    "the",
    "window",
    "with",
}

_ZH_ANCHOR_MARKERS = [
    "高楼边缘",
    "高楼",
    "边缘",
    "掉进海里",
    "掉进海",
    "海里",
    "海",
    "前任发消息",
    "发消息又消失",
    "发消息",
    "消息",
    "前任",
    "消失",
    "小孩找不到家",
    "小孩",
    "找不到家",
    "潮湿的森林",
    "潮湿森林",
    "戴面具的人",
    "面具",
    "追逐",
    "被追逐",
    "犯的错误",
    "过去犯的错误",
    "错误",
    "自责",
    "重演",
    "心率",
    "噩梦",
    "失眠",
    "红色的门",
    "红色门",
    "海边",
    "海浪",
    "森林",
    "白色猫",
    "黑猫",
    "猫",
    "空白路牌",
    "路牌",
    "大雾",
    "雾很大",
    "雾",
    "红色胡同",
    "胡同",
    "便签",
    "草图",
    "蓝色的小屋",
    "小屋",
    "红色邮箱",
    "邮箱",
    "红蓝两条路",
    "两条路",
    "旧房子",
    "天花板",
    "掉灰",
    "考试",
    "掉队",
    "旧钥匙",
    "钥匙",
    "没名字的人",
    "陌生的人",
    "白色走廊",
    "旧图书馆",
    "图书馆",
    "红色楼梯",
    "楼梯",
    "大雨",
    "窗",
    "家门",
    "旧家",
    "楼顶",
    "漆黑的走廊",
    "漆黑走廊",
    "黑暗走廊",
    "走廊",
    "教室",
    "老师",
    "交作业",
    "作业",
    "门牌子",
    "门牌",
    "脚步声",
    "心跳",
    "大雪地",
    "雪地",
    "地铁站",
    "地铁",
    "安全帽",
    "男生",
    "电梯按钮",
    "融化的按钮",
    "按钮融化",
    "数字 14",
    "数字14",
    "老楼",
    "桥",
    "水",
    "被追赶",
    "找不到路",
    "呼救",
    "蓝色楼道",
    "电梯",
    "按钮",
    "楼层",
]

_ZH_TO_EN_PHRASES = {
    "高楼边缘": "high-rise edge",
    "高楼": "high-rise",
    "边缘": "edge",
    "掉进海里": "falling into the sea",
    "掉进海": "falling into the sea",
    "海里": "sea",
    "海": "sea",
    "前任发消息": "former partner sending a message",
    "发消息又消失": "message that disappeared",
    "发消息": "sending a message",
    "消息": "message",
    "前任": "former partner",
    "消失": "disappearing",
    "小孩找不到家": "child unable to find home",
    "小孩": "child",
    "找不到家": "unable to find home",
    "潮湿的森林": "wet forest",
    "潮湿森林": "wet forest",
    "戴面具的人": "masked person",
    "面具": "mask",
    "追逐": "chase",
    "被追逐": "chase",
    "犯的错误": "past mistake",
    "过去犯的错误": "past mistake",
    "错误": "mistake",
    "自责": "self-blame",
    "重演": "replay",
    "心率": "fast heartbeat",
    "噩梦": "nightmare",
    "失眠": "insomnia",
    "红色的门": "red door",
    "红色门": "red door",
    "海边": "seaside",
    "海浪": "wave",
    "大雾": "heavy fog",
    "雾很大": "heavy fog",
    "雾": "fog",
    "森林": "forest",
    "白色猫": "white cat",
    "黑猫": "black cat",
    "猫": "cat",
    "路牌": "road sign",
    "空白路牌": "blank road sign",
    "红色胡同": "red alley",
    "胡同": "alley",
    "便签": "note",
    "草图": "sketch",
    "蓝色的小屋": "blue small house",
    "小屋": "small house",
    "红色邮箱": "red mailbox",
    "邮箱": "mailbox",
    "红蓝两条路": "red and blue roads",
    "两条路": "two roads",
    "旧房子": "old house",
    "天花板": "ceiling",
    "掉灰": "falling dust",
    "考试": "exam",
    "掉队": "falling behind",
    "旧钥匙": "old key",
    "钥匙": "key",
    "没名字的人": "nameless person",
    "陌生的人": "stranger",
    "白色走廊": "white hallway",
    "旧图书馆": "old library",
    "图书馆": "library",
    "红色楼梯": "red staircase",
    "楼梯": "staircase",
    "大雨": "heavy rain",
    "雨": "rain",
    "开着的窗": "open window",
    "窗": "window",
    "家门": "home door",
    "旧家": "old home",
    "楼顶": "rooftop",
    "漆黑的走廊": "dark hallway",
    "漆黑走廊": "dark hallway",
    "黑暗走廊": "dark hallway",
    "走廊": "hallway",
    "教室": "classroom",
    "老师": "teacher",
    "交作业": "assignment",
    "作业": "assignment",
    "门牌子": "door sign",
    "门牌": "door sign",
    "脚步声": "footsteps",
    "心跳": "heartbeat",
    "大雪地": "snowfield",
    "雪地": "snow",
    "地铁站": "subway station",
    "地铁": "subway",
    "安全帽": "hard hat",
    "男生": "young man",
    "电梯按钮": "elevator button",
    "融化的按钮": "melted button",
    "按钮融化": "melted button",
    "数字 14": "floor 14",
    "数字14": "floor 14",
    "楼层数字": "floor number",
    "楼层": "floor",
    "老楼": "old apartment building",
    "蓝色楼道": "blue hallway",
    "电梯": "elevator",
    "按钮": "button",
    "融化": "melted",
    "梦境": "dream",
}

_EN_TO_ZH_PHRASES = {
    "a simple sketch of a person standing on wavy": "海浪上的小人",
    "simple sketch of a person standing on wavy": "海浪上的小人",
    "person standing on wavy": "海浪上的小人",
    "wavy lines representing water": "海浪",
    "wavy lines": "海浪",
    "wavy": "海浪",
    "a dreamlike representation of a sea under night": "夜晚的海",
    "dreamlike representation of a sea": "夜晚的海",
    "sea under night": "夜晚的海",
    "dark sea dream": "漆黑的海",
    "dark sea": "漆黑的海",
    "wavy water": "海浪",
    "waves": "海浪",
    "wave": "海浪",
    "sea": "海",
    "crescent moon": "月牙",
    "moon": "月亮",
    "stick figure": "小人",
    "melted elevator buttons": "融化的电梯按钮",
    "melted elevator button": "融化的电梯按钮",
    "elevator buttons": "电梯按钮",
    "elevator button": "电梯按钮",
    "elevator doors": "电梯门",
    "elevator": "电梯",
    "button": "按钮",
    "floor 14": "数字 14",
    "number 14": "数字 14",
    "lost child at subway station": "地铁站里迷路的小孩",
    "lost child at subway": "地铁里迷路的小孩",
    "subway station": "地铁站",
    "subway": "地铁",
    "child figure": "小孩",
    "child": "小孩",
    "home": "回家的方向",
    "arrow": "箭头",
}


def _dedupe_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        clean = re.sub(r"\s+", " ", item.strip(" .,:;!?\"'()[]{}")).lower()
        if clean and clean not in seen:
            result.append(clean)
            seen.add(clean)
    return result


_PLACEHOLDER_ANCHORS = {
    "梦里的那个细节",
    "梦里的细节",
    "那个细节",
    "dream detail",
    "that dream detail",
    "that that dream detail",
    "the dream detail",
    "dream",
    "dream fragment",
}


def _is_placeholder_anchor(text: str) -> bool:
    clean = re.sub(r"\s+", " ", (text or "").strip().lower())
    return not clean or clean in _PLACEHOLDER_ANCHORS or "dream detail" in clean or "梦里的那个细节" in clean


def _remove_placeholder_anchors(items: List[str]) -> List[str]:
    return [item for item in items if not _is_placeholder_anchor(item)]


_VISUAL_CLUE_PREFIXES = (
    "Scene:",
    "Object:",
    "Visible text:",
    "Spatial relation:",
    "Mood cue:",
    "Uncertain detail:",
    "Surprising detail:",
)


def _flatten_visual_value(value) -> List[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        items: List[str] = []
        for item in value:
            items.extend(_flatten_visual_value(item))
        return items
    if isinstance(value, dict):
        items = []
        for item in value.values():
            items.extend(_flatten_visual_value(item))
        return items
    return []


def _clean_visual_clue_text(clue: str) -> str:
    clean = (clue or "").strip()
    if not clean:
        return ""
    try:
        parsed = json.loads(clean)
    except json.JSONDecodeError:
        parsed = None
    if parsed is not None:
        flattened = _flatten_visual_value(parsed)
        clean = ", ".join(item for item in flattened if item.strip())
    for prefix in _VISUAL_CLUE_PREFIXES:
        if clean.lower().startswith(prefix.lower()):
            clean = clean[len(prefix) :].strip()
            break
    clean = re.sub(r"\b(scene_summary|objects|visible_text|spatial_relations|mood_cues|uncertain_details|surprising_detail)\b", " ", clean)
    clean = re.sub(r"[{}\[\]\"']", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip(" .,:;!?()")
    return clean


def _visual_anchor_candidates(intake: DreamIntake) -> List[str]:
    candidates: List[str] = []
    for clue in intake.visual_clues:
        clean = _clean_visual_clue_text(clue)
        if not clean:
            continue
        for phrase in re.split(r"\s*(?:,|;|，|；|/|\n)\s*", clean):
            phrase = phrase.strip(" .,:;!?()[]{}")
            if not phrase:
                continue
            if len(phrase) > 48:
                phrase = phrase[:48].rsplit(" ", 1)[0].strip() or phrase[:48].strip()
            candidates.append(phrase)
    return _dedupe_preserve_order(candidates)


def _extract_dream_anchors(intake: DreamIntake) -> List[str]:
    raw_text = " ".join(
        [
            intake.dream_text,
            intake.voice_transcript,
            " ".join(intake.visual_clues),
            " ".join(intake.recurring_symbols),
        ]
    )
    text = raw_text.lower()
    candidates: List[str] = []
    visual_candidates = _visual_anchor_candidates(intake)
    candidates.extend(visual_candidates[:3])
    for marker in _ZH_ANCHOR_MARKERS:
        if marker in raw_text:
            candidates.append(marker)
    for number in re.findall(r"\b\d{1,3}\b", raw_text):
        if number == "14":
            candidates.append("数字 14")
    pair_pattern = re.compile(
        r"\b([a-z][a-z'-]+)\s+("
        r"paper|papers|promise|promises|window|windows|suitcase|suitcases|"
        r"clerk|clerks|sunrise|elevator|elevators|button|buttons|hallway|"
        r"gate|gates|floor|floors|stamp|stamps|number|numbers|exam|exams|"
        r"pencil|pencils|train|trains|door|doors|subway|station|stations|snow|snowfield|"
        r"hat|hats|phone|phones|water|shoe|shoes|"
        r"stairwell|stairwells|room|rooms|key|keys|note|notes|rain|moon|moons|curtain|curtains|"
        r"email|emails|meeting|meetings|deadline|deadlines|classroom|classrooms|teacher|teachers|"
        r"assignment|assignments|homework|message|messages|airport|airports|glass|bird|birds|child|children|"
        r"cat|cats|forest|forests|sign|signs|alley|alleys|mailbox|mailboxes|sketch|sketches|ceiling|ceilings"
        r")\b"
    )
    for match in pair_pattern.finditer(text):
        modifier, noun = match.groups()
        normalized_noun = noun[:-1] if noun.endswith("s") and not noun.endswith("ss") else noun
        phrase = f"{modifier} {normalized_noun}"
        if modifier not in _ANCHOR_STOPWORDS:
            candidates.append(phrase)

    noun_pattern = re.compile(
        r"\b(customs|suitcase|clerk|sunrise|elevator|button|hallway|gate|stamp|number|floor|"
        r"exam|pencil|train|door|subway|station|snow|snowfield|hat|phone|water|shoe|stairwell|"
        r"room|key|note|rain|moon|curtain|sleep|dream|email|meeting|deadline|classroom|teacher|"
        r"assignment|homework|message|airport|glass|bird|child|cat|forest|sign|alley|mailbox|sketch|ceiling)\b"
    )
    candidates.extend(match.group(1) for match in noun_pattern.finditer(text))
    candidates.extend(visual_candidates)

    return _dedupe_preserve_order(candidates)[:5]


def _english_anchor_text(text: str) -> str:
    clean = text or ""
    for source, target in sorted(_ZH_TO_EN_PHRASES.items(), key=lambda item: len(item[0]), reverse=True):
        clean = clean.replace(source, target)
    clean = re.sub(r"[\u4e00-\u9fff]+", " dream fragment ", clean)
    clean = re.sub(r"\s+", " ", clean).strip(" .,:;!?\"'()[]{}")
    return clean


def _zh_anchor_text(text: str) -> str:
    clean = re.sub(r"\s+", " ", (text or "").strip(" .,:;!?\"'()[]{}"))
    if not clean:
        return ""
    lowered = clean.lower()
    for source, target in sorted(_EN_TO_ZH_PHRASES.items(), key=lambda item: len(item[0]), reverse=True):
        if source in lowered:
            return target
    if re.search(r"[A-Za-z]", clean) and not re.search(r"[\u4e00-\u9fff]", clean):
        return ""
    return clean


def _anchors_for_language(intake: DreamIntake, language: str = "en") -> List[str]:
    anchors = _extract_dream_anchors(intake)
    if _is_zh(language):
        return _dedupe_preserve_order([anchor for anchor in (_zh_anchor_text(anchor) for anchor in anchors) if anchor])
    localized = [_english_anchor_text(anchor) for anchor in anchors]
    return _dedupe_preserve_order([anchor for anchor in localized if anchor])


def _clean_english_today_tip_language(card: TodayTipCard) -> TodayTipCard:
    cleaned = card.model_copy(deep=True)
    for field in (
        "dream_summary",
        "main_question",
        "interpretation",
        "today_tip",
        "tiny_action",
        "caring_note",
        "safety_note",
    ):
        setattr(cleaned, field, _english_anchor_text(getattr(cleaned, field)))
    cleaned.dream_anchors = _dedupe_preserve_order(
        [_english_anchor_text(anchor) for anchor in cleaned.dream_anchors if anchor]
    )
    cleaned.followup_questions = [_english_anchor_text(question) for question in cleaned.followup_questions]
    cleaned.user_answers = [_english_anchor_text(answer) for answer in cleaned.user_answers]
    return cleaned


def _clean_placeholder_phrase(text: str) -> str:
    clean = text or ""
    clean = clean.replace("梦里的那个细节", "梦境片段").replace("那个细节", "梦境片段")
    clean = re.sub(r"(?<=[A-Za-z])dream\s+detail", " dream detail", clean, flags=re.IGNORECASE)
    clean = re.sub(r"dream\s+detail(?=[A-Za-z])", "dream detail ", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\b(?:the\s+)?that\s+dream\s+detail\b", "the dream fragment", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\bdream detail(?:dream detail|dream)*\b", "dream fragment", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\bthe\s+the\s+", "the ", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\s+", " ", clean)
    return clean.strip()


def _primary_anchor(intake: DreamIntake, language: str = "en") -> str:
    anchors = _anchors_for_language(intake, language)
    if anchors:
        return anchors[0]
    return "梦里的那个细节" if _is_zh(language) else "that dream detail"


def _secondary_anchor(intake: DreamIntake, language: str = "en") -> str:
    anchors = _anchors_for_language(intake, language)
    return anchors[1] if len(anchors) > 1 else _primary_anchor(intake, language)


def _story_text(intake: DreamIntake, answers: str = "") -> str:
    return "\n".join(
        part
        for part in [
            intake.dream_text,
            intake.voice_transcript,
            " ".join(intake.visual_clues),
            intake.mood,
            intake.main_question,
            intake.uncertainty,
            intake.user_context,
            answers or "",
        ]
        if part and part.strip()
    ).lower()


def _contains_any(text: str, terms: List[str]) -> bool:
    return any(term in text for term in terms)


def _dream_theme(intake: DreamIntake, answers: str = "") -> str:
    text = _story_text(intake, answers)
    if _contains_any(text, ["小孩", "child", "找不到家", "lost", "home", "回家", "地铁", "subway"]):
        return "lost_home"
    if _contains_any(text, ["海", "海浪", "水", "月牙", "moon", "sea", "wave", "water", "dark sea"]):
        return "dark_water"
    if _contains_any(text, ["电梯", "按钮", "14", "elevator", "button", "floor"]):
        return "stuck_elevator"
    if _contains_any(text, ["图书馆", "楼梯", "便签", "call home", "library", "staircase", "sticky note"]):
        return "library_signal"
    if _contains_any(text, ["前任", "消息", "消失", "former partner", "ex", "message", "disappear"]):
        return "message_loss"
    if _contains_any(text, ["追", "被追", "chase", "chased", "running away"]):
        return "chased"
    if _contains_any(text, ["考试", "作业", "教室", "老师", "exam", "assignment", "classroom", "teacher", "homework"]):
        return "school_pressure"
    if _contains_any(text, ["路牌", "两条路", "大雾", "找不到路", "sign", "two roads", "fog", "lost road"]):
        return "road_choice"
    return "open"


def _join_anchors(anchors: List[str], language: str = "en", limit: int = 3) -> str:
    visible = [anchor for anchor in anchors[:limit] if anchor]
    if not visible:
        return "梦境片段" if _is_zh(language) else "dream fragments"
    if _is_zh(language):
        return "、".join(visible)
    if len(visible) == 1:
        return visible[0]
    return ", ".join(visible[:-1]) + f", and {visible[-1]}"


def _story_anchor_phrase(intake: DreamIntake, anchors: List[str], language: str = "en", answers: str = "") -> str:
    theme = _dream_theme(intake, answers)
    if _is_zh(language):
        themed = {
            "lost_home": "地铁站里迷路的小孩和回家的方向",
            "dark_water": "夜晚的海、海浪和月牙下的小人",
            "stuck_elevator": "电梯、融化的按钮和数字 14",
            "library_signal": "旧图书馆、红色楼梯和那张便签",
            "message_loss": "那条消息、前任和突然消失",
            "chased": "森林、白色猫和空白路牌",
            "school_pressure": "教室、作业和来不及交上的感觉",
            "road_choice": "雾里的路牌和两条路",
        }
    else:
        themed = {
            "lost_home": "the lost child, the subway, and the way home",
            "dark_water": "the dark water, the waves, and the small figure under the moon",
            "stuck_elevator": "the elevator, the melted button, and floor 14",
            "library_signal": "the old library, the red staircase, and the note",
            "message_loss": "the message, the former partner, and the disappearance",
            "chased": "the chase, the call for help, and the missing route",
            "school_pressure": "the classroom, the assignment, and the late feeling",
            "road_choice": "the foggy sign and the two roads",
        }
    if theme == "chased" and anchors:
        return _join_anchors(anchors, language)
    return themed.get(theme) or _join_anchors(anchors, language)


def _answer_snippet(answers: str, language: str = "en") -> str:
    lines = [
        line.strip()
        for line in (answers or "").splitlines()
        if line.strip() and not _is_skip_answer(line, language)
    ]
    if not lines:
        return ""
    clean = re.sub(r"\s+", " ", lines[-1]).strip(" ：:「」\"'()[]{}")
    if _is_zh(language):
        return clean[:34].rstrip("，。；、 ")
    words = clean.split()
    return " ".join(words[:14])


def _anchor_with_article(anchor: str) -> str:
    clean = (anchor or "").strip()
    if clean.lower().startswith(("the ", "a ", "an ")):
        return clean
    return f"the {clean}"


def _title_anchor(text: str) -> str:
    return " ".join(part.capitalize() for part in text.split())


def _summary_from_intake(intake: DreamIntake, language: str = "en") -> str:
    merged = intake.dream_text.strip() or intake.voice_transcript.strip()
    if not merged and intake.visual_clues:
        merged = "、".join(intake.visual_clues[:3]) if _is_zh(language) else ", ".join(intake.visual_clues[:3])
    if not merged:
        return "你记录了一个还在整理中的梦。" if _is_zh(language) else "You recorded a dream that is still taking shape."
    clean = re.sub(r"\s+", " ", merged).strip()
    if len(clean) > 72:
        clean = clean[:69].rstrip() + "..."
    if not _is_zh(language):
        clean = _clean_placeholder_phrase(_english_anchor_text(clean))
    if not _is_zh(language):
        return clean if clean.lower().startswith(("i ", "you ")) else f"You dreamed about {clean}"
    if clean.startswith(("你", "我", "I ", "i ")) or any(marker in clean[:12] for marker in ("梦见", "梦到")):
        return clean
    return f"你梦见{clean}"


def _user_supplied_text(intake: DreamIntake, answers: str = "", include_mood: bool = False) -> str:
    parts = [
        intake.dream_text,
        intake.voice_transcript,
        intake.main_question,
        intake.uncertainty,
        intake.user_context,
        answers or "",
    ]
    if include_mood:
        parts.append(intake.mood)
    return "\n".join(part.strip() for part in parts if part and part.strip())


def _question_sentence_candidates(text: str) -> List[str]:
    pieces = re.split(r"[。！？!?\n\r]+|(?<=\.)\s+|[，,；;]", text or "")
    return [piece.strip(" ：:「」\"'()[]{}") for piece in pieces if piece.strip()]


def _clean_user_question(text: str, language: str = "en") -> str:
    clean = re.sub(r"\s+", " ", (text or "").strip(" ：:「」\"'()[]{}"))
    if not clean:
        return ""
    if _is_zh(language):
        clean = re.sub(r"^(我)?(醒来后)?(最)?(想知道|想问|在想|担心|害怕)[：:，,\s]*", "", clean)
        clean = re.sub(r"^(只)?想知道[：:，,\s]*", "", clean)
        clean = clean.strip(" ：:「」\"'()[]{}")
        return clean if clean.endswith(("?", "？")) else f"{clean}？"
    clean = re.sub(
        r"^(i\s+)?(woke\s+up\s+)?(want\s+to\s+know|wonder|am\s+wondering|need\s+to\s+know|worry|fear)\s*(if|whether|why|what|how)?\s*",
        lambda match: (match.group(4) or "").strip() + " ",
        clean,
        flags=re.IGNORECASE,
    ).strip()
    clean = clean[0].upper() + clean[1:] if clean else ""
    if clean and not clean.endswith("?") and re.match(r"^(why|what|how|does|do|did|is|am|are|can|could|should|would)\b", clean, re.IGNORECASE):
        clean += "?"
    return clean


def _extract_explicit_user_question(intake: DreamIntake, answers: str = "", language: str = "en") -> str:
    if intake.main_question.strip():
        return _clean_user_question(intake.main_question, language)
    text = _user_supplied_text(intake, answers)
    if _is_zh(language):
        markers = (
            "为什么",
            "是不是",
            "会不会",
            "怎么办",
            "我该",
            "能不能",
            "代表",
            "说明",
            "预兆",
            "征兆",
            "想知道",
            "想问",
            "撑不住",
            "走出来",
            "这么难受",
        )
    else:
        markers = (
            "why",
            "what should",
            "how should",
            "does this mean",
            "do i",
            "am i",
            "is this",
            "could this",
            "can this",
            "should i",
            "i wonder",
            "want to know",
            "not coping",
            "cope",
            "a sign",
            "omen",
        )
    for sentence in _question_sentence_candidates(text):
        lowered = sentence.lower()
        if _is_skip_answer(sentence, language):
            continue
        if any(marker in lowered for marker in markers):
            return _clean_user_question(sentence, language)
    return ""


def _emotion_labels_from_text(text: str, language: str = "en") -> List[str]:
    lowered = (text or "").lower()
    if _is_zh(language):
        groups = [
            ("害怕", ["害怕", "吓", "恐惧", "心慌", "心跳很快", "惊醒"]),
            ("压力", ["压力", "撑不住", "扛不住", "崩溃", "压垮", "焦虑", "太累", "疲惫"]),
            ("难过", ["难过", "难受", "伤心", "失落", "想哭", "委屈", "孤独"]),
            ("自责", ["自责", "内疚", "愧疚", "后悔", "责怪自己"]),
            ("需要安慰", ["安慰", "被安慰", "抱抱", "关心", "陪陪", "鸡汤"]),
        ]
    else:
        groups = [
            ("fear", ["scared", "afraid", "terrified", "panic", "panicked", "frightened"]),
            ("pressure", ["overwhelmed", "not coping", "can't cope", "cannot cope", "burned out", "too much", "anxious"]),
            ("sadness", ["sad", "grief", "hurt", "lonely", "heartbroken", "upset"]),
            ("guilt", ["guilty", "ashamed", "blame myself", "regret"]),
            ("comfort", ["comfort", "reassurance", "not productivity", "not advice", "not a pep talk"]),
        ]
    labels: List[str] = []
    for label, terms in groups:
        if any(term in lowered for term in terms):
            labels.append(label)
    return _dedupe_preserve_order(labels)


def _emotion_phrase(labels: List[str], language: str = "en") -> str:
    if not labels:
        return "这个感受" if _is_zh(language) else "this feeling"
    if _is_zh(language):
        return "、".join(labels)
    if len(labels) == 1:
        return labels[0]
    return ", ".join(labels[:-1]) + f", and {labels[-1]}"


def _needs_comfort(text: str, language: str = "en") -> bool:
    lowered = (text or "").lower()
    if _is_zh(language):
        return any(term in lowered for term in ["安慰", "被安慰", "抱抱", "关心", "别催", "不是鸡汤"])
    return any(term in lowered for term in ["comfort", "reassurance", "not productivity", "not a pep talk", "not advice"])


def _should_use_emotion_led_response(intake: DreamIntake, answers: str, language: str = "en") -> bool:
    user_text = _user_supplied_text(intake, answers)
    explicit_question = _extract_explicit_user_question(intake, answers, language)
    labels = _emotion_labels_from_text(user_text, language)
    if _is_low_context_intake(intake) and _is_skip_answer(answers, language) and not explicit_question and not _needs_comfort(user_text, language):
        return False
    return bool(explicit_question or labels or _needs_comfort(user_text, language))


def _direct_question_reassurance(question: str, labels: List[str], language: str = "en") -> str:
    lowered = (question or "").lower()
    if _is_zh(language):
        if any(term in lowered for term in ["撑不住", "扛不住", "崩溃"]):
            return "它不等于你一定撑不住了；更像是在提醒你，最近的压力已经值得被认真照顾。"
        if "走出来" in lowered:
            return "它不急着证明你有没有走出来；更像是在说明这段难受还需要一点被看见的时间。"
        if any(term in lowered for term in ["预兆", "征兆", "坏事", "会不会发生"]):
            return "它不适合被当作预兆；我们先把它当作醒来后仍在身体里的担心来照顾。"
        if any(term in lowered for term in ["我是不是", "是不是我"]):
            return "它不是给你贴标签的证据；它更像是在把一个需要被接住的感受放到你面前。"
        if "为什么" in lowered or "这么难受" in lowered:
            return "这么难受不是你反应过度；梦可能只是把还没放下的感受放大给你看。"
        emotion = _emotion_phrase(labels, language)
        return f"你提到的{emotion}不是小事，它值得先被接住，而不是立刻被解释掉。"
    if any(term in lowered for term in ["not coping", "cope", "coping", "falling apart"]):
        return "This does not prove you are failing to cope; it may be showing that your pressure deserves care before answers."
    if "sign" in lowered or "omen" in lowered or "bad will happen" in lowered:
        return "This is safer to treat as a fear to care for, not as evidence that something bad will happen."
    if "am i" in lowered or "does this mean i" in lowered:
        return "This dream is not evidence for a label about you; it is one feeling asking to be met gently."
    if "why" in lowered:
        return "The ache makes sense; the dream may be enlarging a feeling that has not had enough room yet."
    emotion = _emotion_phrase(labels, language)
    return f"The {emotion} you named deserves to be met first, not explained away too quickly."


def _emotion_led_interpretation(intake: DreamIntake, answers: str, anchors: List[str], language: str = "en") -> str:
    if not _should_use_emotion_led_response(intake, answers, language):
        return ""
    question = _extract_explicit_user_question(intake, answers, language)
    labels = _emotion_labels_from_text(_user_supplied_text(intake, answers), language)
    emotion = _emotion_phrase(labels, language)
    anchor = _story_anchor_phrase(intake, anchors, language, answers)
    direct = _direct_question_reassurance(question, labels, language)
    if _is_zh(language):
        opener = f"你问的是「{question}」。" if question else ""
        return (
            f"{opener}{direct} 第一层，先承认醒来后的{emotion}是真实的，不需要被责怪。"
            f"第二层，梦里的「{anchor}」也许把这种感受变成了一个可以看的画面。"
            "第三层，今天不急着找唯一答案，先给自己一个能站稳的小支点。"
        )
    opener = f"You asked, \"{question}\" " if question else ""
    return (
        f"{opener}{direct} First, let the {emotion} be real without blaming yourself. "
        f"Second, the {_anchor_with_article(anchor)} may be the dream's concrete shape for that feeling. "
        "Third, for today the goal is not to solve the whole dream, but to give yourself one steadier place to stand."
    )


def _emotion_led_today_tip(intake: DreamIntake, answers: str, anchors: List[str], language: str = "en") -> str:
    if not _should_use_emotion_led_response(intake, answers, language):
        return ""
    if _has_prophecy_frame(_user_supplied_text(intake, answers)):
        return ""
    theme = _dream_theme(intake, answers)
    anchor = _story_anchor_phrase(intake, anchors, language, answers)
    answer_snippet = _answer_snippet(answers, language)
    if _is_zh(language):
        if theme == "lost_home":
            extra = f"如果刚才的回答里「{answer_snippet}」最重，就从它开始。" if answer_snippet else ""
            return (
                f"今天先顺着「{anchor}」照顾那种需要被带路的感觉，而不是急着解释梦的含义。"
                f"{extra}给今天补一个很小的“路标”：问一个人、查一个入口，或写下下一站在哪里。"
            )
        if theme == "dark_water":
            return (
                f"今天先把「{anchor}」当成醒来后还在身体里的浪，不当成危险证明。"
                "先选一个让自己回到岸边的动作：开灯、洗脸、发一句“我醒来有点慌，先缓一下”。"
            )
        if theme == "stuck_elevator":
            return (
                f"今天不要逼自己抵达所有楼层；先把「{anchor}」变成一个只按一次的按钮。"
                "只确认当前最卡的一层是什么，再允许自己停在那里做一个很小动作。"
            )
        if theme == "library_signal":
            return (
                f"今天把「{anchor}」当成一张提醒你回到安定处的便签。"
                "不用立刻整理完整答案，只挑一个让你有“回家感”的人、物或角落，靠近它五分钟。"
            )
        if theme == "message_loss":
            return (
                f"今天先把「{anchor}」看成一段还没被好好收起的联系。"
                "不用真的发出去，先写一封不发送的回信，让那句没说完的话有地方停靠。"
            )
        return (
            f"今天的小建议是：先别把「{anchor}」解释成结论；把它当成梦递过来的线索，"
            "问问它在替你保护哪一种感受，再给那种感受一个很小的照顾动作。"
        )
    if theme == "lost_home":
        extra = f" If your answer points to \"{answer_snippet}\", start there." if answer_snippet else ""
        return (
            f"For today, treat {anchor} as a need for guidance, not as a verdict about you.{extra} "
            "Add one tiny wayfinding marker: ask one person, check one entrance, or name the next stop."
        )
    if theme == "dark_water":
        return (
            f"For today, treat {anchor} as a wave still in your body, not proof of danger. "
            "Choose one shore-like action: turn on a light, wash your face, or tell someone you woke up unsettled."
        )
    if theme == "stuck_elevator":
        return (
            f"For today, do not make yourself reach every floor. Let {anchor} become one button: "
            "name the stuck floor, then do only one small action there."
        )
    if theme == "library_signal":
        return (
            f"For today, treat {anchor} like a note pointing you back to steadiness. "
            "Pick one person, place, or object that feels like home and spend five minutes near it."
        )
    if theme == "message_loss":
        return (
            f"For today, treat {anchor} as an unfinished contact, not a demand to reopen everything. "
            "Write one unsent reply so the unsaid sentence has somewhere to rest."
        )
    return (
        f"For today, do not turn {anchor} into a fixed conclusion. Treat it as a clue about one feeling "
        "that needs care, then give that feeling one small caring action."
    )


def _emotion_led_tiny_action(intake: DreamIntake, answers: str, anchors: List[str], language: str = "en") -> str:
    if not _should_use_emotion_led_response(intake, answers, language):
        return ""
    theme = _dream_theme(intake, answers)
    anchor = _story_anchor_phrase(intake, anchors, language, answers)
    if _is_zh(language):
        if theme == "lost_home":
            return f"用 5 分钟给「{anchor}」画一张三格小路线：我在找什么、我能问谁或查哪里、今天只走到哪一站。"
        if theme == "dark_water":
            return f"用 5 分钟做一个“上岸”动作：看着「{anchor}」，说出三个房间里的真实物件，再喝一口水或开一盏灯。"
        if theme == "stuck_elevator":
            return f"用 5 分钟写一个“只按这一层”的按钮：今天卡在哪一层、我能做的最小动作、做完就停。"
        if theme == "library_signal":
            return f"用 5 分钟把「{anchor}」改写成一张现实便签：我现在可以回到哪里，或联系谁，让自己稳一点。"
        if theme == "message_loss":
            return f"用 5 分钟写一封不发送的短信草稿，开头只写：梦里的「{anchor}」让我想承认的是……"
        return f"用 5 分钟做一个三格便签：梦里的「{anchor}」最亮的细节、它带出的感受、今天能照顾它的一小步。"
    if theme == "lost_home":
        return f"Spend five minutes making a three-box route for {anchor}: what I am looking for, who or where I can ask, and the next stop only."
    if theme == "dark_water":
        return f"Spend five minutes doing one shore action for {anchor}: name three real objects in the room, then drink water or turn on a light."
    if theme == "stuck_elevator":
        return f"Spend five minutes making a one-floor button for {anchor}: the stuck floor, the smallest action, and permission to stop after it."
    if theme == "library_signal":
        return f"Spend five minutes turning {anchor} into a real note: where can I return, or who can I contact, to feel steadier?"
    if theme == "message_loss":
        return f"Spend five minutes drafting one unsent message that begins: what {anchor} makes me want to admit is..."
    return f"Spend five minutes making three boxes for {anchor}: brightest detail, feeling it carries, and one small care step for today."


def _emotion_led_caring_note(intake: DreamIntake, answers: str, language: str = "en") -> str:
    if not _should_use_emotion_led_response(intake, answers, language):
        return ""
    labels = _emotion_labels_from_text(_user_supplied_text(intake, answers), language)
    emotion = _emotion_phrase(labels, language)
    if _is_zh(language):
        return f"你不是太脆弱，也不是需要被催着立刻想通；这份{emotion}可以先被轻轻接住。"
    return f"You are not weak for feeling {emotion}; you do not have to turn it into a lesson before you are comforted."


def _main_question_from_intake(intake: DreamIntake, language: str = "en") -> str:
    if intake.main_question.strip():
        return _clean_user_question(intake.main_question, language)
    explicit_question = _extract_explicit_user_question(intake, "", language)
    if explicit_question:
        return explicit_question
    task = _task_focus(intake.merged_text(), language)
    if task:
        if not _is_zh(language):
            return f"How can I make the {task} feel smaller and more doable today?"
        return f"今天怎样把「{task}」变成更小、更能开始的一步？"
    if _has_prophecy_frame(intake.merged_text()):
        if not _is_zh(language):
            return "How can I treat this dream as a feeling to notice, not a prediction?"
        return "我怎样把这个梦当作一种感受来照顾，而不是当成预兆？"
    primary = _primary_anchor(intake, language)
    if not _is_zh(language):
        return f"What might {_anchor_with_article(primary)} be asking me to notice today?"
    return f"这个梦里的「{primary}」可能在提醒我什么？"


def _fallback_interpretation(intake: DreamIntake, language: str = "en") -> str:
    primary = _primary_anchor(intake, language)
    secondary = _secondary_anchor(intake, language)
    if not _is_zh(language):
        return (
            f"Maybe this dream is not giving you a fixed answer. It is placing {_anchor_with_article(primary)} "
            f"beside {_anchor_with_article(secondary)} so you can notice one small stuck point today."
        )
    return (
        f"也许这个梦不是在给你一个确定答案，而是把「{primary}」和「{secondary}」放到一起，"
        "提醒你先看见今天最卡住的一小处。"
    )


def _grounded_today_tip(intake: DreamIntake, language: str = "en") -> str:
    anchors = _anchors_for_language(intake, language)
    primary = anchors[0] if anchors else _primary_anchor(intake, language)
    anchor = _story_anchor_phrase(intake, anchors, language)
    theme = _dream_theme(intake)
    if not _is_zh(language):
        if theme == "lost_home":
            return f"For today, let {anchor} become a small wayfinding cue: choose one place to ask, one entrance to check, or one next stop to name."
        if theme == "dark_water":
            return f"For today, let {anchor} become a shore cue: name what felt too large, then choose one ordinary thing that helps your body feel here again."
        if theme == "library_signal":
            return f"For today, let {anchor} become a note back to steadiness: choose one person, place, or object that feels like home and spend five minutes near it."
        if theme == "message_loss":
            return f"For today, let {anchor} become one unsent sentence, not a full conversation: write what is still tender and let it rest."
        return (
            f"For today, borrow one action from {_anchor_with_article(primary)}: open the task, write only the first line, "
            "and let that be enough for now."
        )
    if theme == "lost_home":
        return f"今天先让「{anchor}」变成一个小路标：只确认一个可以问的人、一个可以查的入口，或一个下一站。"
    if theme == "dark_water":
        return f"今天先让「{anchor}」变成一个上岸提示：说出那个太大的感受，再选一件能让身体回到当下的小事。"
    if theme == "library_signal":
        return f"今天先让「{anchor}」变成一张回到安定处的便签：靠近一个有回家感的人、地方或物件五分钟。"
    if theme == "message_loss":
        return f"今天先让「{anchor}」变成一句不发送的话，而不是一整场对话：写下还柔软的那句，然后让它停在那里。"
    return f"今天先从「{primary}」借一个动作：只做最小的第一步，不急着把整件事完成。"


def _answer_based_tiny_action(answers: str, language: str = "en") -> str:
    lowered = (answers or "").lower()
    if _is_zh(language):
        if "邮件" in lowered or "email" in lowered:
            return "给自己 5 分钟，只打开那封邮件，写下第一句话；今天不要求立刻发出。"
        if "消息" in lowered or "发消息" in lowered:
            return "给自己 5 分钟，只写一条诚实的进度消息草稿；今天先不要求把整件事做完。"
        if "作业" in lowered or "草稿" in lowered:
            return "给自己 5 分钟，只打开草稿，写下下一小段或一个待补的标题。"
        return ""
    if "email" in lowered or "message" in lowered:
        return "Set a five-minute timer, open the email, and write only the first sentence. You do not have to send it yet."
    if "assignment" in lowered or "homework" in lowered or "draft" in lowered:
        return "Set a five-minute timer, open the draft, and write only the next small heading or first sentence."
    if "presentation" in lowered or "speech" in lowered or "rehearse" in lowered:
        return "Set a five-minute timer and rehearse only the first minute, then stop and write one note for tomorrow."
    if "deadline" in lowered or "application" in lowered:
        return "Set a five-minute timer, open the application checklist, and mark only the next missing item."
    if "apolog" in lowered:
        return "Set a five-minute timer and draft one honest apology sentence without sending it yet."
    return ""


def _answer_based_today_tip(answers: str, anchor: str, language: str = "en") -> str:
    lowered = (answers or "").lower()
    if _is_zh(language):
        if "邮件" in lowered or "email" in lowered:
            return f"今天把「{anchor}」当成允许慢慢开始的按钮：只打开那封邮件，先写第一句话。"
        if "消息" in lowered or "发消息" in lowered:
            return f"今天把「{anchor}」当成一个小门牌：先给对方发一条进度消息，不要求马上完成全部。"
        if "作业" in lowered or "草稿" in lowered:
            return f"今天把「{anchor}」当成一个可以靠近的教室门口：只打开草稿，补上下一小段。"
        return ""
    if "email" in lowered or "message" in lowered:
        return (
            f"For today, treat the {anchor} as permission to start gently: "
            "open the overdue email and write only the first sentence."
        )
    if "assignment" in lowered or "homework" in lowered or "draft" in lowered:
        return (
            f"For today, treat the {anchor} as a smaller doorway: open the draft "
            "and write only the next tiny piece."
        )
    if "presentation" in lowered or "speech" in lowered or "rehearse" in lowered:
        return f"For today, let the {anchor} narrow the work: rehearse only the first minute of the presentation."
    if "deadline" in lowered or "application" in lowered:
        return f"For today, let the {anchor} become a checklist: open the application and choose one missing item."
    if "apolog" in lowered:
        return f"For today, let the {anchor} become one repair step: draft a single apology sentence."
    return ""


def _answer_based_interpretation(answers: str, anchor: str, language: str = "en") -> str:
    lowered = (answers or "").lower()
    if _is_zh(language):
        if "邮件" in lowered or "email" in lowered:
            return f"也许「{anchor}」不是在催你立刻完成什么，而是在提醒你：那封邮件可以先从一句话开始。"
        if "消息" in lowered or "message" in lowered:
            return f"也许「{anchor}」不是在催你立刻回应什么，而是在提醒你：那条消息可以先从一句草稿开始。"
        if "作业" in lowered or "草稿" in lowered:
            return f"也许「{anchor}」不是在说你已经来不及，而是在提醒你：草稿可以先从下一小段开始。"
        return ""
    if "email" in lowered:
        return (
            f"Maybe the {anchor} is not asking you to finish the overdue email at once. "
            "It is pointing to the gentler threshold: opening it and writing one first sentence."
        )
    if "message" in lowered:
        return (
            f"Maybe the {anchor} is not asking you to answer every message at once. "
            "It is pointing to the gentler threshold: opening one thread and drafting one first sentence."
        )
    if "assignment" in lowered or "homework" in lowered or "draft" in lowered:
        return (
            f"Maybe the {anchor} is not asking you to finish the whole assignment at once. "
            "It is pointing to the gentler threshold: opening the draft and adding one small piece."
        )
    if "presentation" in lowered or "speech" in lowered or "rehearse" in lowered:
        return (
            f"Maybe the {anchor} is not asking you to perfect the whole presentation tonight. "
            "It is pointing to the gentler threshold: rehearsing the first minute once."
        )
    if "deadline" in lowered or "application" in lowered:
        return (
            f"Maybe the {anchor} is not asking you to finish the whole application in one push. "
            "It is pointing to the gentler threshold: finding the next missing item."
        )
    if "apolog" in lowered:
        return (
            f"Maybe the {anchor} is not asking you to repair everything at once. "
            "It is pointing to the gentler threshold: drafting one honest sentence."
        )
    return ""


def _answer_bridge_anchor(anchors: List[str]) -> str:
    return next((anchor for anchor in anchors if "14" in anchor), anchors[0])


def _anchor_in_text(text: str, anchors: List[str]) -> bool:
    clean = (text or "").lower()
    for anchor in anchors:
        item = anchor.lower().strip()
        if item and item in clean:
            return True
        if any(marker in item and marker in clean for marker in ["电梯", "按钮", "14", "桥", "水", "elevator", "button"]):
            return True
    return False


def _text_uses_anchor(text: str, anchors: List[str]) -> bool:
    clean = (text or "").lower()
    for anchor in anchors:
        item = anchor.lower().strip()
        if not item or _is_placeholder_anchor(item):
            continue
        if item in clean:
            return True
        tokens = [token for token in re.split(r"[\s,，。:：;；、]+", item) if len(token) >= 3]
        if any(token in clean for token in tokens):
            return True
    return False


def _is_generic_visitor_name(text: str, intake: DreamIntake) -> bool:
    clean = (text or "").strip()
    if not clean:
        return True
    lowered = clean.lower()
    merged = intake.merged_text().lower()
    generic_names = {"dreamer", "night visitor", "elena", "visitor", "the visitor"}
    if lowered in generic_names:
        return True
    anchors = _extract_dream_anchors(intake)
    if anchors and not _text_uses_anchor(lowered, anchors) and lowered not in merged and len(clean.split()) <= 2:
        return True
    return False


def _looks_unclear_or_dream_literal(text: str) -> bool:
    clean = (text or "").strip()
    if len(clean) < 12:
        return True
    dream_literals = [
        "电梯运行",
        "模拟操作",
        "印章",
        "放行",
        "联盟",
        "梦境内容",
        "梦境无",
        "海关",
        "宣言",
        "魔法",
        "香薰皮",
        "果酱",
        "Dreamer",
        "dream content has no medical value",
        "release stamp",
        "customs stamp",
        "clearance stamp",
        "magical",
    ]
    return any(term in clean for term in dream_literals)


def _is_generic_daily_tip(text: str, anchors: List[str]) -> bool:
    clean = (text or "").lower()
    generic_markers = [
        "hydrate",
        "dehydration",
        "piece of fruit",
        "cognitive function",
        "morning routine",
        "take a short walk",
        "eat something",
        "drink water",
    ]
    return any(marker in clean for marker in generic_markers) and not _text_uses_anchor(clean, anchors)


def _is_generic_weird_task(text: str, anchors: List[str]) -> bool:
    clean = (text or "").lower()
    generic_markers = [
        "count the number of birds",
        "requires no special skills",
        "harmless and playful activity",
        "salute the kettle",
    ]
    return any(marker in clean for marker in generic_markers) and not _text_uses_anchor(clean, anchors)


def _is_bare_time_or_generic_release(text: str) -> bool:
    clean = (text or "").strip()
    if re.fullmatch(r"\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)?", clean):
        return True
    if len(clean.split()) <= 3:
        return True
    return False


def _safe_practical_suggestion(intake: DreamIntake) -> str:
    mood = intake.mood.strip().lower()
    if mood in {"uneasy", "foggy", "tired", "焦虑", "迷雾", "累"}:
        return (
            "Start with one body-level reset today: drink water, eat something simple, "
            "then write the most important task as a 10-minute first step."
        )
    return "Do one low-risk stabilizing thing today: drink water, eat something, and write the most important task as a 10-minute first step."


def _safe_weird_task(intake: DreamIntake) -> str:
    return "Write your smallest task on paper, draw a tiny clearance stamp beside it, and work on it for just five minutes."


def _grounded_practical_suggestion(intake: DreamIntake) -> str:
    primary = _primary_anchor(intake)
    secondary = _secondary_anchor(intake)
    if "promise" in primary or "promise" in secondary:
        return (
            "Choose one unfinished promise and shrink it into a first step small enough to finish in "
            "10 minutes."
        )
    return (
        f"Pick one real task that feels like the {primary}, then define only its first step for the next 10 minutes."
    )


def _grounded_weird_task(intake: DreamIntake) -> str:
    primary = _primary_anchor(intake)
    secondary = _secondary_anchor(intake)
    if "paper" in primary or "paper" in secondary:
        return "Write one unfinished promise on a scrap of paper, fold it like a tiny suitcase, and stamp it cleared."
    if "customs" in primary or "customs" in secondary:
        return "Make a one-line customs form for today's smallest task and mark it cleared after five minutes."
    return f"Draw the {primary} as a tiny customs stamp, press it once, and work for five minutes."


def _grounded_bedtime_release(intake: DreamIntake) -> str:
    primary = _primary_anchor(intake)
    secondary = _secondary_anchor(intake)
    return f"Tonight, the {primary} and the {secondary} are logged, cleared, and allowed to rest until morning."


def _grounded_alliance_reading(intake: DreamIntake) -> str:
    primary = _primary_anchor(intake)
    secondary = _secondary_anchor(intake)
    return (
        f"You can treat the {primary} and the {secondary} as last night's way of asking for one promise "
        "to become smaller and easier to carry today."
    )


def _grounded_question(intake: DreamIntake, question: str, language: str = "en") -> str:
    anchors = _extract_dream_anchors(intake)
    if not anchors or _text_uses_anchor(question, anchors):
        return question
    primary = _primary_anchor(intake, language)
    secondary = _secondary_anchor(intake, language)
    if not _is_zh(language):
        return (
            f"When you think about the {primary} and the {secondary}, is there one real thing today "
            "that you want to make easier to start?"
        )
    return (
        f"当你想到「{primary}」和「{secondary}」时，今天有没有一件真实的小事，"
        "你希望它变得更容易开始？"
    )


def _question_for_declared_real_task(intake: DreamIntake, language: str = "en") -> str:
    merged = intake.merged_text().lower()
    primary = _primary_anchor(intake, language)
    prophecy_question = _question_for_prophecy_frame(intake, language)
    if prophecy_question:
        return prophecy_question
    if not _is_zh(language):
        if "email" in merged:
            return f"When the {primary} shows up beside the overdue email, what would make opening that email feel smaller today?"
        if any(term in merged for term in ["assignment", "homework", "draft"]):
            return f"When the {primary} shows up beside the assignment, what is the smallest useful piece you could start today?"
        if any(term in merged for term in ["presentation", "speech", "rehearse"]):
            return f"When the {primary} shows up beside the presentation, what would make the first minute easier to rehearse?"
        if any(term in merged for term in ["deadline", "application"]):
            return f"When the {primary} shows up beside the deadline, what is the next missing item you can safely choose?"
        if "apolog" in merged:
            return f"When the {primary} shows up beside the apology, what is one honest sentence you could draft first?"
        if "message" in merged:
            return f"When the {primary} shows up beside that message, what is one sentence you could safely draft today?"
        return ""
    if "邮件" in merged or "email" in merged:
        return f"当「{primary}」和那封邮件连在一起时，今天怎样才能让打开它这件事变小一点？"
    if "作业" in merged or "草稿" in merged:
        return f"当「{primary}」和作业连在一起时，今天最小、最安全的一步可以是什么？"
    if "演讲" in merged or "汇报" in merged:
        return f"当「{primary}」和演讲连在一起时，今晚只排练开头一分钟可以怎么做？"
    if "申请" in merged or "截止" in merged:
        return f"当「{primary}」和截止时间连在一起时，今天可以先确认哪一个缺口？"
    if "道歉" in merged:
        return f"当「{primary}」和道歉连在一起时，今天可以先写哪一句真诚草稿？"
    if "消息" in merged or "发消息" in merged:
        return f"当「{primary}」和那条消息连在一起时，今天可以先写哪一句草稿？"
    return ""


def _has_prophecy_frame(text: str) -> bool:
    lowered = (text or "").lower()
    return any(
        term in lowered
        for term in [
            "sign something bad",
            "bad will happen",
            "omen",
            "prophecy",
            "predict",
            "预兆",
            "征兆",
            "坏事",
            "会不会发生",
        ]
    )


def _question_for_prophecy_frame(intake: DreamIntake, language: str = "en") -> str:
    if not _has_prophecy_frame(intake.merged_text()):
        return ""
    primary = _primary_anchor(intake, language)
    if not _is_zh(language):
        return (
            f"Rather than treating the {primary} as a prediction, what feeling did it leave in your body "
            "when you woke up?"
        )
    return f"先不把「{primary}」当成预兆。醒来时，它在你身体里留下的最明显感受是什么？"


def _task_focus(text: str, language: str = "en") -> str:
    lowered = (text or "").lower()
    if _is_zh(language):
        for term in ["演讲", "汇报", "申请", "截止", "道歉", "作业", "草稿", "邮件", "消息"]:
            if term in lowered:
                return term
        return ""
    task_terms = [
        ("presentation", ["presentation", "speech", "rehearse"]),
        ("application deadline", ["application", "deadline"]),
        ("apology", ["apolog"]),
        ("assignment", ["assignment", "homework", "draft"]),
        ("email", ["email"]),
        ("message", ["message"]),
    ]
    for label, terms in task_terms:
        if any(term in lowered for term in terms):
            return label
    return ""


def _is_low_context_intake(intake: DreamIntake) -> bool:
    merged = intake.merged_text()
    dream_text = intake.dream_text.strip()
    if not dream_text:
        return False
    cjk_count = sum(1 for char in dream_text if "\u4e00" <= char <= "\u9fff")
    word_count = len(re.findall(r"[A-Za-z0-9'-]+", dream_text))
    return (word_count and word_count <= 7) or (cjk_count and cjk_count <= 12)


def _is_skip_answer(answers: str, language: str = "en") -> bool:
    lowered = (answers or "").lower()
    return "user chose to skip" in lowered or "用户选择跳过" in lowered


def _grounded_followup_question(intake: DreamIntake, language: str = "en") -> str:
    primary = _primary_anchor(intake, language)
    if not _is_zh(language):
        return f"If the {primary} could hand you one smaller first step today, what would that step be?"
    return f"如果「{primary}」能递给你一个更小的第一步，今天那一步会是什么？"


def _first_input_focus_sentence(intake: DreamIntake, language: str = "en") -> str:
    explicit_question = _extract_explicit_user_question(intake, "", language)
    labels = _emotion_labels_from_text(_user_supplied_text(intake, "", include_mood=True), language)
    emotion = _emotion_phrase(labels, language)
    anchors = _anchors_for_language(intake, language)
    story_anchor = _story_anchor_phrase(intake, anchors, language)
    if _is_zh(language):
        if explicit_question and labels:
            return f"你最在意的是「{explicit_question}」，而且醒来后的{emotion}需要先被接住。"
        if explicit_question:
            return f"你最在意的是「{explicit_question}」，不是只想听一个固定象征解释。"
        if labels:
            return f"这个梦留下的{emotion}比符号本身更重要，我会先顺着感受看。"
        return f"核心线索先落在「{story_anchor}」上，我会先确认它和你今天的需要怎么连起来。"
    if explicit_question and labels:
        return f"your main question is \"{explicit_question}\", and the {emotion} after waking needs to be met first."
    if explicit_question:
        return f"your main question is \"{explicit_question}\", not a generic symbol reading."
    if labels:
        return f"the {emotion} after waking matters more than a fixed symbol meaning."
    return f"the strongest trail begins with {story_anchor}, so I will connect it to what you may need today."


def _decomposition_question(
    intake: DreamIntake,
    existing_count: int,
    answers: str,
    model_question: str,
    language: str = "en",
) -> str:
    anchors = _anchors_for_language(intake, language)
    story_anchor = _story_anchor_phrase(intake, anchors, language, answers)
    theme = _dream_theme(intake, answers)
    declared_question = _question_for_declared_real_task(intake, language) if existing_count == 0 else ""
    if declared_question:
        return declared_question
    if _is_zh(language):
        stage_questions = {
            "lost_home": [
                "梦里那个迷路的小孩，更像是你自己需要被带路，还是某件现实里暂时找不到家的事？",
                "如果把地铁站或回家方向看成一个场景，最让你心里一紧的是“没人带路”“找不到入口”，还是“怕把谁弄丢”？",
                "最后只确认今天的需要：你更想被安慰一下，还是想得到一个很小的找路动作？",
            ],
            "dark_water": [
                "醒来后最强的是害怕、孤单、喘不过气，还是别的身体感受？",
                "画面里的海浪、月牙或小人，哪一个最像你醒来后还忘不掉的部分？",
                "最后只确认今天的需要：你更想要安定身体，还是想理解为什么会这么慌？",
            ],
            "stuck_elevator": [
                "电梯、按钮或数字 14 里，哪一个最像你最近卡住的感觉？",
                "这个卡住更像“来不及开始”，还是“已经按了按钮却没有回应”？",
                "最后只确认今天的需要：你想要一个小行动，还是先要一句能让压力降下来的话？",
            ],
            "library_signal": [
                "旧图书馆、楼梯或便签里，哪一个最像梦在提醒你别忽略的线索？",
                "那张便签或“回家”的感觉，更像想联系某个人，还是想回到一种安定状态？",
                "最后只确认今天的需要：你想整理一个现实线索，还是先给自己一点回家的感觉？",
            ],
            "message_loss": [
                "那条消息最刺痛你的地方，是它出现了、消失了，还是它来自某个具体的人？",
                "这个梦更像在问“我还在等什么”，还是在问“我该怎么照顾还没放下的部分”？",
                "最后只确认今天的需要：你想要一句安慰，还是一个不打扰别人的小行动？",
            ],
        }
        fallback = [
            f"在「{story_anchor}」里，醒来后最强烈的感受是什么？",
            f"如果只选一个细节继续看，你会选「{story_anchor}」里的哪一处？为什么？",
            "最后只确认今天的需要：你更想被安慰、被提醒，还是得到一个很小的行动？",
        ]
    else:
        stage_questions = {
            "lost_home": [
                "Does the lost child feel more like a part of you that needs guidance, or like a real situation that has no clear way home yet?",
                "In the subway and way-home scene, what tightens most: nobody guiding you, no visible entrance, or fear of losing someone?",
                "Last check before the tip: would comfort help most today, or one tiny way-finding action?",
            ],
            "dark_water": [
                "After waking, was the strongest feeling fear, loneliness, breathlessness, or something else in your body?",
                "Which image stays with you most: the waves, the moon, or the small figure?",
                "Last check before the tip: do you need help calming your body, or understanding why the image felt so intense?",
            ],
            "stuck_elevator": [
                "Which detail feels closest to your current stuck point: the elevator, the melted button, or floor 14?",
                "Does the stuckness feel more like being late to start, or like pressing the button and getting no response?",
                "Last check before the tip: would one small action help most, or a sentence that lowers the pressure first?",
            ],
        }
        fallback = [
            f"In {story_anchor}, what feeling stayed strongest after waking?",
            f"If we keep only one detail from {story_anchor}, which one matters most, and why?",
            "Last check before the tip: do you want comfort, a reminder, or one very small action?",
        ]
    candidates = stage_questions.get(theme, fallback)
    index = min(max(existing_count, 0), MAX_DREAM_DECOMPOSITION_QUESTIONS - 1)
    question = candidates[index] if index < len(candidates) else model_question
    if question:
        return question
    return model_question or _grounded_followup_question(intake, language)


def _compose_decomposition_response(
    intake: DreamIntake,
    existing_count: int,
    question: str,
    answers: str,
    language: str = "en",
) -> str:
    anchors = _anchors_for_language(intake, language)
    story_anchor = _story_anchor_phrase(intake, anchors, language, answers)
    answer_snippet = _answer_snippet(answers, language)
    if _is_zh(language):
        if existing_count == 0:
            focus = _first_input_focus_sentence(intake, language)
            return (
                f"我先听到的是：{focus}\n\n"
                f"我会把这个梦拆成三层来看：醒来后的感受、梦里最抓人的画面（{story_anchor}）、"
                "以及它今天想帮你照顾的需要。\n\n"
                f"先问一个会影响最后建议的问题：{question}"
            )
        if existing_count == 1:
            prefix = f"我把你的回答也放进来了：{answer_snippet}。" if answer_snippet else "我再补一层具体画面。"
            return f"{prefix} 这一轮只看「{story_anchor}」里最关键的连接：{question}"
        return f"最后只确认一个方向，之后我就生成今日小 Tips：{question}"
    if existing_count == 0:
        focus = _first_input_focus_sentence(intake, language)
        return (
            f"What I hear first is that {focus}\n\n"
            f"I will unpack this in three layers: the feeling after waking, the concrete image ({story_anchor}), "
            f"and what it may be asking you to care for today.\n\n"
            f"One question that will shape the final tip: {question}"
        )
    if existing_count == 1:
        prefix = f"I am adding your answer: {answer_snippet}." if answer_snippet else "I will add one more concrete layer."
        return f"{prefix} For this round, I am looking at the key link in {story_anchor}: {question}"
    return f"One last direction check, then I will write the Today Tip: {question}"


def _polish_card_for_daily_use(card: PactCard, intake: DreamIntake, answers: str) -> PactCard:
    polished = card.model_copy(deep=True)
    merged = "\n".join([intake.merged_text(), answers or ""])
    anchors = _extract_dream_anchors(intake)
    if _is_generic_visitor_name(polished.visitor_name, intake):
        polished.visitor_name = _title_anchor(_primary_anchor(intake))

    if _looks_unclear_or_dream_literal(polished.practical_suggestion):
        polished.practical_suggestion = _safe_practical_suggestion(intake)
    elif _is_generic_daily_tip(polished.practical_suggestion, anchors):
        polished.practical_suggestion = _grounded_practical_suggestion(intake)
    elif anchors and not _text_uses_anchor(polished.practical_suggestion, anchors):
        polished.practical_suggestion = _grounded_practical_suggestion(intake)

    if _looks_unclear_or_dream_literal(polished.weird_task) and polished.weird_task.strip() == polished.practical_suggestion.strip():
        polished.weird_task = _safe_weird_task(intake)
    elif len((polished.weird_task or "").strip()) < 8:
        polished.weird_task = _safe_weird_task(intake)
    elif _is_generic_weird_task(polished.weird_task, anchors):
        polished.weird_task = _grounded_weird_task(intake)
    elif anchors and not _text_uses_anchor(polished.weird_task, anchors):
        polished.weird_task = _grounded_weird_task(intake)

    if (
        len((polished.alliance_reading or "").strip()) < 12
        or "联盟成员" in polished.alliance_reading
        or (anchors and not _text_uses_anchor(polished.alliance_reading, anchors))
    ):
        polished.alliance_reading = _grounded_alliance_reading(intake)
    if polished.risk_level.strip() in {"低", "中", "高", "low", "medium", "high"}:
        polished.risk_level = "medium: handle gently, without treating it as a warning sign"
    if _is_bare_time_or_generic_release(polished.bedtime_release) or (
        anchors and not _text_uses_anchor(polished.bedtime_release, anchors)
    ):
        polished.bedtime_release = _grounded_bedtime_release(intake)

    if not needs_escalation(merged):
        polished.safety_note = ""

    return polished


def _extract_visual_clues(vision_client, image_path: Optional[str]) -> List[str]:
    if not image_path:
        return []
    try:
        if hasattr(vision_client, "extract_witness"):
            witness = vision_client.extract_witness(image_path)
            clues = witness.to_visual_clues()
            if clues:
                return clues
    except Exception:
        pass
    try:
        return vision_client.extract_clues(image_path)
    except Exception:
        return []


def intake_from_modalities(
    dream_text: str,
    image_path: Optional[str],
    audio_path: Optional[str],
    mood: str,
    vision_client,
    asr_client,
    user_context: str = "User wants a gentle next-day suggestion after vivid dreams.",
) -> DreamIntake:
    return build_intake(
        dream_text=dream_text or "",
        voice_transcript=asr_client.transcribe(audio_path),
        visual_clues=_extract_visual_clues(vision_client, image_path),
        mood=mood or "",
        user_context=user_context,
    )


def build_qa_state(
    intake: DreamIntake,
    questions: Optional[List[str]] = None,
    answers: Optional[List[str]] = None,
    language: str = "en",
) -> DreamQAState:
    anchors = _remove_placeholder_anchors(_anchors_for_language(intake, language))
    return DreamQAState(
        dream_summary=_summary_from_intake(intake, language),
        main_question=_main_question_from_intake(intake, language),
        dream_anchors=anchors,
        followup_questions=questions or [],
        user_answers=answers or [],
        current_step="ask" if questions else "record",
    )


def _polish_today_tip(card: TodayTipCard, intake: DreamIntake, answers: str = "", language: str = "en") -> TodayTipCard:
    polished = card.model_copy(deep=True)
    answer_lines = [line.strip() for line in (answers or "").splitlines() if line.strip()]
    if answer_lines:
        polished.user_answers = answer_lines
    intake_anchors = _remove_placeholder_anchors(_anchors_for_language(intake, language))
    card_anchors = _remove_placeholder_anchors(
        polished.dream_anchors
        if _is_zh(language)
        else _dedupe_preserve_order([_english_anchor_text(anchor) for anchor in polished.dream_anchors])
    )
    if intake_anchors and not any(_text_uses_anchor(anchor, intake_anchors) for anchor in card_anchors):
        anchors = intake_anchors
    else:
        anchors = card_anchors or intake_anchors
    if not anchors:
        anchors = _remove_placeholder_anchors([_primary_anchor(intake, language)])
    if not anchors:
        anchors = ["梦境片段" if _is_zh(language) else "dream fragment"]
    polished.dream_anchors = anchors
    for field in (
        "dream_summary",
        "main_question",
        "interpretation",
        "today_tip",
        "tiny_action",
        "caring_note",
        "safety_note",
    ):
        setattr(polished, field, _clean_placeholder_phrase(getattr(polished, field)))
    if not polished.dream_summary.strip() or _is_placeholder_anchor(polished.dream_summary) or not _text_uses_anchor(polished.dream_summary, anchors):
        polished.dream_summary = _summary_from_intake(intake, language)
    explicit_question = _extract_explicit_user_question(intake, answers, language)
    if explicit_question:
        polished.main_question = explicit_question
    elif (
        not polished.main_question.strip()
        or _is_placeholder_anchor(polished.main_question)
        or not _text_uses_anchor(polished.main_question, anchors)
    ):
        polished.main_question = _main_question_from_intake(intake, language)
    emotion_interpretation = _emotion_led_interpretation(intake, answers, anchors, language)
    answer_interpretation = _answer_based_interpretation(answers, _answer_bridge_anchor(anchors), language)
    if emotion_interpretation:
        polished.interpretation = emotion_interpretation
    elif answer_interpretation:
        polished.interpretation = answer_interpretation
    elif _has_prophecy_frame(intake.merged_text()):
        anchor = _answer_bridge_anchor(anchors)
        polished.interpretation = (
            f"Maybe the {anchor} is best treated as a fear-shaped image, not as evidence that something bad will happen."
            if not _is_zh(language)
            else f"也许「{anchor}」更适合被当作一种害怕的画面，而不是坏事会发生的证据。"
        )
    elif _is_low_context_intake(intake) and _is_skip_answer(answers, language):
        anchor = _answer_bridge_anchor(anchors)
        polished.interpretation = (
            f"With only a few details, I would keep this very light: the {anchor} is one clue to notice, not enough for a firm reading."
            if not _is_zh(language)
            else f"目前线索很少，先把「{anchor}」当作一个可以继续补充的线索，而不是确定解读。"
        )
    elif not polished.interpretation.strip() or not _anchor_in_text(polished.interpretation, anchors):
        polished.interpretation = _fallback_interpretation(intake, language)
    generic_tip_markers = ["drink water", "hydrate", "多休息", "保持积极", "take a walk"]
    emotion_tip = _emotion_led_today_tip(intake, answers, anchors, language)
    answer_tip = _answer_based_today_tip(answers, anchors[0], language)
    if emotion_tip:
        polished.today_tip = emotion_tip
    elif answer_tip:
        polished.today_tip = answer_tip
    elif _has_prophecy_frame(intake.merged_text()):
        anchor = anchors[0]
        polished.today_tip = (
            f"For today, do not test whether the {anchor} is a sign. Name one ordinary worry it resembles, then choose one small calming step."
            if not _is_zh(language)
            else f"今天先不要验证「{anchor}」是不是预兆；写下它像哪一种普通担心，再选一个很小的安定动作。"
        )
    elif _is_low_context_intake(intake) and _is_skip_answer(answers, language):
        anchor = anchors[0]
        polished.today_tip = (
            f"For today, keep the {anchor} as a note, not a conclusion: add one concrete detail before you act on the dream."
            if not _is_zh(language)
            else f"今天先把「{anchor}」当作记录，不当作结论：再补一个具体细节，然后再行动。"
        )
    elif (
        not polished.today_tip.strip()
        or any(marker in polished.today_tip.lower() for marker in generic_tip_markers)
        or _is_placeholder_anchor(polished.today_tip)
        or not _anchor_in_text(polished.today_tip, anchors)
    ):
        polished.today_tip = _grounded_today_tip(intake, language)
    hard_action_markers = ["address it immediately", "fix it immediately", "solve it immediately"]
    emotion_action = _emotion_led_tiny_action(intake, answers, anchors, language)
    answer_action = _answer_based_tiny_action(answers, language)
    if emotion_action:
        polished.tiny_action = emotion_action
    elif answer_action:
        polished.tiny_action = answer_action
    elif _has_prophecy_frame(intake.merged_text()):
        polished.tiny_action = (
            "Spend five minutes writing: what did I feel, what ordinary worry could it echo, and what can I do safely today?"
            if not _is_zh(language)
            else "用 5 分钟写下：我醒来时感觉到了什么？它像哪种普通担心？今天我能安全做哪一小步？"
        )
    elif _is_low_context_intake(intake) and _is_skip_answer(answers, language):
        polished.tiny_action = (
            "Add one missing detail: color, body feeling, repeated object, or what happened just before waking."
            if not _is_zh(language)
            else "补一个缺失细节：颜色、身体感受、重复物件，或醒来前最后发生的事。"
        )
    elif (
        not polished.tiny_action.strip()
        or _is_placeholder_anchor(polished.tiny_action)
        or not _anchor_in_text(polished.tiny_action, anchors)
        or any(marker in polished.tiny_action.lower() for marker in hard_action_markers)
    ):
        anchor_phrase = _story_anchor_phrase(intake, anchors, language, answers)
        theme = _dream_theme(intake, answers)
        if _is_zh(language):
            if theme == "lost_home":
                polished.tiny_action = f"用 5 分钟给「{anchor_phrase}」补一张小路标：我在找什么、能问哪里、下一站是什么。"
            elif theme == "dark_water":
                polished.tiny_action = f"用 5 分钟给「{anchor_phrase}」找一个上岸动作：看见三个真实物件，再做一件让身体安定的小事。"
            elif theme == "library_signal":
                polished.tiny_action = f"用 5 分钟把「{anchor_phrase}」变成现实便签：今天我可以靠近哪一个安定来源？"
            elif theme == "message_loss":
                polished.tiny_action = f"用 5 分钟给「{anchor_phrase}」写一句不发送的话，然后把手机放下。"
            else:
                polished.tiny_action = f"用 5 分钟写下：今天和「{anchors[0]}」有关的第一小步是什么？"
        else:
            if theme == "lost_home":
                polished.tiny_action = f"Spend five minutes adding a small route marker for {anchor_phrase}: what I seek, where I can ask, and the next stop."
            elif theme == "dark_water":
                polished.tiny_action = f"Spend five minutes finding a shore action for {anchor_phrase}: name three real objects, then do one grounding thing."
            elif theme == "library_signal":
                polished.tiny_action = f"Spend five minutes turning {anchor_phrase} into a real note: which steady source can I move closer to today?"
            elif theme == "message_loss":
                polished.tiny_action = f"Spend five minutes writing one unsent sentence for {anchor_phrase}, then put the phone down."
            else:
                polished.tiny_action = f"Spend five minutes writing the first small step connected to the {anchors[0]}."
    emotion_caring_note = _emotion_led_caring_note(intake, answers, language)
    if emotion_caring_note:
        polished.caring_note = emotion_caring_note
    elif not polished.caring_note.strip():
        polished.caring_note = (
            "你不需要一醒来就解决整个梦，先把一个细节照亮就很好。"
            if _is_zh(language)
            else "You do not have to solve the whole dream this morning; noticing one detail is enough."
        )
    elif any(
        marker in polished.caring_note.lower()
        for marker in ["does not indicate any real-life concerns", "does not indicate any real life concerns"]
    ):
        polished.caring_note = (
            "你刚才提到的现实困扰值得被温柔对待；今天先照顾一个很小的入口。"
            if _is_zh(language)
            else "The real concern you named deserves gentle handling; today, start with one small doorway into it."
        )
    elif not _is_zh(language) and any(marker in polished.caring_note.lower() for marker in ["whole building", "one floor at a time"]):
        polished.caring_note = "You do not have to solve the whole dream this morning; start by noticing one detail and one small next step."
    elif _is_zh(language) and "所有楼层" in polished.caring_note:
        polished.caring_note = "你不需要一醒来就解释完整个梦；先照顾一个细节和一个很小的下一步就好。"
    merged = "\n".join([intake.merged_text(), answers or ""])
    polished.safety_note = safety_note(language) if needs_escalation(merged) else ""
    if not _is_zh(language):
        polished = _clean_english_today_tip_language(polished)
    return polished


def generate_today_tip(
    intake: DreamIntake,
    answers: str,
    text_client,
    language: str = "en",
    followup_questions: Optional[List[str]] = None,
) -> TodayTipCard:
    language = _normalize_language(language)
    qa_state = build_qa_state(
        intake,
        questions=followup_questions or [],
        answers=[answer for answer in [answers] if answer],
        language=language,
    )
    prompt = today_tip_prompt(qa_state, language=language)
    try:
        if hasattr(text_client, "generate_today_tip"):
            card = text_client.generate_today_tip(prompt)
        else:
            legacy, _html = generate_pact(intake, answers, text_client)
            card = TodayTipCard(
                dream_summary=qa_state.dream_summary,
                main_question=qa_state.main_question,
                dream_anchors=qa_state.dream_anchors,
                followup_questions=qa_state.followup_questions,
                user_answers=qa_state.user_answers,
                interpretation=legacy.alliance_reading,
                today_tip=legacy.practical_suggestion,
                tiny_action=legacy.weird_task,
                caring_note=legacy.bedtime_release,
                safety_note=legacy.safety_note,
            )
    except Exception:
        card = TodayTipCard(
            dream_summary=qa_state.dream_summary,
            main_question=qa_state.main_question,
            dream_anchors=qa_state.dream_anchors,
            followup_questions=qa_state.followup_questions,
            user_answers=qa_state.user_answers,
                interpretation=_fallback_interpretation(intake, language),
                today_tip=_grounded_today_tip(intake, language),
            )
    card.followup_questions = qa_state.followup_questions
    if qa_state.user_answers:
        card.user_answers = qa_state.user_answers
    return _polish_today_tip(card, intake, answers, language)


def generate_negotiation(intake: DreamIntake, text_client) -> Dict:
    prompt = negotiation_prompt(intake)
    return text_client.generate_negotiation(prompt)


def generate_pact(intake: DreamIntake, answers: str, text_client) -> Tuple[PactCard, str]:
    prompt = pact_prompt(intake, answers)
    card = text_client.generate_pact(prompt)
    merged = intake.merged_text() + "\n" + answers
    card = _polish_card_for_daily_use(card, intake, answers)
    if needs_escalation(merged):
        card.safety_note = safety_note()
    card = _stamp_card_for_today(card)
    return card, render_pact_card(card)


def _clean_repeated_articles(text: str) -> str:
    clean = re.sub(r"\bthe\s+an\s+", "an ", text, flags=re.IGNORECASE)
    clean = re.sub(r"\bthe\s+the\s+", "the ", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\ban\s+an\s+", "an ", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\ba\s+a\s+", "a ", clean, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", clean).strip()


def _clean_card_grammar(card: PactCard) -> PactCard:
    cleaned = card.model_copy(deep=True)
    cleaned.visitor_name = _clean_repeated_articles(cleaned.visitor_name)
    cleaned.risk_level = _clean_repeated_articles(cleaned.risk_level)
    cleaned.alliance_reading = _clean_repeated_articles(cleaned.alliance_reading)
    cleaned.practical_suggestion = _clean_repeated_articles(cleaned.practical_suggestion)
    cleaned.weird_task = _clean_repeated_articles(cleaned.weird_task)
    cleaned.bedtime_release = _clean_repeated_articles(cleaned.bedtime_release)
    cleaned.contraband = [_clean_repeated_articles(item) for item in cleaned.contraband]
    return cleaned


def generate_model_led_pact(intake: DreamIntake, answers: str, text_client) -> Tuple[PactCard, str]:
    brief = text_client.generate_brief(dream_brief_prompt(intake))
    card = text_client.generate_pact_draft(pact_draft_prompt(brief, answers))
    critique = text_client.critique_pact(pact_critique_prompt(brief, card))
    if not critique.passes and critique.rewrite_instruction.strip():
        card = text_client.rewrite_pact(pact_rewrite_prompt(brief, card, critique))
    card = _clean_card_grammar(card)
    card = _polish_card_for_daily_use(card, intake, answers)
    merged = intake.merged_text() + "\n" + answers
    if needs_escalation(merged):
        card.safety_note = safety_note()
    else:
        card.safety_note = ""
    card = _stamp_card_for_today(card)
    return card, render_pact_card(card)


def _supports_model_led_pact(text_client) -> bool:
    return all(
        callable(getattr(text_client, name, None))
        for name in ("generate_brief", "generate_pact_draft", "critique_pact", "rewrite_pact")
    )


def create_session(language: str = "en") -> CustomsSession:
    language = _normalize_language(language)
    return CustomsSession(
        language=language,
        events=[
            TimelineEvent(
                role="system",
                title="梦境问答台已打开" if _is_zh(language) else "Dream QA is open",
                body=(
                    "先记录一个梦境片段。文字永远可用，图片和语音会变成同一个梦境 intake 的线索。"
                    if _is_zh(language)
                    else "Record a dream fragment first. Text always works; image and voice become clues in the same intake."
                ),
                status="ready",
            )
        ]
    )


def _append_text(existing: str, new_text: str) -> str:
    new_text = new_text.strip()
    if not new_text:
        return existing
    if not existing.strip():
        return new_text
    if new_text in existing:
        return existing
    return f"{existing.strip()}\n{new_text}"


def _merge_unique(existing: List[str], incoming: List[str]) -> List[str]:
    seen = {item.strip().lower() for item in existing}
    merged = list(existing)
    for item in incoming:
        clean = item.strip()
        if clean and clean.lower() not in seen:
            merged.append(clean)
            seen.add(clean.lower())
    return merged


def _event(role: str, title: str, body: str = "", meta: str = "", status: str = "") -> TimelineEvent:
    return TimelineEvent(role=role, title=title, body=body, meta=meta, status=status)


def _record_safety(session: CustomsSession) -> None:
    merged = "\n".join([session.intake.merged_text(), session.answers_text()])
    if needs_escalation(merged) and "escalation" not in session.safety_flags:
        session.safety_flags.append("escalation")
        session.events.append(
            _event(
                "system",
                "Safety note attached",
                safety_note(),
                status="support",
            )
        )


def add_evidence(
    session: CustomsSession,
    dream_text: str = "",
    image_path: Optional[str] = None,
    audio_path: Optional[str] = None,
    mood: str = "",
    vision_client=None,
    asr_client=None,
    language: str = "en",
) -> CustomsSession:
    language = _normalize_language(language)
    next_session = session.model_copy(deep=True)
    next_session.language = language
    added_items: List[EvidenceItem] = []

    if dream_text and dream_text.strip():
        clean_text = dream_text.strip()
        next_session.intake.dream_text = _append_text(next_session.intake.dream_text, clean_text)
        added_items.append(
            EvidenceItem(
                type="text",
                label="Dream note" if not _is_zh(language) else "梦境记录",
                status="selected",
                content=clean_text,
            )
        )

    if mood and mood.strip() and mood.strip() != next_session.intake.mood:
        next_session.intake.mood = mood.strip()
        added_items.append(
            EvidenceItem(
                type="mood",
                label=f"Mood: {mood.strip()}" if not _is_zh(language) else f"心情：{mood.strip()}",
                status="selected",
                content=mood.strip(),
            )
        )

    if image_path:
        clues: List[str] = []
        error = ""
        try:
            clues = _extract_visual_clues(vision_client, image_path) if vision_client else []
        except Exception:
            clues = []
            error = "Image clue extraction failed. Text-only path remains available."
        if clues:
            next_session.intake.visual_clues = _merge_unique(next_session.intake.visual_clues, clues)
            added_items.append(
                EvidenceItem(
                    type="image",
                    label=f"Image clues ({len(clues)})" if not _is_zh(language) else f"图片线索（{len(clues)}）",
                    status="extracted",
                    content=", ".join(clues),
                    source_path=image_path,
                )
            )
        else:
            added_items.append(
                EvidenceItem(
                    type="image",
                    label="Image evidence" if not _is_zh(language) else "图片证据",
                    status="failed",
                    source_path=image_path,
                    error=error
                    or (
                        "No visual clues extracted. Continue with text or voice."
                        if not _is_zh(language)
                        else "没有提取到视觉线索，可以继续使用文字或语音。"
                    ),
                )
            )

    if audio_path:
        transcript = ""
        error = ""
        try:
            transcript = asr_client.transcribe(audio_path) if asr_client else ""
        except Exception:
            error = "Voice transcription failed. Text-only path remains available."
        if transcript.strip():
            clean_transcript = transcript.strip()
            next_session.intake.voice_transcript = _append_text(next_session.intake.voice_transcript, clean_transcript)
            added_items.append(
                EvidenceItem(
                    type="audio",
                    label="Voice transcript" if not _is_zh(language) else "语音转写",
                    status="extracted",
                    content=clean_transcript,
                    source_path=audio_path,
                )
            )
        else:
            added_items.append(
                EvidenceItem(
                    type="audio",
                    label="Voice evidence" if not _is_zh(language) else "语音证据",
                    status="failed",
                    source_path=audio_path,
                    error=error
                    or (
                        "No transcript returned. Continue by typing the fragment."
                        if not _is_zh(language)
                        else "没有返回转写结果，可以继续手动输入片段。"
                    ),
                )
            )

    if not added_items:
        next_session.phase = "error"
        next_session.events.append(
            _event(
                "error",
                "还没有梦境材料" if _is_zh(language) else "No dream material yet",
                "请先添加文字、图片或语音；text-only 路径始终可用。"
                if _is_zh(language)
                else "Add text, image, or voice first; the text-only path always works.",
                status="empty",
            )
        )
        return next_session

    next_session.evidence_items.extend(added_items)
    next_session.phase = "record"
    next_session.qa_state = build_qa_state(next_session.intake, language=language)
    summary = "\n".join(f"{item.label}: {item.content or item.error}" for item in added_items)
    next_session.events.append(
        _event("user", "梦境已记录" if _is_zh(language) else "Dream recorded", summary, status="record")
    )
    _record_safety(next_session)
    return next_session


def ask_questions(session: CustomsSession, text_client, force_another: bool = False, language: str = "en") -> CustomsSession:
    language = _normalize_language(language)
    next_session = session.model_copy(deep=True)
    next_session.language = language
    if not next_session.intake.merged_text():
        next_session.phase = "error"
        next_session.events.append(
            _event(
                "error",
                "还没有梦境记录" if _is_zh(language) else "No dream note yet",
                "请先添加一个梦境片段，再进入追问。"
                if _is_zh(language)
                else "Add a dream fragment before the follow-up question.",
                status="empty",
            )
        )
        return next_session

    existing_count = len(next_session.question_history)
    if existing_count >= MAX_DREAM_DECOMPOSITION_QUESTIONS:
        next_session.phase = "ask"
        next_session.qa_state = build_qa_state(
            next_session.intake,
            questions=next_session.question_history,
            answers=next_session.answer_history,
            language=language,
        )
        next_session.events.append(
            _event(
                "assistant",
                "线索已经足够" if _is_zh(language) else "Enough context gathered",
                (
                    "我已经问到 3 个核心问题了；现在更适合生成今日小 Tips，而不是继续追问。"
                    if _is_zh(language)
                    else "I have asked three core questions; it is better to generate the Today Tip than keep questioning."
                ),
                status="ready",
            )
        )
        return next_session

    prompt = (
        followup_question_prompt(next_session.intake, next_session.question_history, next_session.answer_history, language)
        if force_another
        else negotiation_prompt(next_session.intake, language)
    )
    negotiation = text_client.generate_negotiation(prompt)
    questions = [question for question in negotiation.get("questions", []) if question]
    task_question = _question_for_declared_real_task(next_session.intake, language)
    if task_question:
        questions = [task_question] + [question for question in questions if question != task_question]
    fresh_questions = [question for question in questions if question not in next_session.question_history]
    if force_another and not fresh_questions:
        fresh_questions = [
            "如果今天只需要一个更小的第一步，它会是什么？"
            if _is_zh(language)
            else "If today only needed one smaller first step, what would it be?"
        ]
    if not fresh_questions:
        fresh_questions = questions[:3]
    if fresh_questions:
        fresh_questions = [_grounded_question(next_session.intake, fresh_questions[0], language)] + fresh_questions[1:]
    seen_questions = set(next_session.question_history)
    deduped_questions: List[str] = []
    for question in fresh_questions:
        if question and question not in seen_questions:
            deduped_questions.append(question)
            seen_questions.add(question)
    if force_another and not deduped_questions:
        deduped_questions = [_grounded_followup_question(next_session.intake, language)]
    fresh_questions = deduped_questions

    model_question = fresh_questions[0] if fresh_questions else _grounded_followup_question(next_session.intake, language)
    focused_question = _decomposition_question(
        next_session.intake,
        existing_count,
        next_session.answers_text(),
        model_question,
        language,
    )
    visible_question = _compose_decomposition_response(
        next_session.intake,
        existing_count,
        focused_question,
        next_session.answers_text(),
        language,
    )
    if visible_question not in next_session.question_history:
        next_session.question_history.append(visible_question)
    next_session.phase = "ask"
    next_session.qa_state = build_qa_state(
        next_session.intake,
        questions=next_session.question_history,
        answers=next_session.answer_history,
        language=language,
    )
    next_session.qa_state.current_step = "ask"
    next_session.events.append(
        _event(
            "assistant",
            "梦境助手理解与追问" if _is_zh(language) and existing_count == 0 else (
                "梦境助手追问" if _is_zh(language) else (
                    "Dream QA understanding and question" if existing_count == 0 else "Dream QA question"
                )
            ),
            visible_question,
            meta=str(negotiation.get("visitor_name", "")),
            status="question",
        )
    )
    return next_session


def answer_question(session: CustomsSession, answer: str, language: str = "en") -> CustomsSession:
    language = _normalize_language(language)
    next_session = session.model_copy(deep=True)
    next_session.language = language
    if not answer or not answer.strip():
        next_session.phase = "error"
        next_session.events.append(
            _event("error", "No answer filed", "Write a reply, or choose to skip the question.", status="empty")
        )
        return next_session
    next_session.answer_history.append(answer.strip())
    next_session.phase = "ask"
    next_session.qa_state = build_qa_state(
        next_session.intake, next_session.question_history, next_session.answer_history, language=language
    )
    next_session.events.append(_event("user", "追问回答" if _is_zh(language) else "Question answered", answer.strip(), status="answered"))
    _record_safety(next_session)
    return next_session


def skip_question(session: CustomsSession, language: str = "en") -> CustomsSession:
    language = _normalize_language(language)
    next_session = session.model_copy(deep=True)
    next_session.language = language
    skip_text = "用户选择跳过这个追问。" if _is_zh(language) else "The user chose to skip this question."
    next_session.answer_history.append(skip_text)
    next_session.phase = "ask"
    next_session.qa_state = build_qa_state(
        next_session.intake, next_session.question_history, next_session.answer_history, language=language
    )
    next_session.events.append(_event("user", "跳过追问" if _is_zh(language) else "Question skipped", skip_text, status="skipped"))
    return next_session


def finish_today_tip(session: CustomsSession, text_client, language: str = "en") -> CustomsSession:
    language = _normalize_language(language)
    next_session = session.model_copy(deep=True)
    next_session.language = language
    if not next_session.intake.merged_text():
        next_session.phase = "error"
        next_session.events.append(
            _event(
                "error",
                "今日小 Tips 需要梦境材料" if _is_zh(language) else "Today Tip needs dream material",
                "请先添加至少一个梦境片段。"
                if _is_zh(language)
                else "Add at least one dream fragment first.",
                status="empty",
            )
        )
        return next_session
    answers = next_session.answers_text()
    card = generate_today_tip(
        next_session.intake,
        answers,
        text_client,
        language=language,
        followup_questions=next_session.question_history,
    )
    next_session.qa_state = build_qa_state(
        next_session.intake, next_session.question_history, next_session.answer_history, language=language
    )
    next_session.qa_state.dream_summary = card.dream_summary
    next_session.qa_state.main_question = card.main_question
    next_session.qa_state.dream_anchors = card.dream_anchors
    next_session.qa_state.current_step = "tip"
    next_session.draft_tip = card
    next_session.sealed_tip = card
    next_session.draft_pact = None
    next_session.sealed_pact = None
    next_session.phase = "tip"
    next_session.events.append(
        _event(
            "tip",
            "今日小 Tips 已生成" if _is_zh(language) else "Today Tip generated",
            f"{card.interpretation}\n{card.today_tip}",
            status="tip",
        )
    )
    _record_safety(next_session)
    return next_session


def draft_pact(session: CustomsSession, text_client) -> CustomsSession:
    next_session = session.model_copy(deep=True)
    if not next_session.intake.merged_text():
        next_session.phase = "error"
        next_session.events.append(
            _event("error", "Pact needs dream material", "Add at least one fragment before drafting a pact.", status="empty")
        )
        return next_session

    answers = next_session.answers_text() or "The user has not answered yet; infer a gentle pact from the declaration."
    if _supports_model_led_pact(text_client):
        card, _html = generate_model_led_pact(next_session.intake, answers, text_client)
    else:
        card, _html = generate_pact(next_session.intake, answers, text_client)
    next_session.draft_pact = card
    next_session.phase = "drafting"
    next_session.events.append(
        _event(
            "pact",
            "Draft pact prepared",
            f"{card.visitor_name}\n{card.practical_suggestion}\n{card.weird_task}",
            meta=card.permit_id,
            status="draft",
        )
    )
    _record_safety(next_session)
    return next_session


def _apply_revision_hint(card: PactCard, revision_request: str) -> PactCard:
    request = revision_request.lower()
    revised = card.model_copy(deep=True)
    if any(term in request for term in ["strange", "weird", "怪", "更奇怪", "更怪"]):
        revised.weird_task = (
            "Write the smallest task on paper and stamp it with an invisible release mark."
        )
    elif any(term in request for term in ["gentle", "softer", "温和", "轻一点"]):
        revised.risk_level = (
            "soft orange: place it gently before interpreting it"
        )
        revised.practical_suggestion = (
            "Choose one start that does not need finishing today. Stop after five minutes."
        )
    elif revision_request.strip():
        revised.practical_suggestion = (
            f"{revised.practical_suggestion} Revision note: {revision_request.strip()}"
        )
    return revised


def revise_pact(session: CustomsSession, revision_request: str, text_client) -> CustomsSession:
    next_session = session.model_copy(deep=True)
    if not next_session.draft_pact:
        next_session = draft_pact(next_session, text_client)
        if not next_session.draft_pact:
            return next_session

    answers = next_session.answers_text()
    prompt = pact_revision_prompt(
        next_session.intake,
        answers,
        next_session.draft_pact.to_plain_text(),
        revision_request,
    )
    card = text_client.generate_pact(prompt)
    merged = next_session.intake.merged_text() + "\n" + answers
    if needs_escalation(merged):
        card.safety_note = safety_note()
    card = _apply_revision_hint(card, revision_request or "")
    card = _stamp_card_for_today(card)
    next_session.draft_pact = card
    next_session.phase = "drafting"
    next_session.events.append(
        _event(
            "pact",
            "Draft pact revised",
            revision_request.strip() or "The draft was tightened for today's smallest action.",
            meta=card.permit_id,
            status="revised",
        )
    )
    return next_session


def seal_pact(session: CustomsSession) -> CustomsSession:
    next_session = session.model_copy(deep=True)
    if not next_session.draft_pact:
        next_session.phase = "error"
        next_session.events.append(
            _event("error", "Nothing to seal yet", "Draft a pact before sealing today's agreement.", status="empty")
        )
        return next_session
    next_session.draft_pact = _stamp_card_for_today(next_session.draft_pact)
    next_session.sealed_pact = next_session.draft_pact
    next_session.phase = "sealed"
    next_session.events.append(
        _event(
            "pact",
            "Today's pact sealed",
            next_session.sealed_pact.bedtime_release,
            meta=next_session.sealed_pact.permit_id,
            status="sealed",
        )
    )
    return next_session
