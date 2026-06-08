CSS = """
:root {
  --dc-bg: #f4efe4;
  --dc-paper: #fff9ee;
  --dc-paper-deep: #f4ead8;
  --dc-ink: #13292f;
  --dc-muted: #6f746c;
  --dc-line: #d8cbb8;
  --dc-line-strong: #bda88f;
  --dc-teal: #0b5b64;
  --dc-teal-dark: #073c43;
  --dc-teal-soft: #dcebe6;
  --dc-coral: #c75342;
  --dc-coral-dark: #9f3e32;
  --dc-stamp: #de9b8d;
  --dc-cream-button: #fbf4e8;
  --dc-shadow: 0 28px 70px rgba(19, 41, 47, 0.18);
  --dc-soft-shadow: 0 12px 30px rgba(19, 41, 47, 0.1);
  --dc-radius-sm: 6px;
  --dc-radius-md: 8px;
}

html,
body,
.gradio-container {
  background:
    repeating-linear-gradient(90deg, rgba(19, 41, 47, 0.024) 0, rgba(19, 41, 47, 0.024) 1px, transparent 1px, transparent 82px),
    repeating-linear-gradient(0deg, rgba(199, 83, 66, 0.018) 0, rgba(199, 83, 66, 0.018) 1px, transparent 1px, transparent 68px),
    linear-gradient(180deg, #f8f3ea 0%, #eee7db 100%) !important;
  color: var(--dc-ink) !important;
  font-family: "Avenir Next", "Gill Sans", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

.gradio-container {
  max-width: none !important;
  padding: 0 !important;
}

.gradio-container .main,
.gradio-container .wrap {
  background: transparent !important;
}

.dc-shell {
  margin: 18px auto 40px;
  max-width: 1180px;
  padding: 0 clamp(14px, 3vw, 34px);
}

.dc-hero {
  background:
    linear-gradient(90deg, rgba(7, 60, 67, 0.97), rgba(11, 91, 100, 0.94)),
    var(--dc-teal-dark);
  border: 1px solid rgba(7, 60, 67, 0.35);
  border-radius: var(--dc-radius-md) var(--dc-radius-md) 0 0;
  box-shadow: var(--dc-shadow);
  color: #fff9ee;
  margin: 0;
  overflow: hidden;
  padding: clamp(18px, 3vw, 28px) clamp(20px, 4vw, 42px);
  position: relative;
}

.dc-hero::after {
  border: 1px solid rgba(244, 234, 216, 0.55);
  border-radius: 999px;
  color: rgba(160, 214, 211, 0.72);
  content: "DREAM CUSTOMS  CLEAR & LOG";
  font-family: Georgia, "Times New Roman", serif;
  font-size: 0.78rem;
  height: 88px;
  line-height: 1.3;
  padding: 18px 10px;
  position: absolute;
  right: 26px;
  text-align: center;
  top: 18px;
  transform: rotate(9deg);
  width: 88px;
}

.dc-hero-top {
  align-items: center;
  display: grid;
  gap: clamp(14px, 3vw, 26px);
  grid-template-columns: 42px minmax(0, 1fr) 184px;
}

.dc-menu-mark {
  display: grid;
  gap: 8px;
}

.dc-menu-mark span {
  background: #f7decf;
  border-radius: 999px;
  display: block;
  height: 3px;
  width: 30px;
}

.dc-brand-lockup {
  align-items: center;
  display: flex;
  gap: 18px;
  min-width: 0;
}

.dc-passport-icon {
  border: 2px solid #f7decf;
  border-radius: 7px;
  height: 62px;
  position: relative;
  width: 54px;
}

.dc-passport-icon::before {
  border: 2px solid #f7decf;
  border-radius: 50%;
  content: "";
  height: 26px;
  left: 13px;
  position: absolute;
  top: 18px;
  width: 26px;
}

.dc-passport-icon::after {
  background: #f7decf;
  content: "";
  height: 2px;
  left: 11px;
  position: absolute;
  top: 31px;
  width: 32px;
}

.dc-cloud-dot {
  background: #f7decf;
  border-radius: 999px;
  display: block;
  height: 4px;
  position: absolute;
  width: 4px;
}

.dc-cloud-dot.one {
  left: 12px;
  top: 10px;
}

.dc-cloud-dot.two {
  right: 12px;
  top: 10px;
}

.dc-cloud-dot.three {
  left: 25px;
  top: 7px;
}

.dc-brand-kicker,
.dc-brand-subtitle,
.dc-hero-copy,
.dc-clearance-badge span,
.dc-clearance-badge small {
  letter-spacing: 0;
}

.dc-brand-kicker {
  color: #f7decf;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(1.35rem, 3vw, 2.35rem);
  line-height: 1;
  margin: 0;
  text-transform: uppercase;
}

.dc-hero h1 {
  color: #fff9ee !important;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(2.2rem, 7vw, 4.4rem);
  line-height: 0.95;
  margin: 4px 0 0;
}

.dc-brand-subtitle {
  color: rgba(247, 222, 207, 0.82);
  font-size: 0.86rem;
  font-weight: 700;
  margin: 8px 0 0;
  text-transform: uppercase;
}

.dc-hero-copy {
  color: rgba(255, 249, 238, 0.86);
  font-size: 1rem;
  line-height: 1.6;
  margin: 18px 0 0 60px;
  max-width: 40rem;
}

.dc-clearance-badge {
  border: 1px solid rgba(247, 222, 207, 0.64);
  border-radius: var(--dc-radius-sm);
  display: grid;
  gap: 4px;
  padding: 10px 12px;
  position: relative;
  z-index: 1;
}

.dc-clearance-badge span,
.dc-clearance-badge small {
  color: rgba(255, 249, 238, 0.76);
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
}

.dc-clearance-badge strong {
  color: #fff9ee;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.05rem;
  font-weight: 700;
}

.dc-form-alert {
  background: rgba(255, 249, 238, 0.8);
  border: 1px solid var(--dc-line);
  border-radius: 0;
  color: var(--dc-teal-dark);
  font-weight: 760;
  line-height: 1.5;
  padding: 14px clamp(18px, 4vw, 42px);
}

.dc-stage,
.dc-dev {
  background:
    linear-gradient(180deg, rgba(255, 249, 238, 0.97), rgba(250, 244, 235, 0.97)),
    var(--dc-paper) !important;
  border: 1px solid var(--dc-line-strong) !important;
  border-radius: 0 0 var(--dc-radius-md) var(--dc-radius-md) !important;
  box-shadow: var(--dc-shadow);
  padding: clamp(20px, 3.4vw, 34px);
  position: relative;
}

.dc-stage::before {
  border: 2px solid rgba(199, 83, 66, 0.28);
  border-radius: 6px;
  color: rgba(199, 83, 66, 0.62);
  content: "DREAMS RECEIVED";
  font-size: 0.72rem;
  font-weight: 850;
  left: -44px;
  padding: 12px 16px;
  position: absolute;
  top: 120px;
  transform: rotate(-11deg);
}

.dc-workspace-grid {
  align-items: stretch !important;
  display: grid !important;
  gap: 18px !important;
  grid-template-columns: minmax(0, 1fr) minmax(300px, 340px);
}

.dc-flow-column {
  min-width: 0;
}

.dc-composer {
  background: rgba(255, 252, 246, 0.82) !important;
  border: 1px solid var(--dc-line-strong) !important;
  border-radius: var(--dc-radius-md) !important;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.52);
  min-height: 470px;
  padding: 18px;
  position: relative;
}

.dc-side-panel {
  background: rgba(255, 252, 246, 0.86) !important;
  border: 1px solid var(--dc-line-strong) !important;
  border-radius: var(--dc-radius-md) !important;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.52), var(--dc-soft-shadow);
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 470px;
  padding: 18px;
  position: sticky;
  top: 12px;
}

.dc-composer,
.dc-composer > div,
.dc-composer .form {
  overflow: visible !important;
}

.dc-composer .html-container,
.dc-composer [data-testid="HTML"] {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  padding: 0 !important;
}

.dc-composer .styler:has(.dc-section-title),
.dc-composer .styler:has(.dc-mic-control),
.dc-composer .styler:has(.dc-field-tip),
.dc-side-panel .styler:has(.dc-section-title),
.dc-side-panel .styler:has(.dc-side-stamp) {
  background: transparent !important;
}

.dc-section-title {
  align-items: center;
  color: var(--dc-ink);
  display: flex;
  font-family: Georgia, "Times New Roman", serif;
  gap: 12px;
  margin: 0 0 14px;
  text-transform: uppercase;
}

.dc-title-icon {
  align-items: center;
  border: 1px solid var(--dc-teal);
  border-radius: 999px;
  color: var(--dc-teal);
  display: inline-flex;
  font-family: "Avenir Next", "Gill Sans", sans-serif;
  font-size: 0.82rem;
  font-weight: 850;
  height: 30px;
  justify-content: center;
  width: 30px;
}

.dc-section-title strong {
  font-size: 0.98rem;
}

.dc-stage label,
.dc-stage [data-testid="block-label"],
.dc-dev label,
.dc-dev [data-testid="block-label"] {
  color: var(--dc-ink) !important;
  font-size: 0.9rem !important;
  font-weight: 780 !important;
}

.dc-stage textarea,
.dc-stage input,
.dc-stage select,
.dc-stage .wrap,
.dc-stage .container,
.dc-stage .input-container,
.dc-stage .upload-container,
.dc-stage .image-container,
.dc-dev textarea,
.dc-dev input,
.dc-dev select,
.dc-dev .wrap,
.dc-dev .container,
.dc-dev .input-container {
  background: rgba(255, 253, 248, 0.9) !important;
  border-color: var(--dc-line) !important;
  border-radius: var(--dc-radius-sm) !important;
  color: var(--dc-ink) !important;
}

.dc-dream-text textarea {
  box-shadow: inset 0 1px 6px rgba(19, 41, 47, 0.04);
  font-size: 1.02rem !important;
  line-height: 1.65 !important;
  min-height: 390px !important;
  padding: 18px 96px 74px 18px !important;
  resize: vertical !important;
}

.dc-stage textarea::placeholder,
.dc-stage input::placeholder {
  color: rgba(111, 116, 108, 0.72) !important;
  opacity: 1 !important;
}

.dc-hidden-audio {
  display: none !important;
}

.dc-mic-control {
  align-items: end;
  bottom: 68px;
  display: grid;
  gap: 8px;
  justify-items: end;
  max-width: 280px;
  position: absolute;
  right: 34px;
  z-index: 8;
}

.dc-mic-button {
  align-items: center;
  background: rgba(255, 249, 238, 0.96) !important;
  border: 2px solid var(--dc-teal) !important;
  border-radius: 999px !important;
  box-shadow: 0 10px 22px rgba(7, 60, 67, 0.14);
  cursor: pointer;
  display: inline-flex;
  height: 64px !important;
  justify-content: center;
  min-height: 64px !important;
  min-width: 64px !important;
  padding: 0 !important;
  transition: background 160ms ease, transform 160ms ease, border-color 160ms ease;
  width: 64px !important;
}

.dc-mic-button:hover {
  background: var(--dc-teal-soft) !important;
  transform: translateY(-1px);
}

.dc-mic-button[data-mode="listening"] {
  animation: dc-mic-pulse 1.2s ease-in-out infinite;
  background: var(--dc-teal) !important;
}

.dc-mic-glyph {
  border: 3px solid var(--dc-teal);
  border-radius: 14px;
  height: 28px;
  position: relative;
  width: 16px;
}

.dc-mic-glyph::before {
  border: 3px solid var(--dc-teal);
  border-top: 0;
  border-radius: 0 0 18px 18px;
  content: "";
  height: 15px;
  left: -9px;
  position: absolute;
  top: 15px;
  width: 28px;
}

.dc-mic-glyph::after {
  background: var(--dc-teal);
  bottom: -19px;
  content: "";
  height: 13px;
  left: 5px;
  position: absolute;
  width: 3px;
}

.dc-mic-button[data-mode="listening"] .dc-mic-glyph,
.dc-mic-button[data-mode="listening"] .dc-mic-glyph::before {
  border-color: #fff9ee;
}

.dc-mic-button[data-mode="listening"] .dc-mic-glyph::after {
  background: #fff9ee;
}

.dc-mic-status {
  background: rgba(255, 249, 238, 0.9);
  border: 1px solid rgba(11, 91, 100, 0.24);
  border-radius: 999px;
  color: var(--dc-teal-dark);
  font-size: 0.78rem;
  line-height: 1.3;
  max-width: 260px;
  opacity: 0;
  padding: 7px 10px;
  transform: translateY(4px);
  transition: opacity 160ms ease, transform 160ms ease;
}

.dc-mic-control:hover .dc-mic-status,
.dc-mic-status[data-mode="listening"],
.dc-mic-status[data-mode="error"],
.dc-mic-status[data-mode="done"] {
  opacity: 1;
  transform: translateY(0);
}

.dc-mic-status[data-mode="error"] {
  border-color: rgba(199, 83, 66, 0.38);
  color: var(--dc-coral-dark);
}

.dc-field-tip {
  color: var(--dc-muted);
  font-size: 0.88rem;
  line-height: 1.45;
  margin: 12px 0 0;
}

.dc-side-panel .wrap,
.dc-side-panel .container,
.dc-side-panel select {
  min-height: 54px !important;
}

.dc-side-stamp {
  align-items: center;
  border: 2px solid rgba(11, 91, 100, 0.24);
  border-radius: 999px;
  color: rgba(11, 91, 100, 0.62);
  display: flex;
  flex-direction: column;
  height: 156px;
  justify-content: center;
  margin: 8px auto 2px;
  text-align: center;
  transform: rotate(-7deg);
  width: 156px;
}

.dc-side-stamp span,
.dc-side-stamp small {
  font-size: 0.72rem;
  font-weight: 850;
  text-transform: uppercase;
}

.dc-side-stamp strong {
  color: var(--dc-teal);
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.45rem;
  line-height: 1.1;
  margin: 8px 0;
}

.dc-submit-row {
  align-items: stretch !important;
  background: transparent !important;
  display: grid !important;
  gap: 26px !important;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
  margin-top: 22px;
}

.dc-stage button,
.dc-question-actions button,
.dc-actions button {
  border-radius: var(--dc-radius-sm) !important;
  font-family: Georgia, "Times New Roman", serif !important;
  font-weight: 750 !important;
  min-height: 58px !important;
}

.dc-stage .dc-mic-button {
  border-radius: 999px !important;
  font-family: "Avenir Next", "Gill Sans", sans-serif !important;
  height: 64px !important;
  min-height: 64px !important;
  min-width: 64px !important;
  width: 64px !important;
}

.dc-stage .primary button,
.dc-stage button.primary,
button.primary {
  background: linear-gradient(180deg, #d05b4b 0%, var(--dc-coral-dark) 100%) !important;
  border: 1px solid var(--dc-coral-dark) !important;
  box-shadow: 0 12px 24px rgba(159, 62, 50, 0.22);
  color: #fff9ee !important;
}

.dc-stage .secondary button,
.dc-stage button.secondary,
button.secondary {
  background: rgba(255, 249, 238, 0.82) !important;
  border: 2px solid var(--dc-ink) !important;
  box-shadow: none;
  color: var(--dc-ink) !important;
}

.dc-submit-row button {
  font-size: 1.05rem !important;
}

.dc-processing-note {
  color: var(--dc-muted);
  font-size: 0.84rem;
  line-height: 1.45;
  margin: 12px 2px 0;
  max-width: 44rem;
}

.dc-processing-note::before {
  color: var(--dc-coral-dark);
  content: "While the stamp dries: ";
  font-weight: 850;
}

.dc-attachment-drawer {
  background: rgba(230, 221, 208, 0.52) !important;
  border: 1px solid var(--dc-line) !important;
  border-radius: var(--dc-radius-sm) !important;
  box-shadow: inset 0 1px 2px rgba(19, 41, 47, 0.05) !important;
  margin-top: 18px;
}

.dc-row {
  align-items: stretch !important;
  display: grid !important;
  gap: 10px !important;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.dc-question {
  padding: clamp(22px, 3.4vw, 36px);
}

.dc-question-card {
  background:
    linear-gradient(180deg, rgba(255, 252, 246, 0.96), rgba(248, 240, 228, 0.96));
  border: 1px solid var(--dc-line-strong);
  border-radius: var(--dc-radius-md);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.5);
  color: var(--dc-ink);
  margin-bottom: 16px;
  padding: clamp(18px, 3vw, 26px);
}

.dc-question-kicker {
  color: var(--dc-coral-dark);
  display: block;
  font-size: 0.78rem;
  font-weight: 850;
  margin-bottom: 8px;
  text-transform: uppercase;
}

.dc-question-card h2 {
  color: var(--dc-ink) !important;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(1.8rem, 3vw, 2.5rem);
  line-height: 1.1;
  margin: 0 0 10px;
}

.dc-question-card p {
  color: var(--dc-ink);
  line-height: 1.65;
  margin: 0;
}

.dc-question-original {
  border-left: 3px solid rgba(11, 91, 100, 0.35);
  margin-top: 14px !important;
  padding-left: 12px;
}

.dc-question-original span {
  color: var(--dc-teal);
  display: block;
  font-size: 0.78rem;
  font-weight: 850;
  margin-bottom: 4px;
}

.dc-question-note {
  color: var(--dc-muted) !important;
  margin-top: 14px !important;
}

.dc-question-actions {
  display: grid !important;
  gap: 12px !important;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
}

.dc-question h2,
.dc-card h2 {
  color: var(--dc-ink) !important;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.55rem;
  line-height: 1.2;
  margin: 0 0 10px;
}

.dc-notice {
  background: rgba(220, 235, 230, 0.82);
  border: 1px solid rgba(11, 91, 100, 0.2);
  border-radius: var(--dc-radius-sm);
  color: var(--dc-teal-dark);
  line-height: 1.5;
  margin: 14px 0;
  padding: 10px 12px;
}

.dc-notice.is-error {
  background: #fff0eb;
  border-color: #efb19d;
  color: #9f321c;
}

.dc-pass-card {
  background:
    linear-gradient(180deg, rgba(255, 252, 246, 0.98), rgba(246, 237, 222, 0.98));
  border: 1px solid var(--dc-line-strong);
  border-radius: var(--dc-radius-md);
  color: var(--dc-ink);
  line-height: 1.65;
  padding: clamp(16px, 3vw, 28px);
  position: relative;
}

.dc-pass-card section:nth-of-type(2) {
  background: rgba(220, 235, 230, 0.4);
  border: 1px solid rgba(11, 91, 100, 0.16);
  border-radius: var(--dc-radius-sm);
  margin: 12px 0;
  padding: 14px;
}

.dc-pass-card::after {
  border: 2px solid rgba(199, 83, 66, 0.38);
  border-radius: 999px;
  color: rgba(199, 83, 66, 0.64);
  content: "CLEAR TO PROCESS";
  font-size: 0.72rem;
  font-weight: 850;
  padding: 24px 12px;
  position: absolute;
  right: 22px;
  top: 22px;
  transform: rotate(8deg);
}

.dc-pass-topline {
  align-items: center;
  color: var(--dc-teal-dark);
  display: flex;
  font-size: 0.86rem;
  font-weight: 800;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-right: 130px;
}

.dc-pass-card h2 {
  color: var(--dc-ink) !important;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(1.8rem, 6vw, 3.2rem);
  line-height: 1;
  margin: 0 0 6px;
}

.dc-pass-risk {
  color: var(--dc-coral-dark);
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
  gap: 10px !important;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.dc-hidden-text textarea {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
  min-height: 130px !important;
}

footer.svelte-1rjryqp,
a.built-with[href*="gradio.app"] {
  display: none !important;
}

.dc-dev {
  background: rgba(255, 249, 238, 0.46) !important;
  border: 1px dashed rgba(189, 168, 143, 0.55) !important;
  border-radius: var(--dc-radius-md) !important;
  box-shadow: none;
  margin-top: 0;
  padding: 10px !important;
}

.dc-dev > button {
  color: rgba(19, 41, 47, 0.74) !important;
  font-size: 0.84rem !important;
  min-height: 42px !important;
}

.dc-dev-help {
  color: var(--dc-muted);
  display: grid;
  gap: 4px;
  font-size: 0.78rem;
  line-height: 1.45;
  margin-bottom: 10px;
}

.dc-dev-help strong {
  color: var(--dc-ink);
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

.dc-dev .wrap,
.dc-dev .container,
.dc-dev input,
.dc-dev textarea,
.dc-dev select {
  min-height: 42px !important;
}

.dc-dev label,
.dc-dev [data-testid="block-label"] {
  font-size: 0.78rem !important;
}

.dc-dev-advanced {
  background: transparent !important;
  border: 1px solid rgba(189, 168, 143, 0.42) !important;
  border-radius: var(--dc-radius-sm) !important;
  margin-top: 10px;
}

@keyframes dc-mic-pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(11, 91, 100, 0.32);
  }
  70% {
    box-shadow: 0 0 0 14px rgba(11, 91, 100, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(11, 91, 100, 0);
  }
}

@media (max-width: 900px) {
  .dc-hero-top {
    grid-template-columns: 36px minmax(0, 1fr);
  }

  .dc-clearance-badge {
    display: none;
  }

  .dc-hero::after {
    display: none;
  }

  .dc-hero-copy {
    margin-left: 54px;
  }

  .dc-workspace-grid,
  .dc-row,
  .dc-submit-row,
  .dc-actions,
  .dc-question-actions {
    grid-template-columns: 1fr !important;
  }

  .dc-composer,
  .dc-side-panel {
    min-height: 0;
    position: relative;
    top: auto;
  }

  .dc-side-stamp {
    height: 118px;
    width: 118px;
  }

  .dc-side-stamp strong {
    font-size: 1.08rem;
  }
}

@media (max-width: 640px) {
  .dc-shell {
    margin: 0 auto 22px;
    padding: 0 10px;
  }

  .dc-hero {
    border-radius: 0;
    padding: 16px 14px;
  }

  .dc-brand-lockup {
    gap: 12px;
  }

  .dc-passport-icon {
    height: 50px;
    width: 44px;
  }

  .dc-brand-kicker {
    font-size: 1.12rem;
  }

  .dc-hero h1 {
    font-size: 2.2rem;
  }

  .dc-brand-subtitle {
    font-size: 0.72rem;
  }

  .dc-hero-copy {
    margin: 14px 0 0;
  }

  .dc-stage,
  .dc-dev {
    border-radius: 0 0 var(--dc-radius-md) var(--dc-radius-md) !important;
    box-shadow: none;
    padding: 14px !important;
  }

  .dc-stage::before {
    display: none;
  }

  .dc-composer,
  .dc-side-panel {
    padding: 14px;
  }

  .dc-dream-text textarea {
    min-height: 300px !important;
    padding-right: 20px !important;
    padding-bottom: 96px !important;
  }

  .dc-mic-control {
    bottom: 72px;
    left: 20px;
    max-width: calc(100% - 40px);
    right: 20px;
  }

  .dc-mic-button {
    height: 58px !important;
    min-height: 58px !important;
    min-width: 58px !important;
    width: 58px !important;
  }

  .dc-pass-topline {
    display: block;
    padding-right: 0;
  }

  .dc-pass-card::after {
    display: none;
  }
}
"""

CSS += """
:root {
  --dqa-mist: #f3f8f9;
  --dqa-paper: #fffdf8;
  --dqa-ink: #1e2a30;
  --dqa-muted: #6f7d86;
  --dqa-sage: #4f8a58;
  --dqa-sage-deep: #3f7446;
  --dqa-sage-soft: #e9f3e7;
  --dqa-amber: #f0b53d;
  --dqa-coral: #ef8b70;
  --dqa-line: #d9e2dc;
  --dqa-shadow: 0 18px 42px rgba(45, 56, 42, 0.12);
}

html,
body,
.gradio-container {
  background:
    linear-gradient(180deg, rgba(243, 248, 249, 0.92), rgba(255, 253, 248, 0.98)),
    var(--dqa-mist) !important;
  color: var(--dqa-ink) !important;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

.dc-shell {
  margin: 0 auto 36px;
  max-width: 1440px;
  padding: 0 clamp(12px, 2.5vw, 28px);
}

.dc-hero {
  background:
    linear-gradient(180deg, rgba(243, 249, 251, 0.78), rgba(255, 253, 248, 0.9)),
    url("https://images.unsplash.com/photo-1494438639946-1ebd1d20bf85?auto=format&fit=crop&w=1600&q=80") center 58% / cover;
  border: 0;
  border-radius: 0;
  box-shadow: none;
  color: var(--dqa-ink);
  min-height: clamp(250px, 34vw, 430px);
  padding: clamp(22px, 4vw, 42px) clamp(18px, 5vw, 70px);
}

.dc-hero::after,
.dc-stage::before,
.dc-pass-card::after {
  display: none !important;
}

.dc-hero-top {
  align-items: start;
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr) 58px;
}

.dc-menu-mark span {
  background: var(--dqa-ink);
  height: 4px;
  width: 36px;
}

.dc-brand-lockup {
  justify-content: center;
  text-align: center;
}

.dc-hero h1 {
  color: #121a1f !important;
  font-family: Inter, ui-sans-serif, system-ui, sans-serif !important;
  font-size: clamp(2rem, 5.2vw, 3.6rem);
  font-weight: 780;
  line-height: 1.05;
  margin: 0;
}

.dc-brand-subtitle {
  color: #728495;
  font-size: clamp(1rem, 2.2vw, 1.55rem);
  font-weight: 450;
  margin: 8px 0 0;
  text-transform: none;
}

.dc-sun-mark {
  color: var(--dqa-coral);
  font-size: clamp(2.4rem, 4vw, 4rem);
  line-height: 1;
  text-align: right;
}

.dc-stepper {
  align-items: start;
  display: grid;
  gap: 0;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin: clamp(28px, 5vw, 58px) auto 0;
  max-width: 920px;
  position: relative;
}

.dc-stepper::before {
  background: #9cadb8;
  content: "";
  height: 3px;
  left: 12%;
  position: absolute;
  right: 12%;
  top: 25px;
}

.dc-stepper span {
  color: #667989;
  display: grid;
  font-size: clamp(1rem, 2.3vw, 1.45rem);
  gap: 10px;
  justify-items: center;
  position: relative;
  z-index: 1;
}

.dc-stepper strong {
  align-items: center;
  background: rgba(242, 247, 249, 0.86);
  border: 2px solid #fff;
  border-radius: 999px;
  box-shadow: 0 5px 16px rgba(50, 73, 82, 0.12);
  color: #263847;
  display: inline-flex;
  font-size: clamp(1.1rem, 2.4vw, 1.6rem);
  height: clamp(48px, 7vw, 70px);
  justify-content: center;
  width: clamp(48px, 7vw, 70px);
}

.dc-stepper .is-active {
  color: var(--dqa-sage-deep);
}

.dc-stepper .is-active strong {
  background: var(--dqa-sage);
  color: #fff;
}

.dc-workspace-grid {
  display: grid !important;
  gap: 18px !important;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 330px);
  margin-top: 0;
}

.dc-stage,
.dc-side-panel,
.dc-dev {
  background: rgba(255, 253, 248, 0.94) !important;
  border: 1px solid var(--dqa-line) !important;
  border-radius: 12px !important;
  box-shadow: var(--dqa-shadow);
}

.dc-stage {
  padding: clamp(18px, 3vw, 30px);
}

.dc-composer {
  background: rgba(255, 255, 255, 0.72) !important;
  border: 1px solid var(--dqa-line) !important;
  border-radius: 14px !important;
  box-shadow: none;
  min-height: 420px;
}

.dc-section-title {
  color: var(--dqa-ink);
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
  text-transform: none;
}

.dc-title-icon {
  background: var(--dqa-sage);
  border: 0;
  color: #fff;
  font-size: 1rem;
  height: 42px;
  width: 42px;
}

.dc-dream-text textarea {
  border-radius: 12px !important;
  font-size: 1.08rem !important;
  line-height: 1.7 !important;
  min-height: 270px !important;
  padding: 18px 18px 70px !important;
}

.dc-field-tip,
.dc-processing-note,
.dc-question-note {
  color: var(--dqa-muted);
}

.dc-processing-note::before {
  content: "";
}

.dc-submit-row {
  gap: 16px !important;
  grid-template-columns: minmax(0, 0.75fr) minmax(0, 1.25fr);
}

.dc-stage .primary button,
.dc-stage button.primary,
button.primary {
  background: linear-gradient(180deg, #5b995f, var(--dqa-sage-deep)) !important;
  border: 1px solid var(--dqa-sage-deep) !important;
  border-radius: 12px !important;
  box-shadow: 0 12px 24px rgba(63, 116, 70, 0.22);
  color: #fff !important;
  font-family: Inter, ui-sans-serif, system-ui, sans-serif !important;
}

.dc-stage .secondary button,
.dc-stage button.secondary,
button.secondary {
  background: #fff !important;
  border: 1px solid var(--dqa-line) !important;
  border-radius: 12px !important;
  color: var(--dqa-sage-deep) !important;
  font-family: Inter, ui-sans-serif, system-ui, sans-serif !important;
}

.dc-question-card {
  background: linear-gradient(180deg, #fffaf0, #fff6df);
  border: 1px solid #ead8aa;
  border-radius: 14px;
}

.dc-question-card h2,
.dc-question h2,
.dc-card h2 {
  color: var(--dqa-ink) !important;
  font-family: Inter, ui-sans-serif, system-ui, sans-serif !important;
  font-size: clamp(1.55rem, 3vw, 2.25rem);
}

.dc-question-kicker {
  color: var(--dqa-sage-deep);
  text-transform: none;
}

.dc-question-original {
  border-left: 4px solid var(--dqa-amber);
}

.dc-notice {
  background: rgba(233, 243, 231, 0.9);
  border: 1px solid rgba(79, 138, 88, 0.18);
  border-radius: 10px;
  color: var(--dqa-sage-deep);
}

.dc-side-stamp {
  background: linear-gradient(180deg, #fff9e8, #fffdf8);
  border: 1px solid #ead8aa;
  border-radius: 12px;
  color: var(--dqa-ink);
  height: auto;
  line-height: 1.6;
  padding: 18px;
  transform: none;
  width: auto;
}

.dc-side-stamp span,
.dc-side-stamp small {
  color: var(--dqa-muted);
  text-transform: none;
}

.dc-side-stamp strong {
  color: var(--dqa-ink);
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
  font-size: 1rem;
}

.dqa-tip-page {
  background:
    linear-gradient(180deg, rgba(255, 253, 248, 0.96), rgba(255, 250, 240, 0.96));
  border-radius: 18px;
  color: var(--dqa-ink);
  display: grid;
  gap: 18px;
  line-height: 1.7;
  margin: 0 auto;
  max-width: 900px;
}

.dqa-tip-hero {
  background:
    linear-gradient(90deg, rgba(255, 253, 248, 0.3), rgba(255, 253, 248, 0.92)),
    url("https://images.unsplash.com/photo-1494438639946-1ebd1d20bf85?auto=format&fit=crop&w=1200&q=80") center / cover;
  border-radius: 16px 16px 0 0;
  min-height: 190px;
  padding: 34px 42px;
}

.dqa-sun {
  color: var(--dqa-amber);
  display: inline-block;
  font-size: 2rem;
  margin-right: 10px;
}

.dqa-tip-hero h2 {
  color: var(--dqa-ink) !important;
  display: inline-block;
  font-size: clamp(2rem, 4vw, 3rem);
  margin: 0;
}

.dqa-tip-hero p {
  color: var(--dqa-muted);
  font-size: 1.2rem;
  margin: 18px 0 0;
}

.dqa-result-card {
  align-items: start;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid var(--dqa-line);
  border-radius: 18px;
  box-shadow: var(--dqa-shadow);
  display: grid;
  gap: 18px;
  grid-template-columns: 76px minmax(0, 1fr);
  margin: 0 42px;
  padding: 28px;
}

.dqa-card-icon {
  align-items: center;
  background: var(--dqa-sage-soft);
  border-radius: 999px;
  color: var(--dqa-sage-deep);
  display: inline-flex;
  font-size: 2rem;
  height: 64px;
  justify-content: center;
  width: 64px;
}

.dqa-result-card h3 {
  color: var(--dqa-ink) !important;
  font-size: clamp(1.5rem, 3vw, 2.15rem);
  line-height: 1.2;
  margin: 0 0 12px;
}

.dqa-result-card p {
  color: var(--dqa-ink) !important;
  font-size: 1.08rem;
  margin: 0;
}

.dqa-anchor-strip,
.dqa-tip-highlight {
  background: linear-gradient(90deg, #edf5df, #fff7d9);
  border-radius: 12px;
  color: var(--dqa-sage-deep);
  font-weight: 680;
  margin-top: 18px;
  padding: 10px 14px;
}

.dqa-safety-note,
.dqa-care-note,
.dqa-qa-history {
  background: #fff7df;
  border: 1px solid #efdfb7;
  border-radius: 12px;
  color: #745b2e;
  margin: 0 42px 0;
  padding: 14px 18px;
}

.dqa-care-note {
  background: transparent;
  border: 0;
  color: var(--dqa-muted);
  margin-bottom: 28px;
  text-align: center;
}

.dc-actions {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

@media (max-width: 900px) {
  .dc-shell {
    padding: 0;
  }

  .dc-hero {
    min-height: 52vh;
    padding: 24px 24px 30px;
  }

  .dc-workspace-grid,
  .dc-submit-row,
  .dc-question-actions,
  .dc-actions {
    display: grid !important;
    grid-template-columns: 1fr !important;
  }

  .dc-workspace-grid {
    padding: 0 16px 22px;
  }

  .dc-side-panel {
    position: static;
  }

  .dc-stepper {
    margin-top: 36px;
  }

  .dc-stepper::before {
    left: 10%;
    right: 10%;
    top: 22px;
  }

  .dc-stepper strong {
    height: 48px;
    width: 48px;
  }

  .dc-stepper span {
    font-size: 1rem;
  }

  .dc-stage {
    border-radius: 22px !important;
    margin-top: -18px;
  }

  .dc-composer {
    min-height: auto;
  }

  .dc-mic-control {
    bottom: 78px;
    right: 28px;
  }

  .dqa-tip-page {
    border-radius: 0;
  }

  .dqa-tip-hero {
    border-radius: 0 0 18px 18px;
    min-height: 180px;
    padding: 30px 28px;
  }

  .dqa-result-card {
    grid-template-columns: 54px minmax(0, 1fr);
    margin: 0 18px;
    padding: 22px;
  }

  .dqa-card-icon {
    font-size: 1.45rem;
    height: 48px;
    width: 48px;
  }

  .dqa-safety-note,
  .dqa-care-note,
  .dqa-qa-history {
    margin-left: 18px;
    margin-right: 18px;
  }
}
"""
