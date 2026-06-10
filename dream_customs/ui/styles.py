CSS = """
:root {
  --dc-bg: #f6f3ec;
  --dc-paper: #fffdf8;
  --dc-green: #4caf6e;
  --dc-green-deep: #3d9a5c;
  --dc-green-soft: #e8f5e9;
  --dc-ink: #2d3436;
  --dc-muted: #636e72;
  --dc-line: #dfe6e9;
  --dc-card-bg: #ffffff;
  --dc-shadow: 0 2px 12px rgba(0,0,0,0.05);
  --dc-radius: 12px;
  --dc-radius-sm: 8px;
  --dc-amber: #f5e6c8;
  --dc-amber-border: #ead8aa;
  --dc-prose-width: 60ch;
}

html,
body,
.gradio-container {
  background: var(--dc-bg) !important;
  color: var(--dc-ink) !important;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Noto Sans SC", sans-serif !important;
}

.gradio-container {
  max-width: none !important;
  padding: 0 !important;
}

.gradio-container .main,
.gradio-container .wrap {
  background: transparent !important;
}

/* ── Top bar (minimal) ── */
.dc-topbar {
  align-items: center;
  background: var(--dc-paper);
  border-bottom: 1px solid var(--dc-line);
  display: flex;
  gap: 12px;
  justify-content: space-between;
  padding: 12px 32px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-sizing: border-box;
}

.dc-topbar-left {
  align-items: center;
  display: flex;
  gap: 10px;
}

.dc-topbar-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dc-topbar-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--dc-ink);
}

.dc-topbar-greeting {
  display: none;
}

.dc-leaf-icon {
  align-items: center;
  background: var(--dc-green);
  border-radius: 8px;
  color: #fff;
  display: flex;
  font-size: 0.95rem;
  height: 32px;
  justify-content: center;
  width: 32px;
}

.dc-topbar-buttons {
  display: flex;
  gap: 6px;
  align-items: center;
  padding: 0;
  background: transparent;
  border: none;
  min-height: unset;
}

.dc-language-switch {
  margin-right: 0;
}

.dc-language-switch,
.dc-language-switch > div,
.dc-language-switch .wrap,
.dc-language-switch .container {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}

.dc-language-switch [role="radiogroup"],
.dc-language-switch .wrap {
  display: inline-flex !important;
  gap: 6px !important;
}

.dc-language-switch label {
  font-size: 0.82rem !important;
  color: var(--dc-ink) !important;
}

/* ── App shell ── */
.dc-app-shell {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ── Main layout: 2-column ── */
.dc-main-layout {
  display: grid;
  grid-template-columns: minmax(0, 2.2fr) minmax(280px, 1fr);
  gap: 32px;
  max-width: 1080px;
  margin: 20px auto;
  padding: 0 32px;
  width: 100%;
  box-sizing: border-box;
  align-items: start;
}

/* ── Step pill bar (replaces left sidebar) ── */
.dc-step-bar {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 8px 0;
  margin-bottom: 12px;
}

.dc-step-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--dc-line);
  transition: background 0.3s;
  display: inline-block;
}

.dc-step-dot.active {
  background: var(--dc-green);
  box-shadow: 0 0 0 3px var(--dc-green-soft);
}

.dc-step-dot.done {
  background: var(--dc-green);
}

.dc-step-label {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--dc-muted);
  display: inline;
}

.dc-step-label.active {
  color: var(--dc-ink);
  font-weight: 600;
}

.dc-step-sep {
  color: var(--dc-line);
  font-size: 0.75rem;
}

/* ── Left sidebar: hidden ── */
.dc-left-rail {
  display: none !important;
}

.dc-left-sidebar {
  display: none !important;
}

/* ── Center: main flow ── */
.dc-flow-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 680px;
}

.dc-center,
.dc-center-preview {
  background: var(--dc-card-bg);
  border: 1px solid var(--dc-line);
  border-radius: var(--dc-radius);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dc-center {
  background: transparent !important;
  border: 0;
  gap: 16px;
  min-height: unset;
}

.dc-center-preview {
  min-height: unset;
  flex: 0;
}

.dc-center-header {
  display: none;
}

/* ── Welcome greeting (large, centered) ── */
.dc-welcome-greeting {
  text-align: center;
  padding: 40px 0 24px;
}

.dc-welcome-greeting h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--dc-ink);
  margin: 0 0 8px;
}

.dc-welcome-greeting p {
  font-size: 0.95rem;
  color: var(--dc-muted);
  max-width: 40ch;
  margin: 0 auto;
  line-height: 1.5;
}

.dc-welcome-bubble {
  display: none;
}

/* ── Chat input row ── */
.dc-chat-input-row {
  display: flex;
  gap: 8px;
  align-items: flex-end;
  margin-bottom: 8px;
}

.dc-chat-input-row .dc-dream-text {
  flex: 1;
}

.dc-send-btn {
  min-width: 72px !important;
  max-width: 100px !important;
  height: 40px !important;
  font-size: 0.88rem !important;
  padding: 0 16px !important;
  border-radius: var(--dc-radius-sm) !important;
  white-space: nowrap;
  flex-shrink: 0;
}

/* ── Chip row ── */
.dc-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.dc-chip-btn {
  background: var(--dc-paper);
  border: 1px solid var(--dc-line);
  border-radius: 20px;
  color: var(--dc-muted);
  cursor: pointer;
  font-size: 0.82rem;
  padding: 6px 14px;
  transition: all 0.2s;
  min-height: unset;
}

.dc-chip-btn:hover {
  background: var(--dc-green-soft);
  border-color: var(--dc-green);
  color: var(--dc-green-deep);
}

.dc-chip-btn:focus-visible {
  outline: 2px solid var(--dc-green);
  outline-offset: 2px;
}

.dc-chip-btn:active {
  transform: scale(0.97);
}

.dc-chip-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Image upload (always visible pill) ── */
.dc-attachment-drawer {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin-top: 0 !important;
}

.dc-image-upload-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px dashed var(--dc-line);
  border-radius: 20px;
  background: var(--dc-paper);
  color: var(--dc-muted);
  font-size: 0.85rem;
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s;
  margin-bottom: 8px;
}

.dc-image-upload-pill:hover {
  border-color: var(--dc-green);
  color: var(--dc-green);
}

/* ── Question card (chat-bubble style) ── */
.dc-question {
  padding: 0;
}

.dc-question-card {
  background: linear-gradient(135deg, #fffaf0, #fff6df);
  border: 1px solid var(--dc-amber-border);
  border-radius: 12px 12px 12px 4px;
  padding: 20px;
  max-width: var(--dc-prose-width);
}

.dc-question-kicker {
  color: var(--dc-green-deep);
  display: block;
  font-size: 0.78rem;
  font-weight: 600;
  margin-bottom: 8px;
}

.dc-question-card h2 {
  color: var(--dc-ink) !important;
  font-size: 1.2rem;
  line-height: 1.3;
  margin: 0 0 8px;
}

.dc-question-card p {
  color: var(--dc-ink);
  line-height: 1.6;
  margin: 0;
}

.dc-question-original {
  border-left: 3px solid var(--dc-green);
  margin-top: 12px !important;
  padding-left: 12px;
}

.dc-question-original span {
  color: var(--dc-green-deep);
  display: block;
  font-size: 0.78rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.dc-question-note {
  color: var(--dc-muted) !important;
  margin-top: 12px !important;
}

.dc-question-actions {
  display: flex !important;
  gap: 10px !important;
  grid-template-columns: unset !important;
  margin-top: 12px;
}

/* ── Result card / Today Tip ── */
.dc-stage,
.dc-dev {
  background: var(--dc-card-bg) !important;
  border: 1px solid var(--dc-line) !important;
  border-radius: var(--dc-radius) !important;
  box-shadow: var(--dc-shadow);
  padding: 20px;
}

.dc-stage,
.dc-stage > div,
.dc-stage .form,
.dc-stage .wrap,
.dc-stage .container,
.dc-stage [data-testid="block-info"],
.dc-stage [data-testid="textbox"],
.dc-stage .block {
  background: var(--dc-card-bg) !important;
}

.dc-stage .form {
  border: 0 !important;
  box-shadow: none !important;
}

.dc-stage::before,
.dc-hero::after,
.dc-pass-card::after {
  display: none !important;
}

.dc-card {
  padding: 0;
}

.dc-tip-card {
  background: linear-gradient(160deg, #fffdf8 0%, #fff9ed 100%);
  border: 1px solid var(--dc-amber-border);
  border-left: 4px solid var(--dc-amber);
  border-radius: var(--dc-radius);
  padding: 28px 24px;
}

.dc-tip-card h3 {
  color: var(--dc-ink);
  font-size: 1.35rem;
  font-weight: 700;
  margin: 0 0 12px;
}

.dc-tip-card p {
  color: var(--dc-ink);
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0 0 10px;
}

.dc-pass-card {
  background: var(--dc-card-bg);
  border: 1px solid var(--dc-line);
  border-radius: var(--dc-radius);
  line-height: 1.65;
  padding: 20px;
}

.dc-pass-topline {
  color: var(--dc-green-deep);
  display: flex;
  font-size: 0.86rem;
  font-weight: 600;
  justify-content: space-between;
  margin-bottom: 12px;
}

.dc-pass-card h2 {
  color: var(--dc-ink) !important;
  font-size: 1.8rem;
  line-height: 1;
  margin: 0 0 6px;
}

.dc-pass-risk {
  color: var(--dc-green-deep);
  font-weight: 500;
  margin: 0 0 14px;
}

.dc-pass-card section {
  border-top: 1px solid var(--dc-line);
  padding: 12px 0;
}

.dc-pass-card h3 {
  color: var(--dc-green-deep) !important;
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
  border: 2px solid var(--dc-green);
  border-radius: 999px;
  color: var(--dc-green-deep);
  display: inline-block;
  font-weight: 600;
  margin-top: 10px;
  padding: 7px 12px;
}

.dc-pass-safety {
  background: #fff7e6;
  border: 1px solid #f0d88a !important;
  border-radius: var(--dc-radius-sm);
  margin: 10px 0;
  padding: 12px !important;
}

.dc-actions {
  display: flex !important;
  gap: 10px !important;
  grid-template-columns: unset !important;
  flex-wrap: wrap;
}

.dc-hidden-text textarea {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
  min-height: 130px !important;
}

/* ── Context rail (right sidebar) ── */
.dc-right-sidebar {
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: sticky;
  top: 72px;
  align-self: flex-start;
}

.dc-right-card {
  background: var(--dc-card-bg);
  border: 1px solid var(--dc-line);
  border-radius: var(--dc-radius);
  padding: 16px;
  min-height: unset;
}

.dc-right-card h3 {
  color: var(--dc-ink);
  font-size: 0.92rem;
  font-weight: 600;
  margin: 0 0 10px;
}

.dc-clue-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
  max-height: 120px;
  overflow-y: auto;
  padding-right: 4px;
}

.dc-clue-tag {
  background: var(--dc-green-soft);
  border-radius: 8px;
  color: var(--dc-green-deep);
  cursor: default;
  font-size: 0.82rem;
  font-weight: 500;
  padding: 5px 10px;
  display: inline-block;
  user-select: none;
}

.dc-clue-tag:hover {
  background: var(--dc-green);
  color: #fff;
}

.dc-skeleton-line {
  background: linear-gradient(90deg, #f0f0f0 25%, #f8f8f8 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: dc-shimmer 1.5s infinite;
  border-radius: 4px;
  height: 14px;
  margin-bottom: 10px;
}

.dc-skeleton-line:nth-child(2) { width: 85%; }
.dc-skeleton-line:nth-child(3) { width: 65%; }

@keyframes dc-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@keyframes dc-pulse {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 0.4; }
}

.dc-draft-preview {
  color: var(--dc-ink);
  font-size: 0.9rem;
  line-height: 1.65;
  margin: 0 0 10px;
}

/* ── Buttons ── */
.dc-expand-btn {
  background: transparent;
  border: 1px solid var(--dc-line);
  border-radius: var(--dc-radius-sm);
  color: var(--dc-muted);
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 500;
  margin-top: 8px;
  padding: 6px 10px;
  text-align: center;
  width: auto;
  opacity: 1;
  transition: background 0.15s, box-shadow 0.15s, opacity 0.15s;
}

.dc-expand-btn:hover {
  background: var(--dc-green-soft);
  border-color: var(--dc-green);
  color: var(--dc-green-deep);
}

.dc-expand-btn:focus-visible {
  outline: 2px solid var(--dc-green);
  outline-offset: 2px;
}

.dc-expand-btn:active {
  transform: scale(0.98);
}

.dc-expand-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dc-save-btn {
  align-items: center;
  background: transparent;
  border: 1px solid var(--dc-line);
  border-radius: var(--dc-radius-sm);
  color: var(--dc-muted);
  cursor: pointer;
  display: flex;
  font-size: 0.78rem;
  gap: 4px;
  padding: 6px 10px;
  opacity: 1;
  transition: background 0.15s, box-shadow 0.15s, opacity 0.15s;
  width: auto;
}

.dc-save-btn:hover {
  background: var(--dc-green-soft);
  border-color: var(--dc-green);
  color: var(--dc-green-deep);
}

.dc-save-btn:focus-visible {
  outline: 2px solid var(--dc-green);
  outline-offset: 2px;
}

.dc-save-btn:active {
  transform: scale(0.98);
}

/* ── Topbar icon buttons ── */
.dc-icon-btn {
  background: transparent;
  border: 1px solid var(--dc-line);
  border-radius: var(--dc-radius-sm);
  color: var(--dc-ink);
  cursor: pointer;
  padding: 4px 8px;
  font-size: 1rem;
  min-width: 32px;
  min-height: 32px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, border-color 0.15s;
  box-sizing: border-box;
}

.dc-icon-btn:hover {
  background: var(--dc-green-soft);
  border-color: var(--dc-green);
}

.dc-icon-btn:focus-visible {
  outline: 2px solid var(--dc-green);
  outline-offset: 2px;
}

.dc-icon-btn:active {
  transform: scale(0.95);
}

/* ── Panel groups ── */
.dc-interpretation-panel,
.dc-history-panel-group,
.dc-notification-panel-group,
.dc-menu-panel-group {
  background: var(--dc-card-bg);
  border: 1px solid var(--dc-line);
  border-radius: var(--dc-radius-sm);
  padding: 14px;
  margin-top: 10px;
}

.dc-history-panel h4,
.dc-notification-panel h4 {
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0 0 10px;
  color: var(--dc-ink);
}

.dc-history-item {
  padding: 8px 0;
  border-bottom: 1px solid var(--dc-line);
}

.dc-menu-panel {
  background: var(--dc-card-bg);
  border: 1px solid var(--dc-line);
  border-radius: var(--dc-radius-sm);
  padding: 14px;
  margin-top: 10px;
}

/* ── Notice ── */
.dc-notice {
  background: var(--dc-green-soft);
  border: 1px solid rgba(76, 175, 110, 0.3);
  border-radius: var(--dc-radius-sm);
  color: #2d7a4f;
  font-size: 0.88rem;
  line-height: 1.5;
  margin: 0 0 14px;
  padding: 10px 14px;
}

.dc-notice.is-error {
  background: #fff0eb;
  border-color: #efb19d;
  color: #9f321c;
}

/* ── Status pill ── */
.dc-status-pill {
  background: var(--dc-green-soft);
  border-radius: 20px;
  color: var(--dc-green-deep);
  font-size: 0.78rem;
  font-weight: 600;
  padding: 4px 12px;
  display: inline-block;
}

/* ── Shared form styles ── */
.dc-stage textarea,
.dc-stage input,
.dc-stage select,
.dc-dev textarea,
.dc-dev input,
.dc-dev select {
  background: #fff !important;
  border-color: var(--dc-line) !important;
  border-radius: var(--dc-radius-sm) !important;
  color: var(--dc-ink) !important;
}

.dc-stage textarea::placeholder,
.dc-stage input::placeholder {
  color: var(--dc-muted) !important;
  opacity: 1 !important;
}

.dc-stage textarea:focus,
.dc-stage input:focus {
  border-color: var(--dc-green) !important;
  box-shadow: 0 0 0 2px rgba(76, 175, 110, 0.2) !important;
  outline: none !important;
}

button.primary:disabled {
  background: #b0bec5 !important;
  border-color: #b0bec5 !important;
  color: #fff !important;
  cursor: not-allowed !important;
  box-shadow: none !important;
}

.dc-stage .primary button,
.dc-stage button.primary,
button.primary {
  background: var(--dc-green) !important;
  border: 1px solid var(--dc-green-deep) !important;
  border-radius: var(--dc-radius-sm) !important;
  box-shadow: 0 2px 8px rgba(76, 175, 110, 0.15);
  color: #fff !important;
}

.dc-stage .secondary button,
.dc-stage button.secondary,
button.secondary {
  background: #fff !important;
  border: 1px solid var(--dc-line) !important;
  border-radius: var(--dc-radius-sm) !important;
  color: var(--dc-ink) !important;
}

.dc-stage .primary button:hover,
.dc-stage button.primary:hover,
button.primary:hover {
  background: var(--dc-green-deep) !important;
  box-shadow: 0 4px 12px rgba(76, 175, 110, 0.25);
}

.dc-stage .primary button:focus-visible,
.dc-stage button.primary:focus-visible,
button.primary:focus-visible {
  outline: 2px solid var(--dc-green-deep);
  outline-offset: 2px;
}

.dc-stage .primary button:active,
.dc-stage button.primary:active,
button.primary:active {
  transform: scale(0.98);
}

.dc-stage .primary button:disabled,
.dc-stage button.primary:disabled,
button.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}

.dc-stage .secondary button:hover,
.dc-stage button.secondary:hover,
button.secondary:hover {
  background: var(--dc-paper) !important;
  border-color: var(--dc-green) !important;
}

.dc-stage .secondary button:focus-visible,
.dc-stage button.secondary:focus-visible,
button.secondary:focus-visible {
  outline: 2px solid var(--dc-green);
  outline-offset: 2px;
}

.dc-stage .secondary button:active,
.dc-stage button.secondary:active,
button.secondary:active {
  transform: scale(0.98);
}

.dc-stage .secondary button:disabled,
.dc-stage button.secondary:disabled,
button.secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dc-stage button,
.dc-question-actions button,
.dc-actions button {
  border-radius: var(--dc-radius-sm) !important;
  font-weight: 600 !important;
  min-height: 40px !important;
}

.dc-processing-note {
  color: var(--dc-muted);
  font-size: 0.84rem;
  line-height: 1.45;
  margin: 8px 2px 0;
}

.dc-field-tip {
  color: var(--dc-muted);
  font-size: 0.82rem;
  line-height: 1.4;
  margin: 6px 0 0;
}

/* ── Side panel (advanced/dev) ── */
.dc-advanced-row {
  box-sizing: border-box;
  margin: 0 auto 28px;
  max-width: 1080px;
  padding: 0 32px;
  width: 100%;
}

.dc-advanced-row > .dc-side-panel {
  width: 100%;
}

.dc-side-panel {
  background: var(--dc-card-bg) !important;
  border: 1px solid var(--dc-line) !important;
  border-radius: var(--dc-radius) !important;
  box-shadow: var(--dc-shadow);
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px;
}

.dc-side-panel .wrap,
.dc-side-panel .container,
.dc-side-panel select {
  min-height: 48px !important;
}

.dc-side-stamp {
  background: var(--dc-green-soft);
  border: 1px solid rgba(76, 175, 110, 0.2);
  border-radius: var(--dc-radius-sm);
  color: var(--dc-green-deep);
  line-height: 1.6;
  padding: 14px;
  text-align: left;
}

.dc-side-stamp span,
.dc-side-stamp small {
  color: var(--dc-muted);
  font-size: 0.78rem;
}

.dc-side-stamp strong {
  color: var(--dc-green-deep);
  font-size: 1rem;
  display: block;
  margin: 4px 0;
}

.dc-section-title {
  align-items: center;
  color: var(--dc-ink);
  display: flex;
  font-weight: 600;
  gap: 10px;
  margin: 0 0 12px;
}

.dc-title-icon {
  align-items: center;
  background: var(--dc-green);
  border-radius: 50%;
  color: #fff;
  display: inline-flex;
  font-size: 0.85rem;
  font-weight: 700;
  height: 28px;
  justify-content: center;
  width: 28px;
}

.dc-title-icon strong {
  font-size: 0.92rem;
}

.dc-dev {
  background: rgba(255, 253, 248, 0.6) !important;
  border: 1px dashed var(--dc-line) !important;
  border-radius: var(--dc-radius-sm) !important;
  box-shadow: none;
  padding: 10px !important;
}

.dc-dev > button {
  color: var(--dc-muted) !important;
  font-size: 0.84rem !important;
  min-height: 40px !important;
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
  min-height: 40px !important;
}

.dc-dev label,
.dc-dev [data-testid="block-label"] {
  font-size: 0.78rem !important;
}

.dc-dev-advanced {
  background: transparent !important;
  border: 1px solid var(--dc-line) !important;
  border-radius: var(--dc-radius-sm) !important;
  margin-top: 10px;
}

.dc-submit-row .image-input,
.dc-submit-row [data-testid="image"] {
  border: 2px dashed var(--dc-line) !important;
  border-radius: var(--dc-radius-sm) !important;
  background: var(--dc-paper) !important;
  min-height: 60px !important;
}

.dc-submit-row .image-input:hover,
.dc-submit-row [data-testid="image"]:hover {
  border-color: var(--dc-green) !important;
  background: var(--dc-green-soft) !important;
}

footer.svelte-1rjryqp,
a.built-with[href*="gradio.app"] {
  display: none !important;
}

/* ── Mobile: stack columns ── */
@media (max-width: 900px) {
  .dc-main-layout {
    grid-template-columns: 1fr;
    gap: 14px;
    padding: 0 16px;
    margin: 12px auto;
  }

  .dc-topbar {
    padding: 10px 16px;
  }

  .dc-topbar-title {
    font-size: 0.95rem;
  }

  .dc-step-bar {
    gap: 10px;
    flex-wrap: wrap;
  }

  .dc-question-actions {
    flex-direction: column;
  }

  .dc-actions {
    flex-direction: column;
  }

  .dc-right-sidebar {
    position: static;
  }
}

@media (max-width: 480px) {
  .dc-main-layout {
    padding: 0 10px;
    gap: 10px;
    margin: 8px auto;
  }

  .dc-topbar {
    padding: 8px 10px;
  }

  .dc-welcome-greeting {
    padding: 24px 0 16px;
  }

  .dc-welcome-greeting h2 {
    font-size: 1.25rem;
  }

  .dc-actions {
    flex-direction: column;
  }
}
"""
