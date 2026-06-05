from html import escape

from dream_customs.schema import PactCard


def render_pact_card(card: PactCard) -> str:
    contraband = "".join(f"<li>{escape(item)}</li>" for item in card.contraband)
    safety = f"<p class='dc-safety'>{escape(card.safety_note)}</p>" if card.safety_note else ""
    return f"""
<style>
  .pact-card {{
    color: #102c3a;
    background: linear-gradient(135deg, #fff8ea 0%, #e8f4ef 100%);
    border: 3px solid #102c3a;
    border-radius: 10px;
    box-shadow: 10px 10px 0 rgba(16, 44, 58, 0.14);
    font-family: Georgia, 'Songti SC', serif;
    line-height: 1.55;
    margin: 8px 0;
    max-width: 860px;
    padding: 24px;
  }}
  .pact-header {{
    align-items: center;
    border-bottom: 2px dashed rgba(16, 44, 58, 0.25);
    display: flex;
    font-weight: 800;
    justify-content: space-between;
    margin-bottom: 16px;
    padding-bottom: 10px;
  }}
  .pact-card h2 {{
    font-size: 32px;
    line-height: 1.1;
    margin: 0 0 4px;
  }}
  .pact-card h3 {{
    color: #e85d4f;
    font-size: 24px;
    margin: 0 0 18px;
  }}
  .dc-label {{
    color: #36545c;
    font-weight: 800;
  }}
  .dc-seal {{
    border: 3px solid #e85d4f;
    border-radius: 999px;
    color: #e85d4f;
    display: inline-block;
    font-weight: 900;
    margin-top: 12px;
    padding: 8px 14px;
    transform: rotate(-4deg);
  }}
  .dc-safety {{
    background: rgba(232, 93, 79, 0.11);
    border-left: 4px solid #e85d4f;
    padding: 10px 12px;
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
