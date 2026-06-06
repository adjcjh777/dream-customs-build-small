CSS = """
:root {
  --dc-bg: #f6f8f6;
  --dc-ink: #17211f;
  --dc-muted: #5f6f68;
  --dc-line: #cbd7d1;
  --dc-panel: #ffffff;
  --dc-panel-soft: #edf4f0;
  --dc-teal: #0f766e;
  --dc-teal-dark: #115e59;
  --dc-coral: #c85235;
  --dc-gold: #b7791f;
  --dc-shadow: 0 18px 42px rgba(23, 33, 31, 0.12);
  --dc-radius-sm: 6px;
  --dc-radius-md: 8px;
}

html,
body,
.gradio-container {
  background:
    linear-gradient(180deg, rgba(15, 118, 110, 0.08), rgba(200, 82, 53, 0.04) 42%, rgba(246, 248, 246, 1)),
    var(--dc-bg) !important;
  color: var(--dc-ink) !important;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

.gradio-container {
  max-width: none !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
}

.dc-shell {
  margin: 0 auto;
  max-width: 920px;
  padding: 22px clamp(14px, 3vw, 34px) 30px;
}

.dc-hero {
  border-bottom: 1px solid var(--dc-line);
  margin-bottom: 16px;
  padding: 4px 0 18px;
}

.dc-hero h1 {
  color: var(--dc-ink) !important;
  font-size: clamp(2rem, 7vw, 4.4rem);
  letter-spacing: 0;
  line-height: 0.98;
  margin: 0;
}

.dc-hero p {
  color: var(--dc-muted);
  font-size: 1.02rem;
  line-height: 1.65;
  margin: 12px 0 0;
  max-width: 40rem;
}

.dc-stage,
.dc-dev {
  background: var(--dc-panel) !important;
  border: 1px solid var(--dc-line) !important;
  border-radius: var(--dc-radius-md) !important;
  box-shadow: var(--dc-shadow);
  padding: clamp(14px, 2.2vw, 22px);
}

.dc-stage textarea,
.dc-stage input,
.dc-stage select,
.dc-stage .wrap,
.dc-stage .container,
.dc-stage .input-container,
.dc-stage .upload-container,
.dc-stage .image-container,
.dc-stage .audio-container {
  background: #fbfdfc !important;
  border-color: var(--dc-line) !important;
  border-radius: var(--dc-radius-sm) !important;
  color: var(--dc-ink) !important;
}

.dc-stage label,
.dc-stage [data-testid="block-label"],
.dc-dev label,
.dc-dev [data-testid="block-label"] {
  color: var(--dc-ink) !important;
  font-weight: 700 !important;
}

.dc-stage textarea::placeholder,
.dc-stage input::placeholder {
  color: #87958f !important;
  opacity: 1 !important;
}

.dc-stage button {
  border-radius: var(--dc-radius-sm) !important;
  font-weight: 750 !important;
  min-height: 44px !important;
}

.dc-stage .primary button,
.dc-stage button.primary,
button.primary {
  background: var(--dc-teal) !important;
  border-color: var(--dc-teal-dark) !important;
  color: white !important;
}

.dc-stage button.secondary {
  background: var(--dc-panel-soft) !important;
  border-color: var(--dc-line) !important;
  color: var(--dc-ink) !important;
}

.dc-row {
  align-items: stretch !important;
  display: grid !important;
  gap: 10px !important;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.dc-question h2,
.dc-card h2 {
  color: var(--dc-ink) !important;
  font-size: 1.55rem;
  letter-spacing: 0;
  line-height: 1.2;
  margin: 0 0 10px;
}

.dc-notice {
  background: #e6f4ef;
  border: 1px solid #b9ddd3;
  border-radius: var(--dc-radius-sm);
  color: var(--dc-teal-dark);
  line-height: 1.5;
  margin: 0 0 12px;
  padding: 10px 12px;
}

.dc-notice.is-error {
  background: #fff0eb;
  border-color: #efb19d;
  color: #9f321c;
}

.dc-pass-card {
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(237, 244, 240, 0.98));
  border: 1px solid var(--dc-line);
  border-left: 6px solid var(--dc-teal);
  border-radius: var(--dc-radius-md);
  color: var(--dc-ink);
  line-height: 1.65;
  padding: clamp(16px, 3vw, 26px);
}

.dc-pass-topline {
  align-items: center;
  color: var(--dc-teal-dark);
  display: flex;
  font-size: 0.86rem;
  font-weight: 800;
  justify-content: space-between;
  margin-bottom: 12px;
}

.dc-pass-card h2 {
  color: var(--dc-ink) !important;
  font-size: clamp(1.8rem, 7vw, 3.2rem);
  letter-spacing: 0;
  line-height: 1;
  margin: 0 0 6px;
}

.dc-pass-risk {
  color: var(--dc-coral);
  font-weight: 750;
  margin: 0 0 16px;
}

.dc-pass-card section {
  border-top: 1px solid var(--dc-line);
  padding: 12px 0;
}

.dc-pass-card h3 {
  color: var(--dc-teal-dark) !important;
  font-size: 0.9rem;
  letter-spacing: 0;
  margin: 0 0 4px;
}

.dc-pass-card p,
.dc-pass-card li {
  color: var(--dc-ink) !important;
  margin: 0;
}

.dc-pass-card ul {
  margin: 0;
  padding-left: 20px;
}

.dc-pass-seal {
  border: 2px solid var(--dc-coral);
  border-radius: 999px;
  color: var(--dc-coral);
  display: inline-block;
  font-weight: 850;
  margin-top: 10px;
  padding: 7px 12px;
  transform: rotate(-3deg);
}

.dc-pass-safety {
  background: #fff0eb;
  border: 1px solid #efb19d !important;
  border-radius: var(--dc-radius-sm);
  margin: 10px 0;
  padding: 12px !important;
}

.dc-actions {
  display: grid !important;
  gap: 8px !important;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.dc-hidden-text textarea {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
  min-height: 130px !important;
}

.dc-dev {
  box-shadow: none;
  margin-top: 12px;
}

.dc-dev textarea {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
  font-size: 0.84rem !important;
}

@media (max-width: 720px) {
  .dc-shell {
    padding: 14px 10px 22px;
  }

  .dc-hero {
    margin-bottom: 10px;
    padding-bottom: 12px;
  }

  .dc-row,
  .dc-actions {
    grid-template-columns: 1fr;
  }

  .dc-stage,
  .dc-dev {
    border-radius: 8px !important;
    box-shadow: none;
    padding: 12px;
  }
}
"""
