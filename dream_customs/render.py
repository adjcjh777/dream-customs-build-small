from html import escape

from dream_customs.schema import CustomsSession, EvidenceItem, PactCard, TimelineEvent, TodayTipCard


def _nl2br(text: str) -> str:
    return "<br>".join(escape(text).splitlines())


def _phase_label(phase: str) -> str:
    labels = {
        "empty": "Empty desk",
        "record": "Record",
        "ask": "Ask",
        "interpret": "Interpret",
        "tip": "Today Tip",
        "declaring": "Declare",
        "negotiating": "Negotiate",
        "drafting": "Draft",
        "sealed": "Sealed",
        "error": "Needs attention",
    }
    return labels.get(phase, phase.title())


def render_today_tip_card(card: TodayTipCard, language: str = "en") -> str:
    is_zh = language == "zh"
    anchors = "　".join(escape(anchor) for anchor in card.dream_anchors)
    questions = "".join(f"<li>{escape(question)}</li>" for question in card.followup_questions)
    answers = "".join(f"<li>{escape(answer)}</li>" for answer in card.user_answers)
    labels = {
        "page": "今日小 Tips" if is_zh else "Today Tip",
        "thanks": "谢谢你的分享。根据你的梦境，我们为你整理了今天的参考。"
        if is_zh
        else "Thanks for sharing this. Here is one grounded suggestion for today.",
        "interpretation": "也许这个梦在提醒你" if is_zh else "Maybe this dream is pointing to",
        "today_tip": "今天的小建议" if is_zh else "Today's small suggestion",
        "tiny_action": "没试过的小事" if is_zh else "Tiny action",
        "anchors": "关键词：" if is_zh else "Anchors:",
        "history": "追问记录" if is_zh else "Question record",
        "safety_default": "这不是诊断，只是一个温和的今日参考。"
        if is_zh
        else "A gentle reflection for today, not a diagnosis or prophecy.",
        "safety_prefix": "这不是诊断。" if is_zh else "This is not a diagnosis. ",
        "highlight": "梦境细节" if is_zh else "dream detail",
    }
    tiny_action = (
        f"<section class='dqa-result-card'><div class='dqa-card-icon'>□</div><div><h3>{labels['tiny_action']}</h3><p>{escape(card.tiny_action)}</p></div></section>"
        if card.tiny_action
        else ""
    )
    caring_note = (
        f"<div class='dqa-care-note'>♡ {escape(card.caring_note)}</div>"
        if card.caring_note
        else ""
    )
    safety = (
        f"<div class='dqa-safety-note'>{labels['safety_prefix']}{escape(card.safety_note)}</div>"
        if card.safety_note
        else f"<div class='dqa-safety-note'>{labels['safety_default']}</div>"
    )
    qa_history = (
        f"<details class='dqa-qa-history'><summary>{labels['history']}</summary><ol>{questions}</ol><ul>{answers}</ul></details>"
        if questions or answers
        else ""
    )
    return f"""
<section class="dqa-tip-page" aria-label="{labels['page']}">
  <div class="dqa-tip-hero">
    <div>
      <div class="dqa-sun">☼</div>
      <h2>{labels['page']}</h2>
      <p>{labels['thanks']}</p>
    </div>
  </div>
  <article class="dqa-result-card is-interpretation">
    <div class="dqa-card-icon">☘</div>
    <div>
      <h3>{labels['interpretation']}</h3>
      <p>{escape(card.interpretation)}</p>
      <div class="dqa-anchor-strip">{labels['anchors']} {anchors}</div>
    </div>
  </article>
  <article class="dqa-result-card is-primary-tip">
    <div class="dqa-card-icon">☼</div>
    <div>
      <h3>{labels['today_tip']}</h3>
      <p>{escape(card.today_tip)}</p>
      <div class="dqa-tip-highlight">★ {escape(card.dream_anchors[0] if card.dream_anchors else labels['highlight'])}</div>
    </div>
  </article>
  {tiny_action}
  {qa_history}
  {safety}
  {caring_note}
</section>
""".strip()


def _evidence_chip(item: EvidenceItem) -> str:
    return (
        f"<span class='dc-evidence-chip is-{escape(item.status)}'>"
        f"<span class='dc-chip-dot'></span>{escape(item.label)}</span>"
    )


def render_status_bar(session: CustomsSession, text_backend: str = "demo", vision_backend: str = "demo") -> str:
    safety = "Support note ready" if session.safety_flags else "Playful reflection, not diagnosis"
    return f"""
<header class="dc-statusbar">
  <div class="dc-brand-lockup">
    <span class="dc-brand-mark">叶</span>
    <div>
      <h1>梦境问答台</h1>
  <p>记录梦境，回答或跳过温和追问，得到一个引用梦境细节的今日小 Tips。</p>
    </div>
  </div>
  <div class="dc-system-status">
    <span>Current: {escape(_phase_label(session.phase))}</span>
    <span>Text {escape(text_backend or "demo")}</span>
    <span>Vision {escape(vision_backend or "demo")}</span>
    <span>{escape(safety)}</span>
  </div>
</header>
""".strip()


def _render_event(event: TimelineEvent) -> str:
    body = f"<p>{_nl2br(event.body)}</p>" if event.body else ""
    meta = f"<span>{escape(event.meta)}</span>" if event.meta else ""
    status = f"<span>{escape(event.status)}</span>" if event.status else ""
    return f"""
<article class="dc-timeline-event is-{escape(event.role)}">
  <div class="dc-event-meta">{meta}{status}</div>
  <h3>{escape(event.title)}</h3>
  {body}
</article>
""".strip()


def render_timeline(session: CustomsSession) -> str:
    if not session.events:
        events = [
            TimelineEvent(
                role="system",
                title="梦境问答台已打开",
                body="先写下一个梦境片段。文字、图片、语音都会进入同一个 intake。",
                status="ready",
            )
        ]
    else:
        events = session.events

    evidence = "".join(_evidence_chip(item) for item in session.evidence_items[-8:])
    evidence_tray = (
        f"<div class='dc-evidence-tray'>{evidence}</div>"
        if evidence
        else (
            "<div class='dc-evidence-tray is-empty'>"
            "<span class='dc-evidence-chip is-queued'><span class='dc-chip-dot'></span>Text</span>"
            "<span class='dc-evidence-chip is-queued'><span class='dc-chip-dot'></span>Image</span>"
            "<span class='dc-evidence-chip is-queued'><span class='dc-chip-dot'></span>Voice</span>"
            "<span class='dc-evidence-chip is-queued'><span class='dc-chip-dot'></span>Mood</span>"
            "</div>"
        )
    )
    return f"""
<section class="dc-timeline-shell" aria-label="Dream QA timeline">
  <div class="dc-timeline-head">
    <div>
      <span class="dc-section-kicker">梦境问答流程</span>
      <h2>目前记录</h2>
      <p>梦境片段、追问、回答和解读草稿会按时间线留在这里。</p>
    </div>
    <span>{session.evidence_count()} filed</span>
  </div>
  {evidence_tray}
  <div class="dc-timeline-list">
    {''.join(_render_event(event) for event in events)}
  </div>
</section>
""".strip()


def render_pact_inspector(session: CustomsSession) -> str:
    if session.sealed_tip or session.draft_tip:
        return render_today_tip_card(session.sealed_tip or session.draft_tip)
    card = session.sealed_pact or session.draft_pact
    state = "sealed" if session.sealed_pact else "draft" if session.draft_pact else "waiting"
    if not card:
        return f"""
<aside class="dc-inspector is-waiting" aria-label="Today Tip preview">
  <div class="dc-inspector-kicker">解读草稿</div>
  <h2>还没有生成今日小 Tips</h2>
  <p>记录梦境并回答或跳过追问后，解读草稿和今日小 Tips 会出现在这里。Text-only 已足够开始。</p>
  <dl>
    <div><dt>Evidence</dt><dd>{session.evidence_count()} filed</dd></div>
    <div><dt>Phase</dt><dd>{escape(_phase_label(session.phase))}</dd></div>
    <div><dt>Questions</dt><dd>{len(session.question_history)} asked</dd></div>
  </dl>
</aside>
""".strip()

    contraband = "".join(f"<li>{escape(item)}</li>" for item in card.contraband)
    safety = (
        f"<div class='dc-support-note'><strong>Support note</strong><p>{escape(card.safety_note)}</p></div>"
        if card.safety_note
        else ""
    )
    return f"""
<aside class="dc-inspector is-{state}" aria-label="Today Tip preview">
  <div class="dc-inspector-kicker">解读草稿</div>
  <div class="dc-permit-row">
    <span>{escape(card.permit_id)}</span>
    <span>{escape(state.title())}</span>
  </div>
  <h2>{escape(card.visitor_name)}</h2>
  <dl>
    <div><dt>Risk level</dt><dd>{escape(card.risk_level)}</dd></div>
    <div><dt>Evidence</dt><dd>{session.evidence_count()} filed</dd></div>
    <div><dt>Questions</dt><dd>{len(session.question_history)} asked</dd></div>
  </dl>
  <section>
    <h3>Alliance reading</h3>
    <p>{escape(card.alliance_reading)}</p>
  </section>
  <section>
    <h3>Life tip for today</h3>
    <p>{escape(card.practical_suggestion)}</p>
  </section>
  <section>
    <h3>5-minute task</h3>
    <p>{escape(card.weird_task)}</p>
  </section>
  <section>
    <h3>Contraband</h3>
    <ul>{contraband}</ul>
  </section>
  {safety}
</aside>
""".strip()


def render_pact_card(card: PactCard) -> str:
    contraband = "".join(f"<li>{escape(item)}</li>" for item in card.contraband)
    safety = (
        f"<div class='dc-sealed-safety'><strong>Safety note</strong><p>{escape(card.safety_note)}</p></div>"
        if card.safety_note
        else ""
    )
    return f"""
<style>
  .pact-card {{
    color: oklch(0.170 0.016 55);
    background:
      radial-gradient(circle at 88% 0%, oklch(0.830 0.120 76 / 0.20), transparent 26%),
      linear-gradient(135deg, oklch(0.965 0.014 82), oklch(0.900 0.028 72));
    border: 1px solid oklch(0.700 0.140 32 / 0.42);
    border-radius: 18px;
    box-shadow: 0 18px 38px oklch(0.130 0.012 55 / 0.34);
    font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    line-height: 1.55;
    margin: 8px 0;
    max-width: 860px;
    padding: 24px;
  }}
  .pact-header {{
    align-items: center;
    border-bottom: 1px solid oklch(0.700 0.140 32 / 0.22);
    display: flex;
    font-weight: 720;
    justify-content: space-between;
    margin-bottom: 16px;
    padding-bottom: 10px;
  }}
  .pact-card h2 {{
    color: oklch(0.170 0.016 55) !important;
    font-size: 2rem;
    line-height: 1.1;
    margin: 0 0 4px;
    text-wrap: balance;
  }}
  .pact-card h3 {{
    color: oklch(0.455 0.090 155) !important;
    font-size: 1.35rem;
    margin: 0 0 18px;
  }}
  .pact-card p,
  .pact-card li,
  .pact-card div,
  .pact-card span {{
    color: oklch(0.900 0.018 235) !important;
    color: oklch(0.230 0.018 55) !important;
  }}
  .pact-header span {{
    color: oklch(0.280 0.020 55) !important;
  }}
  .dc-label {{
    color: oklch(0.455 0.090 155) !important;
    font-weight: 720;
  }}
  .dc-seal {{
    border: 2px solid oklch(0.700 0.140 32);
    border-radius: 999px;
    color: oklch(0.700 0.140 32) !important;
    display: inline-block;
    font-weight: 820;
    margin-top: 12px;
    padding: 8px 14px;
    transform: rotate(-4deg);
  }}
  .dc-sealed-safety {{
    background: oklch(0.700 0.140 32 / 0.10);
    border: 1px solid oklch(0.700 0.140 32 / 0.34);
    border-radius: 10px;
    padding: 12px 14px;
  }}
  .dc-sealed-safety p {{
    margin: 6px 0 0;
  }}
  .pact-card ul {{
    margin-top: 8px;
  }}
</style>
<section class="pact-card">
  <div class="pact-header">
    <span>Dream Customs</span>
    <span>{escape(card.permit_id)}</span>
  </div>
  <h2>Today's Pact</h2>
  <h3>{escape(card.visitor_name)}</h3>
  <p><span class="dc-label">Risk:</span> {escape(card.risk_level)}</p>
  <p><span class="dc-label">Alliance:</span> {escape(card.alliance_reading)}</p>
  <p><span class="dc-label">Life tip:</span> {escape(card.practical_suggestion)}</p>
  <p><span class="dc-label">Weird 5-minute task:</span> {escape(card.weird_task)}</p>
  <p><span class="dc-label">Bedtime release:</span> {escape(card.bedtime_release)}</p>
  <div><span class="dc-label">Contraband:</span><ul>{contraband}</ul></div>
  {safety}
  <span class="dc-seal">SEALED</span>
</section>
""".strip()
