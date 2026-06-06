CSS = """
:root {
  --dc-bg: #f6f8f6;
  --dc-ink: #17211f;
  --dc-muted: #5f6f68;
  --dc-line: #cbd7d1;
  --dc-panel: #ffffff;
  --dc-panel-soft: #edf4f0;
  --dc-paper: #fffaf1;
  --dc-graphite: #26302d;
  --dc-teal: #0f766e;
  --dc-teal-dark: #115e59;
  --dc-coral: #c85235;
  --dc-gold: #b7791f;
  --dc-shadow: 0 24px 70px rgba(23, 33, 31, 0.13);
  --dc-soft-shadow: 0 10px 28px rgba(23, 33, 31, 0.08);
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
  max-width: 1060px;
  padding: 28px clamp(18px, 4vw, 46px) 34px;
}

.dc-hero {
  border-bottom: 1px solid var(--dc-line);
  margin-bottom: 20px;
  padding: 4px 0 20px;
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
  padding: clamp(18px, 3vw, 30px);
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

.dc-intake-grid {
  align-items: stretch !important;
  display: grid !important;
  gap: clamp(16px, 3vw, 24px) !important;
  grid-template-columns: minmax(0, 1fr) minmax(210px, 270px);
}

.dc-composer {
  background:
    linear-gradient(180deg, rgba(255, 250, 241, 0.86), rgba(251, 253, 252, 0.98)) !important;
  border: 1px solid color-mix(in srgb, var(--dc-line) 82%, var(--dc-gold)) !important;
  border-radius: var(--dc-radius-md) !important;
  box-shadow: var(--dc-soft-shadow);
  min-height: 300px;
  padding: 12px;
  position: relative;
}

.dc-composer,
.dc-composer > div,
.dc-composer .form {
  overflow: visible !important;
}

.dc-dream-text textarea {
  min-height: 248px !important;
  padding-bottom: 78px !important;
  resize: vertical !important;
}

.dc-mic-input {
  bottom: 16px;
  max-width: 132px;
  min-width: 112px !important;
  position: absolute !important;
  right: 16px;
  z-index: 4;
}

.dc-mic-input label,
.dc-mic-input [data-testid="block-label"] {
  display: none !important;
}

.dc-mic-input,
.dc-mic-input .wrap,
.dc-mic-input .container,
.dc-mic-input .audio-container,
.dc-mic-input .component-wrapper {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  min-height: 46px !important;
}

.dc-mic-input .audio-container,
.dc-mic-input .wrap {
  height: 46px !important;
  overflow: hidden !important;
}

.dc-mic-input button {
  background: var(--dc-graphite) !important;
  border-color: var(--dc-graphite) !important;
  border-radius: var(--dc-radius-sm) !important;
  color: #ffffff !important;
  min-height: 40px !important;
}

.dc-side-panel {
  background: var(--dc-paper) !important;
  border: 1px solid #e3d6bd !important;
  border-radius: var(--dc-radius-md) !important;
  box-shadow: var(--dc-soft-shadow);
  justify-content: space-between;
  min-height: 300px;
  padding: 14px;
}

.dc-side-stamp {
  border: 1px dashed rgba(200, 82, 53, 0.55);
  border-radius: var(--dc-radius-md);
  color: var(--dc-coral);
  margin-top: 12px;
  padding: 14px;
  text-transform: none;
}

.dc-side-stamp span {
  display: block;
  font-size: 0.72rem;
  font-weight: 850;
  margin-bottom: 6px;
}

.dc-side-stamp strong {
  color: var(--dc-graphite);
  display: block;
  font-size: 1.12rem;
}

.dc-attachment-drawer {
  background: transparent !important;
  border: 1px solid var(--dc-line) !important;
  border-radius: var(--dc-radius-md) !important;
  box-shadow: none !important;
  margin-top: 16px;
}

.dc-submit-row {
  align-items: stretch !important;
  background: transparent !important;
  display: grid !important;
  gap: 14px !important;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
  margin-top: 18px;
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
  border-radius: var(--dc-radius-md) !important;
  font-weight: 750 !important;
  min-height: 48px !important;
}

.dc-stage .primary button,
.dc-stage button.primary,
button.primary {
  background: var(--dc-teal) !important;
  border-color: var(--dc-teal-dark) !important;
  color: white !important;
}

.dc-stage button.secondary {
  background: #f3eee3 !important;
  border-color: var(--dc-line) !important;
  color: var(--dc-ink) !important;
}

.dc-submit-row button {
  box-shadow: var(--dc-soft-shadow);
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
  margin-top: 16px;
}

.dc-dev-grid {
  align-items: stretch !important;
  display: grid !important;
  gap: 12px !important;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.dc-dev .form,
.dc-dev .wrap,
.dc-dev .container,
.dc-dev input,
.dc-dev textarea,
.dc-dev select {
  border-radius: var(--dc-radius-sm) !important;
}

.dc-dev textarea {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
  font-size: 0.84rem !important;
}

@media (max-width: 720px) {
  .dc-shell {
    padding: 16px 12px 24px;
  }

  .dc-hero {
    margin-bottom: 10px;
    padding-bottom: 12px;
  }

  .dc-intake-grid,
  .dc-dev-grid,
  .dc-row,
  .dc-submit-row,
  .dc-actions {
    grid-template-columns: 1fr;
  }

  .dc-side-panel {
    min-height: 0;
  }

  .dc-side-stamp {
    display: none;
  }

  .dc-composer {
    min-height: 270px;
  }

  .dc-dream-text textarea {
    min-height: 220px !important;
  }

  .dc-stage,
  .dc-dev {
    border-radius: 8px !important;
    box-shadow: none;
    padding: 14px;
  }
}
"""
