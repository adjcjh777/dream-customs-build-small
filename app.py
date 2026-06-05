import os

import gradio as gr
from gradio_client import utils as gradio_client_utils

from dream_customs.app_logic import (
    add_material_action,
    answer_question_action,
    ask_another_question_action,
    draft_pact_action,
    initial_workbench_state,
    revise_pact_action,
    seal_pact_action,
    skip_question_action,
    start_declaration_action,
    start_new_action,
)


_ORIGINAL_SCHEMA_TO_TYPE = gradio_client_utils._json_schema_to_python_type


def _json_schema_to_python_type(schema, defs):
    # Gradio 4.44 can pass JSON Schema booleans here on newer dependency sets.
    if isinstance(schema, bool):
        return "Any" if schema else "None"
    return _ORIGINAL_SCHEMA_TO_TYPE(schema, defs)


gradio_client_utils._json_schema_to_python_type = _json_schema_to_python_type


CSS = """
:root {
  --dc-bg-night: oklch(0.145 0.030 238);
  --dc-bg-void: oklch(0.080 0.010 250);
  --dc-surface-ink: oklch(0.205 0.035 238);
  --dc-surface-raised: oklch(0.275 0.045 236);
  --dc-primary: oklch(0.690 0.105 232);
  --dc-primary-deep: oklch(0.510 0.115 234);
  --dc-coral: oklch(0.705 0.160 28);
  --dc-aurora: oklch(0.820 0.110 185);
  --dc-ink-main: oklch(0.965 0.010 235);
  --dc-ink-muted: oklch(0.760 0.030 232);
  --dc-border: oklch(0.430 0.055 235);
  --dc-warning: oklch(0.760 0.150 75);
  --dc-radius-sm: 6px;
  --dc-radius-md: 10px;
  --dc-radius-lg: 14px;
}

html,
body,
.gradio-container {
  background:
    radial-gradient(circle at 8% 0%, oklch(0.690 0.105 232 / 0.20), transparent 30rem),
    radial-gradient(circle at 80% 12%, oklch(0.820 0.110 185 / 0.13), transparent 26rem),
    linear-gradient(180deg, var(--dc-bg-void), var(--dc-bg-night) 34%, var(--dc-bg-void));
  color: var(--dc-ink-main);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-kerning: normal;
}

.gradio-container {
  max-width: none !important;
}

.gradio-container .main,
.gradio-container .wrap {
  max-width: none !important;
}

.dc-app-shell {
  gap: 16px !important;
  margin: 0 auto;
  max-width: 1440px;
  min-height: 100vh;
  padding: 16px;
}

.dc-session-store {
  display: none !important;
}

.dc-statusbar {
  align-items: center;
  background:
    linear-gradient(135deg, oklch(0.205 0.035 238 / 0.96), oklch(0.145 0.030 238 / 0.96)),
    url("/file=docs/design/assets/dream-customs-probe-night-desk.png");
  background-position: center;
  background-size: cover;
  border: 1px solid var(--dc-border);
  border-radius: var(--dc-radius-lg);
  display: grid;
  gap: 16px;
  grid-template-columns: minmax(280px, 1fr) auto minmax(260px, 0.8fr);
  min-height: 108px;
  overflow: hidden;
  padding: 16px;
  position: relative;
}

.dc-statusbar::before {
  background: linear-gradient(90deg, oklch(0.080 0.010 250 / 0.88), oklch(0.145 0.030 238 / 0.72));
  content: "";
  inset: 0;
  position: absolute;
}

.dc-statusbar > * {
  position: relative;
  z-index: 1;
}

.dc-brand-lockup {
  align-items: center;
  display: flex;
  gap: 12px;
}

.dc-brand-mark {
  align-items: center;
  background: var(--dc-primary-deep);
  border: 1px solid var(--dc-primary);
  border-radius: var(--dc-radius-md);
  color: var(--dc-ink-main);
  display: inline-flex;
  flex: 0 0 auto;
  font-size: 0.875rem;
  font-weight: 760;
  height: 44px;
  justify-content: center;
  letter-spacing: 0;
  width: 44px;
}

.dc-brand-lockup h1 {
  color: var(--dc-ink-main);
  font-size: 1.35rem;
  font-weight: 760;
  letter-spacing: 0;
  line-height: 1.15;
  margin: 0;
  text-wrap: balance;
}

.dc-brand-lockup p,
.dc-timeline-head p {
  color: var(--dc-ink-muted);
  font-size: 0.92rem;
  line-height: 1.45;
  margin: 4px 0 0;
  max-width: 68ch;
}

.dc-phase-rail {
  background: oklch(0.080 0.010 250 / 0.58);
  border: 1px solid oklch(0.430 0.055 235 / 0.72);
  border-radius: 999px;
  display: flex;
  gap: 4px;
  padding: 4px;
}

.dc-phase-rail span,
.dc-system-status span {
  border-radius: 999px;
  color: var(--dc-ink-muted);
  font-size: 0.78rem;
  font-weight: 680;
  letter-spacing: 0;
  line-height: 1.2;
  padding: 8px 10px;
  white-space: nowrap;
}

.dc-phase-rail .is-active {
  background: var(--dc-primary-deep);
  color: var(--dc-ink-main);
}

.dc-system-status {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: flex-end;
}

.dc-system-status span {
  background: oklch(0.080 0.010 250 / 0.62);
  border: 1px solid oklch(0.430 0.055 235 / 0.62);
}

.dc-main-grid {
  align-items: stretch !important;
  display: grid !important;
  gap: 16px !important;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 420px);
}

.dc-timeline-column,
.dc-inspector-column {
  min-width: 0 !important;
}

.dc-timeline-shell,
.dc-inspector,
.dc-composer-panel {
  background: oklch(0.205 0.035 238 / 0.96);
  border: 1px solid var(--dc-border);
  border-radius: var(--dc-radius-lg);
  color: var(--dc-ink-main);
}

.dc-timeline-shell {
  min-height: 480px;
  padding: 18px;
}

.dc-timeline-head {
  align-items: start;
  display: flex;
  gap: 16px;
  justify-content: space-between;
  margin-bottom: 14px;
}

.dc-timeline-head h2,
.dc-inspector h2 {
  color: var(--dc-ink-main);
  font-size: 1.25rem;
  font-weight: 740;
  letter-spacing: 0;
  line-height: 1.2;
  margin: 0;
  text-wrap: balance;
}

.dc-timeline-head > span,
.dc-inspector-kicker,
.dc-permit-row span {
  color: var(--dc-aurora);
  font-size: 0.8rem;
  font-weight: 720;
  letter-spacing: 0;
}

.dc-evidence-tray {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0 0 16px;
}

.dc-evidence-chip {
  align-items: center;
  background: oklch(0.145 0.030 238);
  border: 1px solid oklch(0.430 0.055 235 / 0.84);
  border-radius: 999px;
  color: var(--dc-ink-main);
  display: inline-flex;
  font-size: 0.83rem;
  font-weight: 650;
  gap: 8px;
  line-height: 1.2;
  padding: 8px 10px;
}

.dc-chip-dot {
  background: var(--dc-ink-muted);
  border-radius: 999px;
  display: inline-block;
  height: 7px;
  width: 7px;
}

.dc-evidence-chip.is-extracted .dc-chip-dot,
.dc-evidence-chip.is-selected .dc-chip-dot {
  background: var(--dc-aurora);
}

.dc-evidence-chip.is-failed {
  border-color: oklch(0.705 0.160 28 / 0.72);
}

.dc-evidence-chip.is-failed .dc-chip-dot {
  background: var(--dc-coral);
}

.dc-timeline-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dc-timeline-event {
  background: oklch(0.145 0.030 238 / 0.82);
  border: 1px solid oklch(0.430 0.055 235 / 0.72);
  border-radius: var(--dc-radius-md);
  padding: 14px;
}

.dc-timeline-event h3 {
  color: var(--dc-ink-main);
  font-size: 1rem;
  font-weight: 720;
  line-height: 1.25;
  margin: 6px 0 0;
}

.dc-timeline-event p,
.dc-inspector p,
.dc-inspector li {
  color: var(--dc-ink-muted);
  font-size: 0.95rem;
  line-height: 1.55;
  margin: 8px 0 0;
}

.dc-event-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.dc-event-meta span {
  background: oklch(0.275 0.045 236 / 0.88);
  border: 1px solid oklch(0.430 0.055 235 / 0.64);
  border-radius: 999px;
  color: var(--dc-aurora);
  font-size: 0.75rem;
  font-weight: 680;
  padding: 5px 8px;
}

.dc-timeline-event.is-user {
  background: oklch(0.275 0.045 236 / 0.92);
}

.dc-timeline-event.is-pact {
  border-color: oklch(0.705 0.160 28 / 0.72);
}

.dc-timeline-event.is-error {
  background: oklch(0.705 0.160 28 / 0.11);
  border-color: oklch(0.705 0.160 28 / 0.72);
}

.dc-inspector {
  min-height: 480px;
  padding: 18px;
}

.dc-inspector.is-sealed {
  border-color: var(--dc-coral);
}

.dc-inspector-kicker {
  margin-bottom: 10px;
}

.dc-permit-row {
  align-items: center;
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.dc-inspector dl {
  display: grid;
  gap: 8px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin: 16px 0;
}

.dc-inspector dl div {
  background: oklch(0.145 0.030 238 / 0.82);
  border: 1px solid oklch(0.430 0.055 235 / 0.66);
  border-radius: var(--dc-radius-md);
  padding: 10px;
}

.dc-inspector dt,
.dc-inspector h3 {
  color: var(--dc-aurora);
  font-size: 0.78rem;
  font-weight: 720;
  letter-spacing: 0;
  margin: 0;
}

.dc-inspector dd {
  color: var(--dc-ink-main);
  font-size: 0.92rem;
  font-weight: 680;
  margin: 4px 0 0;
}

.dc-inspector section {
  border-top: 1px solid oklch(0.430 0.055 235 / 0.6);
  padding: 12px 0;
}

.dc-inspector ul {
  margin: 8px 0 0;
  padding-left: 18px;
}

.dc-support-note,
.dc-inline-notice {
  background: oklch(0.705 0.160 28 / 0.13);
  border: 1px solid oklch(0.705 0.160 28 / 0.72);
  border-radius: var(--dc-radius-md);
  color: var(--dc-ink-main);
  line-height: 1.45;
  padding: 12px 14px;
}

.dc-inline-notice {
  background: oklch(0.275 0.045 236 / 0.94);
  border-color: oklch(0.430 0.055 235 / 0.76);
}

.dc-inline-notice.is-error {
  background: oklch(0.705 0.160 28 / 0.13);
  border-color: oklch(0.705 0.160 28 / 0.72);
}

.dc-inline-notice.is-sealed {
  border-color: var(--dc-coral);
}

.dc-composer-panel {
  bottom: 12px;
  padding: 14px;
  position: sticky;
  z-index: 5;
}

.dc-composer-panel textarea,
.dc-composer-panel input,
.dc-composer-panel select,
.dc-composer-panel label,
.dc-composer-panel .wrap,
.dc-composer-panel .block,
.dc-composer-panel .input-container,
.dc-composer-panel .container {
  border-radius: var(--dc-radius-md) !important;
  font-size: 1rem !important;
}

.dc-composer-panel .block,
.dc-composer-panel .container,
.dc-composer-panel .input-container,
.dc-composer-panel .wrap.default {
  background: oklch(0.205 0.035 238) !important;
  border-color: oklch(0.430 0.055 235 / 0.72) !important;
  color: var(--dc-ink-main) !important;
}

.dc-composer-panel .upload-container,
.dc-composer-panel .image-container,
.dc-composer-panel .audio-container,
.dc-composer-panel .upload-container button,
.dc-composer-panel .audio-container button {
  background: oklch(0.145 0.030 238) !important;
  border-color: oklch(0.430 0.055 235 / 0.72) !important;
  color: var(--dc-ink-muted) !important;
}

.dc-composer-panel .upload-container button,
.dc-composer-panel .audio-container button {
  border: 1px dashed oklch(0.430 0.055 235 / 0.82) !important;
}

.dc-composer-panel .source-selection button {
  background: oklch(0.080 0.010 250) !important;
  border: 1px solid oklch(0.430 0.055 235 / 0.72) !important;
  color: var(--dc-aurora) !important;
}

.dc-composer-panel svg {
  color: var(--dc-aurora) !important;
  stroke: currentColor !important;
}

.dc-composer-panel label,
.dc-composer-panel .label-wrap span {
  color: var(--dc-ink-main) !important;
  font-weight: 680 !important;
}

.dc-composer-panel textarea,
.dc-composer-panel input,
.dc-composer-panel select {
  background: oklch(0.145 0.030 238) !important;
  color: var(--dc-ink-main) !important;
}

.dc-composer-panel textarea::placeholder,
.dc-composer-panel input::placeholder {
  color: var(--dc-ink-muted) !important;
  opacity: 1 !important;
}

.dc-composer-panel button {
  border-radius: var(--dc-radius-md) !important;
  font-weight: 720 !important;
  min-height: 44px;
}

.dc-action-row button {
  background: oklch(0.275 0.045 236) !important;
  border: 1px solid oklch(0.430 0.055 235 / 0.82) !important;
  color: var(--dc-ink-main) !important;
}

.dc-action-row button:hover {
  border-color: var(--dc-primary) !important;
}

.dc-primary,
.dc-primary button {
  background: var(--dc-primary-deep) !important;
  border: 1px solid var(--dc-primary) !important;
  color: var(--dc-ink-main) !important;
}

.dc-seal-button,
.dc-seal-button button {
  background: var(--dc-coral) !important;
  border: 1px solid var(--dc-coral) !important;
  color: var(--dc-bg-void) !important;
}

.dc-action-row {
  align-items: stretch !important;
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 8px !important;
}

.dc-action-row > * {
  min-width: 148px !important;
}

.dc-sealed-output {
  margin-bottom: 16px;
}

.dc-diagnostics textarea,
.dc-diagnostics code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace !important;
}

*:focus-visible {
  outline: 2px solid var(--dc-primary) !important;
  outline-offset: 2px !important;
}

@media (max-width: 980px) {
  .dc-statusbar {
    grid-template-columns: 1fr;
  }

  .dc-system-status {
    justify-content: flex-start;
  }

  .dc-main-grid {
    grid-template-columns: 1fr;
  }

  .dc-inspector {
    min-height: auto;
  }
}

@media (max-width: 620px) {
  .dc-app-shell {
    padding: 10px;
  }

  .dc-statusbar,
  .dc-timeline-shell,
  .dc-inspector,
  .dc-composer-panel {
    border-radius: var(--dc-radius-md);
  }

  .dc-brand-lockup {
    align-items: flex-start;
  }

  .dc-brand-lockup h1 {
    font-size: 1.1rem;
  }

  .dc-phase-rail {
    overflow-x: auto;
  }

  .dc-timeline-head,
  .dc-permit-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .dc-inspector dl {
    grid-template-columns: 1fr;
  }

  .dc-action-row > * {
    min-width: 100% !important;
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.001ms !important;
    scroll-behavior: auto !important;
    transition-duration: 0.001ms !important;
  }
}

/* V3 rescue: first-screen trust, real phase actions, and no empty panel cliffs. */
:root {
  --dc-lamp: oklch(0.825 0.105 78);
  --dc-plum: oklch(0.265 0.055 312);
  --dc-warm-line: oklch(0.680 0.070 62);
}

.gradio-container {
  min-height: auto !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
}

.dc-app-shell {
  gap: 12px !important;
  min-height: auto;
  padding: 14px clamp(10px, 2vw, 22px) 18px;
}

.dc-statusbar {
  background:
    linear-gradient(110deg, oklch(0.080 0.010 250 / 0.92), oklch(0.265 0.055 312 / 0.70)),
    url("/file=docs/design/assets/dream-customs-probe-night-desk.png");
  background-position: center 42%;
  background-size: cover;
  border-color: oklch(0.680 0.070 62 / 0.42);
  grid-template-columns: minmax(260px, 1fr) minmax(260px, auto);
  min-height: auto;
  padding: 14px 16px;
}

.dc-statusbar::before {
  background:
    radial-gradient(circle at 18% 18%, oklch(0.825 0.105 78 / 0.16), transparent 18rem),
    linear-gradient(90deg, oklch(0.080 0.010 250 / 0.90), oklch(0.145 0.030 238 / 0.66));
}

.dc-brand-mark {
  background: linear-gradient(135deg, var(--dc-primary-deep), oklch(0.265 0.055 312));
  border-color: oklch(0.825 0.105 78 / 0.58);
}

.dc-system-status span {
  background: oklch(0.080 0.010 250 / 0.72);
  border-color: oklch(0.680 0.070 62 / 0.34);
}

.dc-stage-nav {
  align-items: stretch !important;
  background: oklch(0.145 0.030 238 / 0.92);
  border: 1px solid oklch(0.430 0.055 235 / 0.70);
  border-radius: var(--dc-radius-lg);
  display: grid !important;
  gap: 8px !important;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  padding: 8px;
}

.dc-stage-nav button {
  background: oklch(0.205 0.035 238) !important;
  border: 1px solid oklch(0.430 0.055 235 / 0.78) !important;
  border-radius: var(--dc-radius-md) !important;
  color: var(--dc-ink-main) !important;
  font-weight: 760 !important;
  min-height: 42px !important;
  white-space: normal !important;
}

.dc-stage-nav button:hover {
  background: oklch(0.275 0.045 236) !important;
  border-color: var(--dc-primary) !important;
}

.dc-stage-nav .dc-stage-seal button {
  border-color: oklch(0.705 0.160 28 / 0.72) !important;
}

.dc-focus-grid {
  align-items: start !important;
  display: grid !important;
  gap: 14px !important;
  grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.65fr);
}

.dc-declaration-column,
.dc-side-rail {
  min-width: 0 !important;
}

.dc-side-rail {
  gap: 12px !important;
}

.dc-composer-panel {
  background:
    radial-gradient(circle at 0% 0%, oklch(0.825 0.105 78 / 0.10), transparent 18rem),
    linear-gradient(145deg, oklch(0.205 0.035 238 / 0.98), oklch(0.265 0.055 312 / 0.38));
  border-color: oklch(0.680 0.070 62 / 0.38);
  bottom: auto;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.24);
  padding: 16px;
  position: relative;
}

.dc-composer-head {
  align-items: end;
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-bottom: 12px;
}

.dc-composer-head h2 {
  color: var(--dc-ink-main);
  font-size: 1.18rem;
  line-height: 1.18;
  margin: 0;
}

.dc-composer-head p {
  color: var(--dc-ink-muted);
  font-size: 0.92rem;
  line-height: 1.45;
  margin: 4px 0 0;
}

.dc-trust-pill {
  background: oklch(0.825 0.105 78 / 0.12);
  border: 1px solid oklch(0.825 0.105 78 / 0.40);
  border-radius: 999px;
  color: oklch(0.920 0.055 78);
  flex: 0 0 auto;
  font-size: 0.78rem;
  font-weight: 760;
  padding: 8px 10px;
}

.dc-declaration-row {
  align-items: stretch !important;
  display: grid !important;
  gap: 10px !important;
  grid-template-columns: minmax(0, 1fr) minmax(168px, 210px);
}

.dc-primary-stack {
  display: grid !important;
  gap: 8px !important;
}

.dc-primary-stack button {
  background: oklch(0.205 0.035 238) !important;
  border: 1px solid oklch(0.430 0.055 235 / 0.78) !important;
  color: var(--dc-ink-main) !important;
  min-height: 52px !important;
  white-space: normal !important;
}

.dc-primary-stack .dc-primary,
.dc-primary-stack .dc-primary button {
  background: var(--dc-primary-deep) !important;
  border-color: var(--dc-primary) !important;
  color: var(--dc-ink-main) !important;
}

.dc-primary-stack .dc-seal-button,
.dc-primary-stack .dc-seal-button button {
  background: var(--dc-coral) !important;
  border-color: var(--dc-coral) !important;
  color: var(--dc-bg-void) !important;
}

.dc-evidence-grid {
  align-items: stretch !important;
  display: grid !important;
  gap: 10px !important;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(170px, 220px);
}

.dc-route-row,
.dc-followup-grid {
  display: grid !important;
  gap: 10px !important;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.dc-secondary-actions {
  align-items: stretch !important;
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 8px !important;
}

.dc-secondary-actions > * {
  flex: 1 1 140px !important;
  min-width: 132px !important;
}

.dc-secondary-actions button {
  background: oklch(0.205 0.035 238) !important;
  border: 1px solid oklch(0.430 0.055 235 / 0.78) !important;
  color: var(--dc-ink-main) !important;
  min-height: 42px !important;
  white-space: normal !important;
}

.dc-secondary-actions button:hover {
  background: oklch(0.275 0.045 236) !important;
  border-color: var(--dc-primary) !important;
}

.dc-timeline-shell,
.dc-inspector {
  min-height: auto;
}

.dc-timeline-shell {
  padding: 16px;
}

.dc-inspector {
  background:
    radial-gradient(circle at 100% 0%, oklch(0.825 0.105 78 / 0.07), transparent 14rem),
    oklch(0.205 0.035 238 / 0.96);
  padding: 16px;
}

.dc-inspector dl {
  margin: 12px 0;
}

.dc-timeline-list {
  gap: 8px;
}

.dc-sealed-output:empty {
  display: none !important;
}

.dc-composer-panel .block,
.dc-composer-panel .container,
.dc-composer-panel .input-container,
.dc-composer-panel .wrap,
.dc-composer-panel .wrap.default,
.dc-composer-panel .wrap.svelte-1cl284s {
  background: oklch(0.130 0.024 238) !important;
  border-color: oklch(0.680 0.070 62 / 0.34) !important;
}

.dc-composer-panel textarea,
.dc-composer-panel input,
.dc-composer-panel select,
.dc-composer-panel [role="combobox"] {
  background: oklch(0.105 0.018 245) !important;
  border-color: oklch(0.430 0.055 235 / 0.82) !important;
  color: var(--dc-ink-main) !important;
}

.dc-composer-panel .upload-container,
.dc-composer-panel .image-container,
.dc-composer-panel .audio-container,
.dc-composer-panel .upload-container button,
.dc-composer-panel .audio-container button {
  background: oklch(0.105 0.018 245) !important;
  border-color: oklch(0.680 0.070 62 / 0.28) !important;
  color: var(--dc-ink-muted) !important;
}

.dc-composer-panel .image-container,
.dc-composer-panel .audio-container {
  min-height: 112px !important;
}

.dc-composer-panel label,
.dc-composer-panel .label-wrap span,
.dc-composer-panel [data-testid="block-label"] {
  color: oklch(0.900 0.020 235) !important;
}

.dc-composer-panel .label-wrap {
  background: oklch(0.130 0.024 238) !important;
  border: 1px solid oklch(0.680 0.070 62 / 0.30) !important;
  border-radius: 999px !important;
}

.dc-composer-panel label.float {
  background: oklch(0.130 0.024 238) !important;
  border-color: oklch(0.680 0.070 62 / 0.34) !important;
  color: oklch(0.900 0.020 235) !important;
}

.dc-composer-panel .label-wrap svg {
  color: var(--dc-aurora) !important;
}

.options,
.option,
ul.options,
.dropdown-options {
  background: oklch(0.130 0.024 238) !important;
  color: var(--dc-ink-main) !important;
}

.options li,
.option {
  color: var(--dc-ink-main) !important;
}

.dc-diagnostics,
.dc-examples {
  margin-top: 2px;
}

@media (max-width: 980px) {
  .dc-focus-grid {
    grid-template-columns: 1fr;
  }

  .dc-stage-nav {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .dc-declaration-row {
    grid-template-columns: 1fr;
  }

  .dc-primary-stack {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .dc-evidence-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 620px) {
  *,
  *::before,
  *::after {
    box-sizing: border-box !important;
  }

  html,
  body,
  .gradio-container,
  .dc-app-shell {
    max-width: 100vw !important;
    overflow-x: hidden !important;
  }

  .gradio-container,
  .gradio-container .main,
  .gradio-container .wrap,
  .gradio-container .contain {
    margin-left: 0 !important;
    margin-right: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
  }

  .dc-app-shell {
    margin: 0 !important;
    padding: 10px !important;
    width: 100vw !important;
  }

  .dc-statusbar,
  .dc-stage-nav,
  .dc-focus-grid,
  .dc-composer-panel,
  .dc-timeline-shell,
  .dc-inspector {
    max-width: 100% !important;
    min-width: 0 !important;
    width: 100% !important;
  }

  .dc-statusbar {
    grid-template-columns: 1fr;
  }

  .dc-brand-lockup,
  .dc-brand-lockup > div,
  .dc-system-status {
    min-width: 0 !important;
  }

  .dc-brand-lockup p {
    max-width: 100% !important;
    overflow-wrap: anywhere;
  }

  .dc-brand-lockup h1 {
    font-size: 1rem;
    overflow-wrap: anywhere;
  }

  .dc-system-status {
    justify-content: flex-start;
  }

  .dc-system-status span {
    font-size: 0.74rem;
    padding: 7px 8px;
    white-space: normal;
  }

  .dc-stage-nav button {
    min-width: 0 !important;
  }

  .dc-composer-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .dc-stage-nav {
    gap: 6px !important;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    padding: 6px;
  }

  .dc-stage-nav button {
    font-size: 0.86rem !important;
    min-height: 40px !important;
    padding-left: 6px !important;
    padding-right: 6px !important;
  }

  .dc-composer-panel {
    padding: 14px;
  }

  .dc-primary-stack button {
    min-height: 48px !important;
  }

  .dc-primary-stack .dc-draft-button,
  .dc-primary-stack .dc-seal-button {
    display: none !important;
  }

  .dc-composer-panel textarea {
    min-height: 116px !important;
  }

  .dc-primary-stack,
  .dc-route-row,
  .dc-followup-grid {
    grid-template-columns: 1fr;
  }

  .dc-secondary-actions > * {
    flex-basis: 100% !important;
  }
}
"""


def _outputs(
    session_state,
    status_html,
    timeline_html,
    inspector_html,
    sealed_html,
    debug_json,
    notice_html,
):
    return [session_state, status_html, timeline_html, inspector_html, sealed_html, debug_json, notice_html]


def build_demo() -> gr.Blocks:
    with gr.Blocks(css=CSS, title="Dream Customs") as demo:
        session_state = gr.Textbox(label="Session manifest", show_label=False, elem_classes=["dc-session-store"])
        with gr.Column(elem_classes=["dc-app-shell"]):
            status_html = gr.HTML()

            with gr.Row(elem_classes=["dc-stage-nav"]):
                declare_phase_btn = gr.Button("Declare")
                inspect_phase_btn = gr.Button("Inspect")
                draft_phase_btn = gr.Button("Draft")
                seal_phase_btn = gr.Button("Seal", elem_classes=["dc-stage-seal"])

            with gr.Row(elem_classes=["dc-focus-grid"]):
                with gr.Column(scale=7, elem_classes=["dc-declaration-column"]):
                    with gr.Column(elem_classes=["dc-composer-panel"]):
                        gr.HTML(
                            """
<div class="dc-composer-head">
  <div>
    <h2>File the dream fragment here</h2>
    <p>Start with text. Add a sketch, voice note, or mood only if it helps.</p>
  </div>
  <span class="dc-trust-pill">Private by default</span>
</div>
""".strip()
                        )
                        notice_html = gr.HTML()
                        with gr.Row(elem_classes=["dc-declaration-row"]):
                            dream_text = gr.Textbox(
                                label="Dream material",
                                lines=5,
                                value="我梦见一部迟到的电梯，按钮都融化了，我一直到不了 14 楼。",
                                placeholder="Type the dream, a fragment, or a new piece of material.",
                            )
                            with gr.Column(elem_classes=["dc-primary-stack"]):
                                send_btn = gr.Button("Send to customs", elem_classes=["dc-primary"])
                                draft_btn = gr.Button("Draft pact", elem_classes=["dc-draft-button"])
                                seal_btn = gr.Button("Seal today's pact", elem_classes=["dc-seal-button"])
                        with gr.Row(elem_classes=["dc-evidence-grid"]):
                            image_input = gr.Image(label="Attach image", type="filepath", height=132)
                            audio_input = gr.Audio(label="Record voice", type="filepath")
                            mood = gr.Dropdown(
                                label="Mood chip",
                                choices=["foggy", "anxious", "curious", "tired", "restless", "calm"],
                                value="foggy",
                            )
                        with gr.Row(elem_classes=["dc-route-row"]):
                            text_backend = gr.Dropdown(
                                label="Text route",
                                choices=["demo", "model", "ollama"],
                                value="demo",
                            )
                            vision_backend = gr.Dropdown(
                                label="Vision route",
                                choices=["demo", "model", "ollama"],
                                value="demo",
                            )
                        with gr.Row(elem_classes=["dc-followup-grid"]):
                            answer_text = gr.Textbox(
                                label="Answer to the clerk",
                                lines=2,
                                value="我想和它结盟，但今天只想完成一件很小的事。",
                                placeholder="Answer a customs question, or leave blank and skip.",
                            )
                            revision_request = gr.Textbox(
                                label="Revision request",
                                lines=2,
                                value="Make it gentler and more specific for today.",
                                placeholder="Try: make it stranger, make it gentler, or make the action smaller.",
                            )
                        with gr.Row(elem_classes=["dc-secondary-actions"]):
                            add_btn = gr.Button("Add material")
                            ask_btn = gr.Button("Ask another question")
                            answer_btn = gr.Button("Answer question")
                            skip_btn = gr.Button("Skip question")
                            revise_btn = gr.Button("Revise pact")
                            new_btn = gr.Button("Start new")

                with gr.Column(scale=4, elem_classes=["dc-side-rail"]):
                    inspector_html = gr.HTML()
                    sealed_html = gr.HTML(elem_classes=["dc-sealed-output"])

            timeline_html = gr.HTML()

            with gr.Accordion("Diagnostics", open=False, elem_classes=["dc-diagnostics"]):
                debug_json = gr.Code(label="Session state", language="json")

            with gr.Accordion("Examples", open=False, elem_classes=["dc-examples"]):
                gr.Examples(
                    examples=[
                        [
                            "梦见一间便利店漂在海上，收银员让我用旧日历付款。",
                            "curious",
                            "我想知道它到底在保护什么。",
                        ],
                        [
                            "I found a tiny border checkpoint inside my pillow. The officer stamped my hand with blue ink.",
                            "restless",
                            "I want a small action that makes tomorrow less loud.",
                        ],
                    ],
                    inputs=[dream_text, mood, answer_text],
                )

        outputs = _outputs(session_state, status_html, timeline_html, inspector_html, sealed_html, debug_json, notice_html)
        demo.load(initial_workbench_state, outputs=outputs, api_name=False)

        declare_phase_btn.click(
            add_material_action,
            inputs=[session_state, dream_text, image_input, audio_input, mood, text_backend, vision_backend],
            outputs=outputs,
            api_name=False,
        )
        inspect_phase_btn.click(
            ask_another_question_action,
            inputs=[session_state, text_backend, vision_backend],
            outputs=outputs,
            api_name=False,
        )
        draft_phase_btn.click(
            draft_pact_action,
            inputs=[session_state, text_backend, vision_backend],
            outputs=outputs,
            api_name=False,
        )
        seal_phase_btn.click(
            seal_pact_action,
            inputs=[session_state, text_backend, vision_backend],
            outputs=outputs,
            api_name=False,
        )
        send_btn.click(
            start_declaration_action,
            inputs=[session_state, dream_text, image_input, audio_input, mood, text_backend, vision_backend],
            outputs=outputs,
            api_name=False,
        )
        add_btn.click(
            add_material_action,
            inputs=[session_state, dream_text, image_input, audio_input, mood, text_backend, vision_backend],
            outputs=outputs,
            api_name=False,
        )
        ask_btn.click(
            ask_another_question_action,
            inputs=[session_state, text_backend, vision_backend],
            outputs=outputs,
            api_name=False,
        )
        answer_btn.click(
            answer_question_action,
            inputs=[session_state, answer_text, text_backend, vision_backend],
            outputs=outputs,
            api_name=False,
        )
        skip_btn.click(
            skip_question_action,
            inputs=[session_state, text_backend, vision_backend],
            outputs=outputs,
            api_name=False,
        )
        draft_btn.click(
            draft_pact_action,
            inputs=[session_state, text_backend, vision_backend],
            outputs=outputs,
            api_name=False,
        )
        revise_btn.click(
            revise_pact_action,
            inputs=[session_state, revision_request, text_backend, vision_backend],
            outputs=outputs,
            api_name=False,
        )
        seal_btn.click(
            seal_pact_action,
            inputs=[session_state, text_backend, vision_backend],
            outputs=outputs,
            api_name=False,
        )
        new_btn.click(
            start_new_action,
            inputs=[text_backend, vision_backend],
            outputs=outputs,
            api_name=False,
        )

    return demo


demo = build_demo()


if __name__ == "__main__":
    allowed_paths = [os.path.abspath("docs/design/assets")]
    if os.getenv("SPACE_ID"):
        demo.launch(show_api=False, show_error=True, allowed_paths=allowed_paths)
    else:
        server_port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
        demo.launch(
            server_name="127.0.0.1",
            server_port=server_port,
            show_api=False,
            show_error=True,
            allowed_paths=allowed_paths,
        )
