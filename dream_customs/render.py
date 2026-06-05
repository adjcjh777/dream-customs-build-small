from html import escape

from dream_customs.schema import CustomsSession, EvidenceItem, PactCard, TimelineEvent


def _nl2br(text: str) -> str:
    return "<br>".join(escape(text).splitlines())


def _phase_label(phase: str) -> str:
    labels = {
        "empty": "Empty desk",
        "declaring": "Declare",
        "negotiating": "Negotiate",
        "drafting": "Draft",
        "sealed": "Sealed",
        "error": "Needs attention",
    }
    return labels.get(phase, phase.title())


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
    <span class="dc-brand-mark">DC</span>
    <div>
      <h1>Dream Customs / 梦境海关</h1>
      <p>Turn last night's strange visitor into one gentle pact for the day: a practical suggestion, a small weird task, and a bedtime release.</p>
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
                title="The night desk is open",
                body="Start with one fragment. The clerk can work from text, image, voice, or only the mood.",
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
<section class="dc-timeline-shell" aria-label="Dream Customs timeline">
  <div class="dc-timeline-head">
    <div>
      <span class="dc-section-kicker">Customs timeline</span>
      <h2>Story so far</h2>
      <p>Dream fragments, clerk questions, and pact drafts stay together so the ritual feels easy to follow.</p>
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
    card = session.sealed_pact or session.draft_pact
    state = "sealed" if session.sealed_pact else "draft" if session.draft_pact else "waiting"
    if not card:
        return f"""
<aside class="dc-inspector is-waiting" aria-label="Pact inspector">
  <div class="dc-inspector-kicker">Pact inspector</div>
  <h2>No pact drafted yet</h2>
  <p>Your alliance card will appear here after the clerk has enough dream material. Text-only is enough to begin.</p>
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
<aside class="dc-inspector is-{state}" aria-label="Pact inspector">
  <div class="dc-inspector-kicker">Pact inspector</div>
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
    <h3>Today</h3>
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
  <p><span class="dc-label">Suggestion:</span> {escape(card.practical_suggestion)}</p>
  <p><span class="dc-label">Weird task:</span> {escape(card.weird_task)}</p>
  <p><span class="dc-label">Bedtime release:</span> {escape(card.bedtime_release)}</p>
  <div><span class="dc-label">Contraband:</span><ul>{contraband}</ul></div>
  {safety}
  <span class="dc-seal">SEALED</span>
</section>
""".strip()
