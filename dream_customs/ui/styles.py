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
  align-items: start !important;
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

.dc-voice-input {
  display: none !important;
}

.dc-voice-input .wrap,
.dc-voice-input .container,
.dc-voice-input .input-container {
  background: rgba(255, 253, 248, 0.9) !important;
  border-color: var(--dc-line) !important;
  border-radius: var(--dc-radius-sm) !important;
  color: var(--dc-ink) !important;
}

.dc-mic-control {
  align-items: end;
  bottom: 28px;
  display: grid;
  gap: 8px;
  justify-items: end;
  max-width: 280px;
  position: absolute;
  right: 28px;
  z-index: 8;
}

.dc-mic-button {
  align-items: center;
  background: rgba(255, 249, 238, 0.96) !important;
  border: 1px solid rgba(7, 60, 67, 0.26) !important;
  border-radius: 999px !important;
  box-shadow: 0 8px 18px rgba(7, 60, 67, 0.12);
  cursor: pointer;
  display: inline-flex;
  height: 48px !important;
  justify-content: center;
  min-height: 48px !important;
  min-width: 48px !important;
  padding: 0 !important;
  transition: background 160ms ease, transform 160ms ease, border-color 160ms ease;
  width: 48px !important;
}

.dc-mic-button:hover {
  background: var(--dc-teal-soft) !important;
  transform: translateY(-1px);
}

.dc-mic-button[data-mode="recording"],
.dc-mic-button[data-mode="transcribing"],
.dc-mic-button[data-mode="waking"] {
  animation: dc-mic-pulse 1.2s ease-in-out infinite;
  background: var(--dc-teal) !important;
}

.dc-mic-glyph {
  border: 2px solid var(--dc-teal);
  border-radius: 14px;
  height: 22px;
  position: relative;
  width: 13px;
}

.dc-mic-glyph::before {
  border: 2px solid var(--dc-teal);
  border-top: 0;
  border-radius: 0 0 18px 18px;
  content: "";
  height: 12px;
  left: -7px;
  position: absolute;
  top: 13px;
  width: 23px;
}

.dc-mic-glyph::after {
  background: var(--dc-teal);
  bottom: -15px;
  content: "";
  height: 10px;
  left: 4px;
  position: absolute;
  width: 2px;
}

.dc-mic-button[data-mode="recording"] .dc-mic-glyph,
.dc-mic-button[data-mode="recording"] .dc-mic-glyph::before,
.dc-mic-button[data-mode="transcribing"] .dc-mic-glyph,
.dc-mic-button[data-mode="transcribing"] .dc-mic-glyph::before,
.dc-mic-button[data-mode="waking"] .dc-mic-glyph,
.dc-mic-button[data-mode="waking"] .dc-mic-glyph::before {
  border-color: #fff9ee;
}

.dc-mic-button[data-mode="recording"] .dc-mic-glyph::after,
.dc-mic-button[data-mode="transcribing"] .dc-mic-glyph::after,
.dc-mic-button[data-mode="waking"] .dc-mic-glyph::after {
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
.dc-mic-status[data-mode="recording"],
.dc-mic-status[data-mode="transcribing"],
.dc-mic-status[data-mode="waking"],
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

.dc-field-tip.is-error {
  background: rgba(255, 240, 235, 0.95);
  border: 1px solid #efb19d;
  border-radius: 10px;
  color: #9f321c;
  margin-top: 12px;
  padding: 10px 12px;
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
  height: 48px !important;
  min-height: 48px !important;
  min-width: 48px !important;
  width: 48px !important;
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

.dc-processing-note.is-active {
  background: rgba(244, 201, 94, 0.16);
  border: 1px solid rgba(191, 133, 35, 0.28);
  border-radius: 10px;
  color: var(--dc-ink);
  padding: 10px 12px 10px 36px;
  position: relative;
}

.dc-processing-note.is-active::before {
  animation: dc-processing-pulse 1.1s ease-in-out infinite;
  background: var(--dc-sage);
  border-radius: 999px;
  content: "";
  height: 10px;
  left: 14px;
  position: absolute;
  top: 16px;
  width: 10px;
}

@keyframes dc-processing-pulse {
  0%,
  100% {
    opacity: 0.45;
    transform: scale(0.82);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}

.dc-processing-note::before {
  color: var(--dc-coral-dark);
  content: "While the stamp dries: ";
  font-weight: 850;
}

.dc-attachment-drawer {
  background: transparent !important;
  border: 0 !important;
  bottom: 28px;
  box-shadow: none !important;
  left: 28px;
  margin: 0;
  max-width: min(420px, calc(100% - 96px));
  padding: 0 !important;
  position: absolute;
  z-index: 9;
}

.dc-attachment-drawer > button {
  align-items: center !important;
  background: rgba(255, 249, 238, 0.96) !important;
  border: 1px solid rgba(7, 60, 67, 0.26) !important;
  border-radius: 999px !important;
  box-shadow: 0 8px 18px rgba(7, 60, 67, 0.12);
  color: var(--dc-teal-dark) !important;
  display: inline-flex !important;
  font-family: "Avenir Next", "Gill Sans", sans-serif !important;
  font-size: 1.5rem !important;
  height: 48px !important;
  justify-content: center !important;
  line-height: 1 !important;
  min-height: 48px !important;
  padding: 0 !important;
  width: 48px !important;
}

.dc-attachment-drawer > div {
  background: rgba(255, 253, 248, 0.98) !important;
  border: 1px solid var(--dc-line) !important;
  border-radius: var(--dc-radius-md) !important;
  box-shadow: var(--dc-soft-shadow);
  margin-top: 8px;
  padding: 12px !important;
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

.dc-notice.is-processing {
  background: rgba(244, 201, 94, 0.18);
  border-color: rgba(191, 133, 35, 0.32);
  color: var(--dc-ink);
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

.dc-debug-panel {
  background: rgba(255, 253, 248, 0.94) !important;
  border: 1px solid var(--dqa-line, var(--dc-line)) !important;
  border-radius: 12px !important;
  box-shadow: var(--dqa-shadow, var(--dc-soft-shadow));
  margin-top: 18px;
  padding: 10px !important;
}

.dc-flow-column .dc-debug-panel {
  align-self: stretch;
  width: 100%;
}

.dc-debug-panel > button {
  color: var(--dc-ink) !important;
  font-size: 0.92rem !important;
  min-height: 46px !important;
}

.dc-debug-help {
  color: var(--dc-muted);
  display: grid;
  gap: 4px;
  font-size: 0.84rem;
  line-height: 1.5;
  margin-bottom: 10px;
}

.dc-debug-help strong {
  color: var(--dc-ink);
}

.dc-debug-panel textarea,
.dc-debug-panel code,
.dc-debug-panel pre {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
  font-size: 0.82rem !important;
}

.dc-debug-panel,
.dc-debug-panel .block,
.dc-debug-panel .wrap,
.dc-debug-panel .container,
.dc-debug-panel .cm-editor,
.dc-debug-panel .cm-scroller,
.dc-debug-panel .cm-content,
.dc-dev,
.dc-dev .block,
.dc-dev .wrap,
.dc-dev .container,
.dc-dev-advanced,
.dc-dev-advanced .block,
.dc-dev-advanced .wrap,
.dc-dev-advanced .container {
  max-width: 100% !important;
  min-width: 0 !important;
  overflow-x: hidden !important;
}

.dc-debug-panel .cm-scroller,
.dc-debug-panel pre {
  overflow-x: auto !important;
}

.dc-debug-panel .cm-line,
.dc-debug-panel .cm-content,
.dc-debug-panel code,
.dc-debug-panel pre {
  overflow-wrap: anywhere !important;
  white-space: pre-wrap !important;
  word-break: break-word !important;
}

.dc-debug-panel .cm-line {
  max-width: 100% !important;
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
    padding-right: 78px !important;
    padding-bottom: 96px !important;
  }

  .dc-mic-control {
    bottom: 22px;
    left: auto;
    max-width: calc(100% - 112px);
    right: 20px;
  }

  .dc-mic-button {
    height: 48px !important;
    min-height: 48px !important;
    min-width: 48px !important;
    width: 48px !important;
  }

  .dc-attachment-drawer {
    bottom: 22px;
    left: 20px;
    max-width: calc(100% - 96px);
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
.dc-question-original p {
  font-size: clamp(1.16rem, 2.4vw, 1.45rem);
  font-weight: 720;
  line-height: 1.45;
  margin: 4px 0 0 !important;
}

.dc-question-context {
  background: rgba(255, 253, 248, 0.72);
  border: 1px solid rgba(215, 168, 66, 0.22);
  border-radius: 10px;
  margin-top: 12px;
  padding: 10px 12px;
}

.dc-question-context summary {
  color: var(--dqa-sage-deep);
  cursor: pointer;
  font-size: 0.84rem;
  font-weight: 760;
}

.dc-question-context p {
  color: var(--dqa-muted);
  font-size: 0.92rem;
  margin-top: 8px;
}

.dc-stage button.dc-is-loading {
  cursor: progress !important;
  opacity: 0.82;
  pointer-events: none;
}

.dc-stage button.dc-is-loading::after {
  animation: dqa-loading-dot 900ms ease-in-out infinite;
  content: "";
  display: inline-block;
  margin-left: 8px;
}

@keyframes dqa-loading-dot {
  0%,
  100% {
    content: "";
  }
  33% {
    content: ".";
  }
  66% {
    content: "..";
  }
}

@media (max-width: 640px) {
  .dc-hero {
    min-height: 248px !important;
    padding-bottom: 18px !important;
  }

  .dc-stepper {
    margin-top: 18px !important;
  }

  .dc-stepper span {
    flex-basis: 62px !important;
    font-size: 0.82rem !important;
  }

  .dc-stepper strong {
    height: 38px !important;
    width: 38px !important;
  }

  .dc-side-stamp {
    display: none;
  }
}
"""
CSS += """
/* Reference-space polish: soft PawMap spacing, case-file step clarity, paper-note tactility. */
:root {
  --dqa-dawn: #eef6f1;
  --dqa-desk: #f7eddc;
  --dqa-paper-warm: #fffaf0;
  --dqa-pencil: #2c3734;
  --dqa-sage-2: #5f8f68;
  --dqa-rose: #d67b67;
  --dqa-brass: #d7a842;
  --dqa-paper-line: rgba(95, 143, 104, 0.16);
  --dqa-table-shadow: 0 18px 44px rgba(52, 66, 55, 0.14);
  --dqa-paper-shadow: 5px 6px 0 rgba(44, 55, 52, 0.08);
}

html,
body,
.gradio-container {
  background:
    linear-gradient(90deg, rgba(95, 143, 104, 0.045) 0 1px, transparent 1px 80px),
    linear-gradient(180deg, #eef7f2 0%, #fffaf0 45%, #f6ead8 100%) !important;
}

.dc-shell {
  max-width: 1320px;
}

.dc-hero {
  background:
    linear-gradient(180deg, rgba(247, 251, 246, 0.84), rgba(255, 250, 240, 0.96)),
    url("https://images.unsplash.com/photo-1494438639946-1ebd1d20bf85?auto=format&fit=crop&w=1600&q=80") center 55% / cover !important;
  border-bottom: 1px solid rgba(95, 143, 104, 0.18);
  min-height: clamp(280px, 36vw, 460px);
  padding-bottom: clamp(30px, 5vw, 58px);
}

.dc-hero-top {
  align-items: start;
}

.dc-hero-ribbon {
  align-items: center;
  background: rgba(255, 250, 240, 0.86);
  border: 1px solid rgba(95, 143, 104, 0.22);
  border-radius: 8px;
  box-shadow: 3px 4px 0 rgba(44, 55, 52, 0.07);
  color: var(--dqa-pencil);
  display: inline-flex;
  gap: 12px;
  justify-self: center;
  margin-top: 8px;
  max-width: min(100%, 680px);
  padding: 9px 12px;
}

.dc-hero-ribbon span {
  color: var(--dqa-sage-deep);
  font-size: 0.84rem;
  font-weight: 780;
}

.dc-hero-ribbon small {
  color: #65746e;
  font-size: 0.82rem;
  font-weight: 650;
}

.dc-workspace-grid {
  gap: 20px !important;
  grid-template-columns: minmax(0, 1fr) minmax(288px, 334px) !important;
  margin-top: -20px;
}

.dc-stage,
.dc-side-panel,
.dc-debug-panel {
  border-radius: 8px !important;
  box-shadow: var(--dqa-table-shadow);
}

.dc-stage {
  background:
    linear-gradient(180deg, rgba(255, 252, 246, 0.98), rgba(250, 241, 227, 0.98)),
    var(--dqa-desk) !important;
  overflow: hidden;
  position: relative;
}

.dc-stage::after {
  background: linear-gradient(90deg, rgba(95, 143, 104, 0.24), rgba(214, 123, 103, 0.2), rgba(215, 168, 66, 0.2));
  content: "";
  height: 5px;
  left: 0;
  position: absolute;
  right: 0;
  top: 0;
}

.dc-stage .dc-composer {
  padding-top: 8px !important;
}

.dc-stage .dc-dream-text textarea {
  background:
    linear-gradient(180deg, rgba(255, 250, 240, 0.96), rgba(255, 253, 248, 0.98)),
    repeating-linear-gradient(180deg, transparent 0 31px, var(--dqa-paper-line) 31px 32px) !important;
  border-color: rgba(95, 143, 104, 0.2) !important;
  border-radius: 8px !important;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.78),
    var(--dqa-paper-shadow) !important;
  color: var(--dqa-pencil) !important;
  min-height: 350px !important;
  padding-left: 72px !important;
}

.dc-stage .dc-dream-text textarea:focus {
  border-color: rgba(95, 143, 104, 0.54) !important;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.78),
    0 0 0 3px rgba(95, 143, 104, 0.14),
    var(--dqa-paper-shadow) !important;
}

.dc-field-tip {
  background: #fff7df;
  border: 1px solid rgba(215, 168, 66, 0.34);
  border-radius: 8px;
  box-shadow: 3px 4px 0 rgba(111, 92, 48, 0.08);
  display: grid;
  gap: 5px;
  margin: 16px 0 0;
  padding: 13px 15px;
}

.dc-field-tip span {
  color: #8c6733;
  font-size: 0.74rem;
  font-weight: 820;
  text-transform: uppercase;
}

.dc-field-tip strong {
  color: var(--dqa-pencil);
  font-size: 1rem;
  line-height: 1.25;
}

.dc-field-tip p {
  color: #6f746c;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

.dc-field-tip.is-error {
  display: block;
}

.dc-demo-chip-intro {
  align-items: baseline;
  color: var(--dqa-muted);
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 18px 0 0;
}

.dc-demo-chip-intro span {
  color: var(--dqa-sage-deep);
  font-size: 0.78rem;
  font-weight: 820;
  text-transform: uppercase;
}

.dc-demo-chip-intro strong {
  color: #59675f;
  font-size: 0.92rem;
  font-weight: 650;
}

.dc-demo-chip-row .dc-demo-chip button {
  background: var(--dqa-paper-warm) !important;
  border: 1px solid rgba(95, 143, 104, 0.22) !important;
  border-radius: 8px !important;
  box-shadow: 4px 4px 0 rgba(44, 55, 52, 0.08) !important;
  min-height: 58px !important;
  padding: 10px 12px !important;
  white-space: normal !important;
}

.dc-demo-chip-row .dc-demo-chip button:hover,
.dc-demo-chip-row .dc-demo-chip button:focus-visible {
  background: #eef7e9 !important;
  border-color: rgba(95, 143, 104, 0.45) !important;
}

.dc-side-panel {
  background: rgba(255, 253, 248, 0.98) !important;
  gap: 14px;
}

.dc-side-stack {
  display: grid;
  gap: 12px;
}

.dc-side-stamp,
.dc-desk-rule,
.dc-intake-rail {
  border-radius: 8px;
  box-shadow: 3px 4px 0 rgba(44, 55, 52, 0.06);
}

.dc-side-stamp {
  background: linear-gradient(180deg, #fff8e2, #fffdf8) !important;
  border-color: rgba(215, 168, 66, 0.32) !important;
}

.dc-desk-rule {
  background: #eff7ee;
  border: 1px solid rgba(95, 143, 104, 0.24);
  color: var(--dqa-pencil);
  display: grid;
  gap: 6px;
  padding: 16px;
}

.dc-desk-rule span,
.dc-intake-rail small {
  color: var(--dqa-sage-deep);
  font-size: 0.74rem;
  font-weight: 820;
  text-transform: uppercase;
}

.dc-desk-rule strong {
  color: var(--dqa-pencil);
  font-size: 1.06rem;
  line-height: 1.25;
}

.dc-desk-rule p {
  color: #607169;
  font-size: 0.92rem;
  line-height: 1.5;
  margin: 0;
}

.dc-intake-rail {
  background: #fffdf8;
  border: 1px solid rgba(217, 226, 220, 0.92);
  display: grid;
  gap: 10px;
  padding: 14px;
}

.dc-intake-rail div {
  display: grid;
  gap: 8px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.dc-intake-rail span {
  background: #f4faf2;
  border: 1px solid rgba(95, 143, 104, 0.2);
  border-radius: 999px;
  color: var(--dqa-sage-deep);
  font-size: 0.78rem;
  font-weight: 760;
  padding: 7px 6px;
  text-align: center;
}

.dc-question-card {
  background:
    linear-gradient(180deg, rgba(255, 250, 240, 0.98), rgba(255, 245, 222, 0.98)),
    repeating-linear-gradient(180deg, transparent 0 30px, rgba(215, 168, 66, 0.12) 30px 31px) !important;
  border-color: rgba(215, 168, 66, 0.36);
  border-radius: 8px;
  box-shadow: var(--dqa-paper-shadow);
  position: relative;
}

.dc-question-card::before {
  background: rgba(95, 143, 104, 0.16);
  border: 1px solid rgba(95, 143, 104, 0.16);
  content: "";
  height: 28px;
  left: 50%;
  position: absolute;
  top: -14px;
  transform: translateX(-50%) rotate(-2deg);
  width: 104px;
}

.dc-question-anchor-wrap {
  background: rgba(255, 253, 248, 0.62);
  border: 1px dashed rgba(95, 143, 104, 0.28);
  border-radius: 8px;
  margin: 16px 0 8px;
  padding: 12px;
}

.dc-question-anchor-label {
  color: var(--dqa-sage-deep);
  display: block;
  font-size: 0.76rem;
  font-weight: 820;
  margin-bottom: 8px;
  text-transform: uppercase;
}

.dc-question-anchor-strip {
  margin: 0;
}

.dc-question-original {
  background: rgba(255, 253, 248, 0.7);
  border-left-color: var(--dqa-brass);
  border-radius: 0 8px 8px 0;
  padding: 11px 12px;
}

.dqa-tip-page {
  border-radius: 8px;
}

.dqa-tip-hero {
  border-radius: 8px 8px 0 0;
  display: grid;
  gap: 18px;
  grid-template-columns: minmax(0, 1fr) minmax(140px, 190px);
  position: relative;
}

.dqa-ticket-stamp {
  align-self: start;
  background: rgba(255, 250, 240, 0.9);
  border: 2px solid rgba(95, 143, 104, 0.36);
  border-radius: 8px;
  box-shadow: 3px 4px 0 rgba(44, 55, 52, 0.08);
  color: var(--dqa-sage-deep);
  display: grid;
  gap: 6px;
  justify-items: center;
  padding: 13px 12px;
  text-align: center;
  transform: rotate(3deg);
}

.dqa-ticket-stamp span {
  font-size: 0.72rem;
  font-weight: 820;
  text-transform: uppercase;
}

.dqa-ticket-stamp strong {
  color: var(--dqa-pencil);
  font-size: 0.96rem;
  line-height: 1.2;
}

.dqa-morning-ticket {
  border-radius: 8px;
  position: relative;
}

.dqa-morning-ticket::after {
  background: linear-gradient(180deg, rgba(215, 168, 66, 0.18), rgba(95, 143, 104, 0.18));
  content: "";
  height: 100%;
  left: 0;
  position: absolute;
  top: 0;
  width: 6px;
}

.dqa-ticket-row.is-primary-tip {
  background:
    linear-gradient(90deg, rgba(239, 247, 238, 0.96), rgba(255, 248, 226, 0.96)),
    repeating-linear-gradient(180deg, transparent 0 34px, rgba(95, 143, 104, 0.1) 34px 35px);
}

.dqa-safety-note,
.dqa-care-note,
.dqa-qa-history,
.dqa-small-model-note {
  border-radius: 8px;
}

@media (max-width: 900px) {
  .dc-workspace-grid {
    margin-top: -14px;
  }

  .dc-hero-ribbon {
    justify-self: stretch;
  }

  .dc-stage .dc-dream-text textarea {
    min-height: 320px !important;
  }

  .dqa-tip-hero {
    grid-template-columns: 1fr;
  }

  .dqa-ticket-stamp {
    justify-self: start;
    transform: none;
  }
}

@media (max-width: 640px) {
  .dc-hero {
    min-height: 430px;
  }

  .dc-hero-ribbon {
    align-items: flex-start;
    display: grid;
  }

  .dc-stage .dc-dream-text textarea {
    padding-left: 58px !important;
  }

  .dc-intake-rail div {
    grid-template-columns: 1fr;
  }

  .dc-question-card::before {
    left: 24px;
    transform: rotate(-2deg);
  }
}
"""

CSS += """
.dc-hero {
  align-content: end;
  display: grid;
  gap: 18px;
  min-height: clamp(330px, 40vw, 500px);
}

.dc-hero-kicker {
  color: var(--dqa-sage-deep);
  font-size: clamp(0.84rem, 1.4vw, 1rem);
  font-weight: 760;
  letter-spacing: 0;
  margin: 0 0 10px;
}

.dc-hero h1 {
  max-width: 960px;
}

.dc-brand-subtitle {
  margin-left: auto;
  margin-right: auto;
  max-width: 760px;
}

.dc-hero-body {
  color: #4f626c;
  font-size: clamp(1rem, 1.8vw, 1.22rem);
  line-height: 1.65;
  margin: 0 auto;
  max-width: 740px;
  text-align: center;
}

.dc-sun-mark {
  aspect-ratio: 1;
  background:
    linear-gradient(90deg, transparent 47%, rgba(239, 139, 112, 0.55) 48% 52%, transparent 53%),
    linear-gradient(0deg, transparent 47%, rgba(239, 139, 112, 0.55) 48% 52%, transparent 53%),
    radial-gradient(circle, rgba(240, 181, 61, 0.7) 0 34%, transparent 35%);
  border: 1px solid rgba(239, 139, 112, 0.32);
  border-radius: 999px;
  height: 58px;
  justify-self: end;
  width: 58px;
}

.dc-demo-chip-intro {
  color: var(--dqa-muted);
  font-size: 0.92rem;
  font-weight: 650;
  margin: 14px 0 0;
}

.dc-submit-row {
  align-items: stretch !important;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr) !important;
}

.dc-demo-chip-row {
  align-content: stretch !important;
  display: grid !important;
  gap: 10px !important;
  grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
  min-width: 0;
}

.dc-demo-chip-row .dc-demo-chip button {
  background: #ffffff !important;
  border: 1px solid rgba(79, 138, 88, 0.28) !important;
  border-radius: 999px !important;
  box-shadow: none !important;
  color: var(--dqa-sage-deep) !important;
  font-size: 0.95rem !important;
  min-height: 52px !important;
  padding: 10px 12px !important;
  transition: background 180ms ease, border-color 180ms ease, transform 180ms ease;
}

.dc-demo-chip-row .dc-demo-chip button:hover,
.dc-demo-chip-row .dc-demo-chip button:focus-visible {
  background: var(--dqa-sage-soft) !important;
  border-color: rgba(79, 138, 88, 0.52) !important;
  transform: translateY(-1px);
}

.dqa-tip-page {
  background: #fffdf8;
  border: 1px solid var(--dqa-line);
  box-shadow: 0 24px 60px rgba(45, 56, 42, 0.14);
  overflow: hidden;
}

.dqa-tip-hero {
  background:
    linear-gradient(90deg, rgba(255, 253, 248, 0.94), rgba(255, 253, 248, 0.68)),
    url("https://images.unsplash.com/photo-1494438639946-1ebd1d20bf85?auto=format&fit=crop&w=1200&q=80") center / cover;
  min-height: 150px;
}

.dqa-tip-hero h2 {
  font-size: clamp(2rem, 5vw, 3.4rem);
}

.dqa-anchor-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 22px 42px 0;
}

.dqa-anchor-chips span {
  background: var(--dqa-sage-soft);
  border: 1px solid rgba(79, 138, 88, 0.26);
  border-radius: 999px;
  color: var(--dqa-sage-deep);
  font-size: 0.92rem;
  font-weight: 720;
  padding: 8px 12px;
}

.dqa-morning-ticket {
  background:
    linear-gradient(#fffdf8 0 0) padding-box,
    repeating-linear-gradient(90deg, #ead8aa 0 16px, transparent 16px 28px) border-box;
  border: 1px solid transparent;
  border-radius: 10px;
  box-shadow: var(--dqa-shadow);
  margin: 0 42px;
  overflow: hidden;
}

.dqa-ticket-topline {
  align-items: center;
  background: #f8f1df;
  border-bottom: 1px dashed #dfc98e;
  color: #6c5a37;
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  justify-content: space-between;
  padding: 14px 18px;
}

.dqa-ticket-topline span {
  font-size: 0.82rem;
  font-weight: 760;
}

.dqa-ticket-topline strong {
  color: var(--dqa-sage-deep);
  font-size: 0.96rem;
  line-height: 1.4;
}

.dqa-ticket-row {
  border-bottom: 1px dashed #ead8aa;
  padding: clamp(18px, 3vw, 30px);
}

.dqa-ticket-row:last-child {
  border-bottom: 0;
}

.dqa-ticket-row h3 {
  color: var(--dqa-ink) !important;
  font-size: clamp(1.1rem, 2.6vw, 1.65rem);
  margin: 0 0 10px;
}

.dqa-ticket-row p {
  color: var(--dqa-ink) !important;
  font-size: 1.05rem;
  line-height: 1.72;
  margin: 0;
}

.dqa-ticket-row.is-primary-tip {
  background: linear-gradient(90deg, rgba(233, 243, 231, 0.9), rgba(255, 247, 217, 0.92));
}

.dqa-ticket-row.is-primary-tip h3 {
  font-size: clamp(1.7rem, 4vw, 2.45rem);
}

.dqa-small-model-note {
  background: #f7fbf4;
  border: 1px solid rgba(79, 138, 88, 0.2);
  border-radius: 12px;
  color: var(--dqa-ink);
  margin: 0 42px;
  padding: 14px 18px;
}

.dqa-small-model-note summary {
  color: var(--dqa-sage-deep);
  cursor: pointer;
  font-weight: 760;
}

.dqa-small-model-note p {
  color: var(--dqa-muted);
  line-height: 1.6;
  margin: 10px 0 0;
}

.dqa-care-note {
  display: grid;
  gap: 4px;
}

.dqa-care-note strong {
  color: var(--dqa-sage-deep);
}

@media (max-width: 900px) {
  .dc-submit-row,
  .dc-demo-chip-row {
    grid-template-columns: 1fr !important;
  }

  .dc-sun-mark {
    display: none;
  }
}

@media (max-width: 640px) {
  .dc-hero {
    min-height: 360px;
  }

  .dc-hero-body {
    text-align: left;
  }

  .dc-brand-lockup {
    text-align: left;
  }

  .dc-brand-subtitle {
    margin-left: 0;
    margin-right: 0;
  }

  .dqa-anchor-chips,
  .dqa-morning-ticket,
  .dqa-small-model-note {
    margin-left: 18px;
    margin-right: 18px;
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
  align-items: flex-start;
  display: flex;
  gap: 0;
  margin: clamp(28px, 5vw, 58px) auto 0;
  max-width: 920px;
  position: relative;
}

.dc-stepper-line {
  background: #9cadb8;
  border-radius: 999px;
  display: block;
  flex: 1 1 70px;
  height: 3px;
  margin-top: clamp(24px, 3.4vw, 35px);
  min-width: 34px;
  transition: background-color 180ms ease, box-shadow 180ms ease;
}

.dc-stepper-line.is-complete {
  background: var(--dqa-sage);
  box-shadow: 0 0 0 1px rgba(79, 138, 88, 0.14);
}

.dc-stepper span {
  color: #667989;
  display: grid;
  flex: 0 0 clamp(72px, 13vw, 128px);
  font-size: clamp(1rem, 2.3vw, 1.45rem);
  gap: 10px;
  justify-items: center;
  min-width: 0;
  position: relative;
  text-align: center;
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

.dc-stepper .is-complete {
  color: var(--dqa-sage-deep);
}

.dc-stepper .is-complete strong {
  background: rgba(91, 138, 97, 0.18);
  border-color: rgba(91, 138, 97, 0.42);
  color: var(--dqa-sage-deep);
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

.dc-question-anchor-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 16px 0 4px;
}

.dc-question-anchor-strip span {
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(152, 125, 69, 0.24);
  border-radius: 999px;
  box-shadow: 0 8px 18px rgba(88, 72, 40, 0.08);
  color: var(--dqa-ink);
  font-size: 0.88rem;
  font-weight: 750;
  line-height: 1.2;
  padding: 8px 12px;
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

.dc-stage .dc-composer {
  background: transparent !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  min-height: 0 !important;
  overflow: visible !important;
  padding: 0 !important;
  position: relative;
}

.dc-stage > .styler {
  background: transparent !important;
}

.dc-stage .dc-composer .form {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}

.dc-stage .dc-composer .dc-section-title {
  color: var(--dqa-ink) !important;
  margin: 0 0 14px;
}

.dc-stage .dc-composer .dc-section-title strong {
  color: var(--dqa-ink) !important;
}

.dc-side-panel .dc-section-title,
.dc-side-panel .dc-section-title strong {
  color: var(--dqa-ink) !important;
  opacity: 1 !important;
}

.dc-shell,
.dc-stage,
.dc-side-panel,
.dc-dev,
.dc-debug-panel {
  color-scheme: light;
}

.dc-side-panel {
  background: rgba(255, 253, 248, 0.96) !important;
  border-color: var(--dqa-line) !important;
  color: var(--dqa-ink) !important;
}

.dc-side-panel > .styler,
.dc-side-panel .form,
.dc-side-panel .block,
.dc-side-panel .wrap,
.dc-side-panel .container,
.dc-side-panel .input-container {
  background: transparent !important;
  border-color: rgba(217, 226, 220, 0.88) !important;
  box-shadow: none !important;
  color: var(--dqa-ink) !important;
}

.dc-side-panel .block:has(input[type="radio"]),
.dc-side-panel .wrap:has(input[type="radio"]) {
  background: transparent !important;
}

.dc-side-panel label,
.dc-side-panel [data-testid="block-label"],
.dc-side-panel [data-testid="block-info"] {
  color: var(--dqa-ink) !important;
}

.dc-side-panel label:has(input[type="radio"]),
.dc-side-panel .wrap label {
  background: rgba(255, 253, 248, 0.96) !important;
  border: 1px solid var(--dqa-line) !important;
  border-radius: 12px !important;
  color: var(--dqa-ink) !important;
}

.dc-side-panel label:has(input[type="radio"]:checked) {
  background: var(--dqa-sage-soft) !important;
  border-color: rgba(79, 138, 88, 0.42) !important;
  color: var(--dqa-sage-deep) !important;
}

.dc-side-panel input,
.dc-side-panel select,
.dc-side-panel button,
.dc-side-panel .dropdown,
.dc-side-panel .svelte-1gfkn6j,
.dc-side-panel .svelte-1hfxrpf,
.dc-side-panel .svelte-1b6s6s {
  color: var(--dqa-ink) !important;
}

.dc-side-panel select,
.dc-side-panel .wrap:has(select),
.dc-side-panel .container:has(select),
.dc-side-panel [role="listbox"],
.dc-side-panel [aria-haspopup="listbox"] {
  background: rgba(255, 253, 248, 0.98) !important;
  border-color: var(--dqa-line) !important;
  border-radius: 12px !important;
  color: var(--dqa-ink) !important;
}

.dc-side-panel svg,
.dc-side-panel img {
  color: var(--dqa-muted) !important;
  opacity: 0.86;
}

.dc-side-panel .dc-dev,
.dc-side-panel .dc-dev > .label-wrap,
.dc-side-panel .dc-dev > button,
.dc-side-panel button[aria-expanded] {
  background: rgba(255, 253, 248, 0.96) !important;
  border-color: var(--dqa-line) !important;
  color: var(--dqa-muted) !important;
}

.dc-side-panel .block:has(input[role="listbox"]) {
  background: rgba(255, 253, 248, 0.98) !important;
  border: 1px solid var(--dqa-line) !important;
  border-radius: 16px !important;
  box-shadow: none !important;
  padding: 20px 22px 18px !important;
}

.dc-side-panel .form:has(input[role="listbox"]) {
  background: transparent !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  padding: 0 !important;
}

.dc-side-panel .block:has(input[role="listbox"]) .wrap,
.dc-side-panel .block:has(input[role="listbox"]) .container,
.dc-side-panel .block:has(input[role="listbox"]) .wrap-inner,
.dc-side-panel .block:has(input[role="listbox"]) .secondary-wrap,
.dc-side-panel .block:has(input[role="listbox"]) .input-container,
.dc-side-panel .block:has(input[role="listbox"]) input[role="listbox"] {
  background: transparent !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
}

.dc-side-panel .block:has(input[role="listbox"]) .wrap {
  min-height: 34px !important;
}

.dc-side-panel .block:has(input[role="listbox"]) input[role="listbox"] {
  font-size: 1rem !important;
  min-height: 30px !important;
}

.dc-side-panel .block:has(input[role="listbox"]) * {
  --input-border-width: 0px;
  --block-border-width: 0px;
}

.dc-side-panel .block:has(input[role="listbox"]) .wrap,
.dc-side-panel .block:has(input[role="listbox"]) .container,
.dc-side-panel .block:has(input[role="listbox"]) .wrap-inner,
.dc-side-panel .block:has(input[role="listbox"]) .secondary-wrap,
.dc-side-panel .block:has(input[role="listbox"]) .input-container,
.dc-side-panel .block:has(input[role="listbox"]) input[role="listbox"] {
  border: 0 !important;
  border-color: transparent !important;
  outline: 0 !important;
}

.dc-side-panel .block:has(input[role="listbox"]) .icon-wrap {
  pointer-events: none !important;
  transition: color 160ms ease, transform 160ms ease;
}

.dc-side-panel .block:has(input[role="listbox"]) .dropdown-arrow {
  color: var(--dqa-muted) !important;
  transition: color 160ms ease, transform 160ms ease;
  transform-origin: center;
  transform-box: fill-box;
}

.dc-side-panel .block:has(> .container input[role="listbox"][aria-expanded="true"]) > .container .dropdown-arrow {
  color: var(--dqa-sage-deep) !important;
  transform: rotate(180deg) !important;
}

.dc-side-panel .block:has(input[role="listbox"]:hover) .dropdown-arrow,
.dc-side-panel .block:has(input[role="listbox"]:focus) .dropdown-arrow,
.dc-side-panel .block:has(input[role="listbox"]) .icon-wrap:hover .dropdown-arrow {
  color: var(--dqa-sage-deep) !important;
}

.dc-side-panel .dc-dev {
  background: rgba(255, 253, 248, 0.98) !important;
  border: 1px solid var(--dqa-line) !important;
  border-radius: 20px !important;
  box-shadow: none !important;
  color: var(--dqa-ink) !important;
  padding: 14px !important;
}

.dc-side-panel .dc-dev > button {
  align-items: center !important;
  background: transparent !important;
  border: 0 !important;
  border-radius: 14px !important;
  box-shadow: none !important;
  color: var(--dqa-ink) !important;
  font-size: 1rem !important;
  font-weight: 680 !important;
  min-height: 46px !important;
  padding: 0 4px !important;
}

.dc-side-panel .dc-dev > button:hover,
.dc-side-panel .dc-dev > button[aria-expanded="true"] {
  background: var(--dqa-sage-soft) !important;
  color: var(--dqa-sage-deep) !important;
}

.dc-side-panel .dc-dev-help {
  color: #60717a !important;
  display: grid !important;
  font-size: 0.92rem !important;
  gap: 8px !important;
  line-height: 1.5 !important;
  margin: 8px 0 14px !important;
}

.dc-side-panel .dc-dev-help strong {
  color: var(--dqa-ink) !important;
  font-size: 0.94rem !important;
  font-weight: 760 !important;
  line-height: 1.42 !important;
}

.dc-side-panel .dc-dev-help span {
  color: #60717a !important;
  opacity: 1 !important;
}

.dc-side-panel .dc-dev .block:has(input[role="listbox"]) {
  background: rgba(255, 253, 248, 0.98) !important;
  border: 1px solid var(--dqa-line) !important;
  border-radius: 14px !important;
  box-shadow: none !important;
  margin: 8px 0 !important;
  padding: 12px 14px !important;
}

.dc-side-panel .dc-dev .block:has(input[role="listbox"]) label,
.dc-side-panel .dc-dev .block:has(input[role="listbox"]) [data-testid="block-label"] {
  color: var(--dqa-ink) !important;
  font-size: 0.84rem !important;
  font-weight: 680 !important;
  margin-bottom: 8px !important;
}

.dc-side-panel .dc-dev .block:has(input[role="listbox"]) .wrap,
.dc-side-panel .dc-dev .block:has(input[role="listbox"]) .container,
.dc-side-panel .dc-dev .block:has(input[role="listbox"]) .wrap-inner,
.dc-side-panel .dc-dev .block:has(input[role="listbox"]) .secondary-wrap,
.dc-side-panel .dc-dev .block:has(input[role="listbox"]) .input-container,
.dc-side-panel .dc-dev .block:has(input[role="listbox"]) input[role="listbox"] {
  min-height: 32px !important;
  padding: 0 !important;
}

.dc-side-panel .dc-dev .block:has(input[role="listbox"]) input[role="listbox"] {
  color: var(--dqa-ink) !important;
  font-size: 0.94rem !important;
  font-weight: 560 !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
  width: 100% !important;
}

.dc-side-panel .dc-dev .block:has(input[role="listbox"]) .wrap-inner {
  align-items: center !important;
  display: flex !important;
  gap: 8px !important;
}

.dc-side-panel .dc-dev .block:has(input[role="listbox"]) .secondary-wrap {
  flex: 1 1 auto !important;
  max-width: calc(100% - 38px) !important;
  min-width: 0 !important;
  overflow: hidden !important;
}

.dc-side-panel .dc-dev .block:has(input[role="listbox"]) .icon-wrap {
  flex: 0 0 28px !important;
  height: 28px !important;
  width: 28px !important;
}

.dc-side-panel .dc-dev-tuning {
  background: rgba(255, 253, 248, 0.98) !important;
  border: 1px solid var(--dqa-line) !important;
  border-radius: 16px !important;
  box-shadow: none !important;
  display: grid !important;
  gap: 0 !important;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin: 6px 0 12px !important;
  overflow: hidden !important;
  padding: 6px !important;
}

.dc-side-panel .dc-dev-tuning > .styler,
.dc-side-panel .dc-dev-tuning .form {
  background: transparent !important;
  border: 0 !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  display: grid !important;
  gap: 6px !important;
  grid-column: 1 / -1 !important;
  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  width: 100% !important;
}

.dc-side-panel .dc-dev-tuning .block {
  background: rgba(255, 255, 255, 0.58) !important;
  border: 1px solid rgba(217, 226, 220, 0.72) !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  margin: 0 !important;
  min-width: 0 !important;
  padding: 9px 10px !important;
}

.dc-side-panel .dc-dev-tuning .wrap.hide {
  display: none !important;
  height: 0 !important;
  min-height: 0 !important;
}

.dc-side-panel .dc-dev-tuning .container {
  min-height: 0 !important;
  padding: 0 !important;
}

.dc-side-panel .dc-dev-tuning label,
.dc-side-panel .dc-dev-tuning [data-testid="block-label"] {
  color: var(--dqa-muted) !important;
  font-size: 0.74rem !important;
  font-weight: 700 !important;
  line-height: 1.25 !important;
  margin-bottom: 0 !important;
}

.dc-side-panel .dc-dev-tuning input {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  color: var(--dqa-ink) !important;
  font-size: 0.92rem !important;
  font-weight: 700 !important;
  min-height: 30px !important;
  padding: 0 !important;
}

.dc-side-panel .dc-dev-advanced {
  background: rgba(255, 253, 248, 0.98) !important;
  border: 1px solid var(--dqa-line) !important;
  border-radius: 14px !important;
  box-shadow: none !important;
  margin-top: 12px !important;
}

.dc-side-panel .dc-dev-advanced > button {
  color: var(--dqa-ink) !important;
  font-size: 0.94rem !important;
  font-weight: 650 !important;
  min-height: 42px !important;
  padding: 0 12px !important;
}

.gradio-container [role="listbox"],
.gradio-container .options,
.gradio-container .dropdown-options {
  background: rgba(255, 253, 248, 0.99) !important;
  border: 1px solid var(--dqa-line) !important;
  border-radius: 16px !important;
  box-shadow: 0 16px 38px rgba(30, 42, 48, 0.12) !important;
  color: var(--dqa-ink) !important;
  overflow: hidden !important;
}

.gradio-container [role="option"],
.gradio-container .option,
.gradio-container .item {
  background: transparent !important;
  color: var(--dqa-ink) !important;
}

.gradio-container [role="option"]:hover,
.gradio-container [role="option"][aria-selected="true"],
.gradio-container [role="option"].selected,
.gradio-container .option:hover,
.gradio-container .option.selected,
.gradio-container .item:hover,
.gradio-container .item.selected {
  background: var(--dqa-sage-soft) !important;
  color: var(--dqa-ink) !important;
}

.gradio-container [role="option"]:focus,
.gradio-container .option:focus,
.gradio-container .item:focus {
  background: rgba(233, 243, 231, 0.78) !important;
  color: var(--dqa-ink) !important;
  outline: 2px solid rgba(79, 138, 88, 0.34) !important;
  outline-offset: -2px;
}

.dc-stage .dc-dream-text,
.dc-stage .dc-dream-text .wrap,
.dc-stage .dc-dream-text .container,
.dc-stage .dc-dream-text .input-container,
.dc-stage .dc-dream-text .form,
.dc-stage .dc-dream-text > div {
  background: transparent !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  margin: 0 !important;
  overflow: visible !important;
  padding: 0 !important;
}

.dc-stage .dc-dream-text [data-testid="block-label"],
.dc-stage .dc-dream-text [data-testid="block-info"],
.dc-stage .dc-dream-text .block-label {
  display: none !important;
}

.dc-stage .dc-dream-text textarea {
  background: rgba(255, 253, 248, 0.98) !important;
  border: 1px solid var(--dqa-line) !important;
  border-radius: 30px !important;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.82),
    0 18px 38px rgba(30, 42, 48, 0.1) !important;
  color: var(--dqa-ink) !important;
  min-height: 320px !important;
  overflow: hidden !important;
  padding: 28px 96px 82px 78px !important;
  resize: none !important;
}

.dc-attach-control,
.dc-mic-control {
  bottom: 24px !important;
  position: absolute;
  z-index: 18;
}

.dc-attach-control {
  left: 24px;
}

.dc-mic-control {
  display: block !important;
  height: 52px !important;
  right: 24px !important;
  width: 52px !important;
}

.dc-stage .dc-attach-control .dc-attach-button,
.dc-stage .dc-mic-control .dc-mic-button {
  align-items: center !important;
  background: rgba(255, 253, 248, 0.98) !important;
  border: 1px solid rgba(7, 60, 67, 0.22) !important;
  border-radius: 999px !important;
  box-sizing: border-box !important;
  box-shadow: 0 10px 22px rgba(7, 60, 67, 0.12) !important;
  color: var(--dc-teal-dark) !important;
  display: inline-flex !important;
  height: 52px !important;
  justify-content: center !important;
  line-height: 1 !important;
  max-height: 52px !important;
  min-height: 52px !important;
  padding: 0 !important;
  width: 52px !important;
}

.dc-stage .dc-attach-control .dc-attach-button {
  cursor: pointer;
  font-size: 1.6rem !important;
  font-weight: 720 !important;
  opacity: 1 !important;
}

.dc-stage .dc-attach-control .dc-attach-button span {
  color: var(--dc-teal-dark) !important;
  opacity: 1 !important;
}

.dc-stage .dc-attach-control .dc-attach-button:hover,
.dc-stage .dc-attach-control .dc-attach-button[aria-expanded="true"],
.dc-stage .dc-mic-control .dc-mic-button:hover {
  border-color: rgba(234, 107, 44, 0.42) !important;
  color: var(--dc-coral-dark) !important;
  transform: translateY(-1px);
}

.dc-stage .dc-mic-control .dc-mic-status {
  bottom: 62px;
  position: absolute;
  right: 0;
  white-space: nowrap;
}

.dc-image-popover {
  bottom: 88px;
  background: rgba(255, 253, 248, 0.99) !important;
  border: 1px solid var(--dqa-line) !important;
  border-radius: 26px !important;
  border-style: solid !important;
  box-shadow: 0 18px 42px rgba(30, 42, 48, 0.16) !important;
  color: var(--dqa-ink) !important;
  height: 220px !important;
  left: 24px;
  margin: 0 !important;
  max-width: calc(100% - 48px);
  opacity: 0;
  overflow: hidden !important;
  pointer-events: none;
  position: absolute !important;
  transform: translateY(8px) scale(0.98);
  transition: opacity 160ms ease, transform 160ms ease, visibility 160ms ease;
  visibility: hidden;
  width: min(420px, calc(100% - 48px));
  z-index: 20;
}

.dc-composer.dc-image-open .dc-image-popover {
  opacity: 1;
  pointer-events: auto;
  transform: translateY(0) scale(1);
  visibility: visible;
}

.dc-image-popover .wrap,
.dc-image-popover .container,
.dc-image-popover .upload-container,
.dc-image-popover .image-container,
.dc-image-popover [data-testid="image"],
.dc-image-popover [data-testid="file-upload"] {
  background: transparent !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
}

.dc-image-popover [data-testid="block-label"] {
  align-items: center !important;
  background: rgba(238, 247, 236, 0.96) !important;
  border: 1px solid rgba(88, 142, 94, 0.2) !important;
  border-radius: 999px !important;
  box-shadow: none !important;
  color: var(--dqa-sage-deep) !important;
  display: inline-flex !important;
  font-family: inherit !important;
  font-size: 0.84rem !important;
  font-weight: 720 !important;
  gap: 7px !important;
  left: 16px !important;
  line-height: 1 !important;
  padding: 8px 12px !important;
  top: 14px !important;
}

.dc-image-popover [data-testid="block-label"] svg {
  color: var(--dqa-sage-deep) !important;
  height: 16px !important;
  width: 16px !important;
}

.dc-image-popover .image-container {
  height: 100% !important;
  overflow: hidden !important;
}

.dc-image-popover .upload-container {
  height: 100% !important;
  padding: 18px 18px 64px !important;
}

.dc-image-popover .upload-container button {
  align-items: center !important;
  background: transparent !important;
  border: 0 !important;
  border-radius: 22px !important;
  box-shadow: none !important;
  color: var(--dqa-ink) !important;
  display: flex !important;
  justify-content: center !important;
  min-height: 130px !important;
  width: 100% !important;
}

.dc-image-popover .upload-container button:hover {
  background: rgba(238, 247, 236, 0.56) !important;
}

.dc-image-popover .upload-container .wrap {
  align-items: center !important;
  color: var(--dqa-ink) !important;
  display: flex !important;
  flex-direction: column !important;
  font-size: 0 !important;
  gap: 12px !important;
  justify-content: center !important;
}

.dc-image-popover .upload-container .icon-wrap,
.dc-image-popover .upload-container svg {
  color: var(--dqa-sage-deep) !important;
  height: 32px !important;
  width: 32px !important;
}

.dc-image-popover .upload-container .or {
  display: none !important;
}

.dc-image-upload-copy {
  color: var(--dqa-ink) !important;
  display: block !important;
  font-size: 1rem !important;
  font-weight: 760 !important;
  letter-spacing: 0 !important;
}

.dc-image-popover [data-testid="source-select"] {
  align-items: center !important;
  background: transparent !important;
  border: 0 !important;
  border-top: 0 !important;
  bottom: 16px !important;
  box-shadow: none !important;
  display: flex !important;
  gap: 12px !important;
  justify-content: center !important;
  left: 0 !important;
  padding: 0 !important;
  position: absolute !important;
  right: 0 !important;
}

.dc-image-popover [data-testid="source-select"]::before,
.dc-image-popover [data-testid="source-select"]::after {
  display: none !important;
}

.dc-image-popover [data-testid="source-select"] button {
  align-items: center !important;
  background: rgba(255, 253, 248, 0.92) !important;
  border: 1px solid var(--dqa-line) !important;
  border-radius: 999px !important;
  box-shadow: none !important;
  color: var(--dqa-muted) !important;
  display: inline-flex !important;
  height: 42px !important;
  justify-content: center !important;
  min-height: 42px !important;
  padding: 0 !important;
  width: 42px !important;
}

.dc-image-popover [data-testid="source-select"] button:hover,
.dc-image-popover [data-testid="source-select"] button.selected {
  background: var(--dqa-sage-soft) !important;
  border-color: rgba(88, 142, 94, 0.26) !important;
  color: var(--dqa-sage-deep) !important;
}

.dc-image-popover [aria-label="Capture from camera"] {
  display: none !important;
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

  .dc-stepper-line {
    flex-basis: 26px;
    margin-top: 24px;
    min-width: 20px;
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
    bottom: 22px;
    right: 20px;
  }

  .dc-attach-control {
    bottom: 22px;
    left: 20px;
  }

  .dc-stage .dc-dream-text textarea {
    border-radius: 24px !important;
    min-height: 300px !important;
    padding: 24px 78px 78px 70px !important;
  }

  .dc-image-popover {
    bottom: 84px;
    left: 20px;
    width: min(360px, calc(100% - 40px));
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

CSS += """
/* Hero proportion fix: make the desk invitation feel calm, centered, and brief. */
.dc-hero {
  align-content: center;
  justify-items: center;
  background:
    radial-gradient(circle at 74% 37%, rgba(255, 253, 248, 0.54) 0 16%, rgba(255, 253, 248, 0.88) 33%, rgba(255, 253, 248, 0.98) 62%),
    linear-gradient(180deg, rgba(246, 251, 246, 0.96), rgba(255, 250, 240, 0.99)),
    url("https://images.unsplash.com/photo-1494438639946-1ebd1d20bf85?auto=format&fit=crop&w=1600&q=80") 74% 43% / cover !important;
  gap: clamp(10px, 1.8vw, 16px);
  min-height: clamp(360px, 44vh, 500px);
  overflow: hidden;
  padding: clamp(22px, 3.6vw, 40px) clamp(18px, 5vw, 70px) clamp(26px, 4.2vw, 48px);
  text-align: center;
}

.dc-hero-top {
  justify-self: stretch;
  grid-template-columns: 44px minmax(0, 1fr) 44px;
}

.dc-brand-lockup {
  justify-content: center;
  text-align: center;
}

.dc-brand-lockup > div {
  display: grid;
  justify-items: center;
  max-width: min(100%, 900px);
}

.dc-menu-mark {
  opacity: 0.78;
}

.dc-sun-mark {
  height: 44px;
  opacity: 0.78;
  width: 44px;
}

.dc-hero-kicker {
  font-size: clamp(0.78rem, 1.1vw, 0.96rem);
  margin-bottom: 8px;
}

.dc-hero h1 {
  font-size: clamp(2.45rem, 5.2vw, 4.35rem) !important;
  line-height: 1.01;
  margin-left: auto;
  margin-right: auto;
  max-width: 820px;
  text-align: center;
  text-wrap: balance;
}

.dc-brand-subtitle {
  color: #6f7f8b;
  font-size: clamp(1rem, 1.55vw, 1.2rem);
  line-height: 1.45;
  margin-left: auto;
  margin-right: auto;
  max-width: 560px;
  text-align: center;
  text-wrap: balance;
}

.dc-hero-body {
  color: #4f5f67;
  font-size: clamp(0.95rem, 1.32vw, 1.08rem);
  line-height: 1.58;
  max-width: 700px;
  text-wrap: balance;
}

.dc-hero-ribbon {
  justify-self: center;
  background: rgba(255, 253, 248, 0.62);
  border-color: rgba(95, 143, 104, 0.2);
  border-radius: 999px;
  box-shadow: none;
  gap: 10px;
  margin-top: 0;
  padding: 7px 12px;
}

.dc-hero-ribbon span,
.dc-hero-ribbon small {
  font-size: 0.78rem;
  line-height: 1.2;
}

.dc-hero-ribbon span {
  align-items: center;
  display: inline-flex;
  gap: 7px;
}

.dc-hero-ribbon span::before {
  background: var(--dqa-sage-deep);
  border-radius: 999px;
  content: "";
  display: inline-block;
  height: 7px;
  width: 7px;
}

.dc-stepper {
  justify-self: center;
  margin-top: clamp(14px, 2.4vw, 26px);
  max-width: 680px;
}

.dc-stepper span {
  flex-basis: clamp(74px, 10vw, 112px);
  font-size: clamp(0.9rem, 1.48vw, 1.14rem);
}

.dc-stepper strong {
  font-size: clamp(1rem, 1.8vw, 1.28rem);
  height: clamp(44px, 5.2vw, 58px);
  width: clamp(44px, 5.2vw, 58px);
}

.dc-stepper-line {
  margin-top: clamp(21px, 2.6vw, 29px);
}

@media (max-width: 900px) {
  .dc-hero {
    min-height: 430px;
    padding: 24px 22px 32px;
  }

  .dc-hero h1 {
    font-size: clamp(2.15rem, 9.4vw, 3.45rem) !important;
  }

  .dc-brand-subtitle,
  .dc-hero-body {
    max-width: 620px;
  }
}

@media (max-width: 640px) {
  .dc-hero {
    min-height: 460px;
  }

  .dc-hero-top {
    grid-template-columns: 38px minmax(0, 1fr);
  }

  .dc-hero-ribbon {
    border-radius: 14px;
  }
}
"""
