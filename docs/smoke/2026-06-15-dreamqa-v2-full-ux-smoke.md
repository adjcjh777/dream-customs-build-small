# Dream QA V2 Full UX Smoke - 2026-06-15

Controlling plan: `/tmp/dreamqa_v1_v2_agent_command_plan.md`.

## Scope

This smoke verifies the final Dream QA V2 local demo package for Build Small submission prep:

- Text input, image upload, voice input/fallback state, one grounded question, user answer, and final Morning Ticket are visible in each recorded flow.
- Final Today Tips use image-derived anchors plus the user's answer clue.
- Voice is represented honestly as a recoverable fallback when transcription is unavailable. No fake transcript is claimed.
- The final videos are local evidence assets; public/live Space acceptance still requires syncing the final commit to Hugging Face Space and re-smoking live runtime.

## Code And Runtime

- Branch: `feature/mimo-asr-modal`
- Base before this smoke: `c9a54a4 Fix Dream QA multimodal UX grounding`
- Smoke package commit: `efc02a838bdf6bc476e2c40cdc5ab2d3c33c46e2` (`Finalize Dream QA V2 demo evidence`), followed by an audit-fix commit that tightens ux02 tip grounding and ux03 question grounding.
- Local URL: `http://127.0.0.1:7862`
- Local recording backend: demo text/vision/ASR routes, with voice fallback shown in UI.
- ASR status: fallback only in these recordings. The UI displays `Voice was not transcribed. Type that fragment or try again.`

## Automated Checks

Commands run before recording:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/evaluate_today_tip_quality.py
git diff --check
```

Observed result:

- Full pytest: `182 passed, 6 warnings`
- Today Tip quality eval: `11/11`, `passes: true`
- `git diff --check`: clean

## V2 Video Evidence

| Case | Video | Duration | Evidence | Timeline | Final ticket | Verdict |
| --- | --- | ---: | --- | --- | --- | --- |
| ux01 train platform | `videos/2026-06-15-dreamqa-v2/ux01_full_ux.mp4` | 24.32s | `videos/2026-06-15-dreamqa-v2/ux01_evidence.json` | `videos/2026-06-15-dreamqa-v2/ux01_timeline.jpg` | `videos/2026-06-15-dreamqa-v2/ux01_final_ticket.png` | PASS |
| ux02 elevator buttons | `videos/2026-06-15-dreamqa-v2/ux02_full_ux.mp4` | 23.36s | `videos/2026-06-15-dreamqa-v2/ux02_evidence.json` | `videos/2026-06-15-dreamqa-v2/ux02_timeline.jpg` | `videos/2026-06-15-dreamqa-v2/ux02_final_ticket.png` | PASS |
| ux03 floating table | `videos/2026-06-15-dreamqa-v2/ux03_full_ux.mp4` | 23.36s | `videos/2026-06-15-dreamqa-v2/ux03_evidence.json` | `videos/2026-06-15-dreamqa-v2/ux03_timeline.jpg` | `videos/2026-06-15-dreamqa-v2/ux03_final_ticket.png` | PASS |

Each evidence JSON records:

- `videoPath`
- `duration`
- `questionVisibleForSeconds: 3.6`
- `finalTicketVisibleForSeconds: 4.3`
- `voiceEvidenceStatus`
- `finalAnchors`
- `todayTipText`
- assertions for answer clue grounding, demo-specific tip cue grounding, demo-specific question cue grounding, honest voice fallback, no template tip phrase, and no safety-boundary leak.

## Semantic Evidence

ux01 Today Tip:

> Connect train platform to the waking-life clue you named: "It feels like my real question is whether I am waiting for permission to choose a direction at work today". Use it as a tiny direction check today: write the work direction you named on one note, then choose one sign you can test before the day pulls away.

ux02 Today Tip:

> Connect melted elevator buttons to the work message pressure you named, without changing it into a different task. Write down the one thing the message needs to convey before deciding when to open or send it.

After the audit fix, the ux02 Today Tip text is:

> Connect melted elevator buttons to the work message pressure you named, without changing it into a different task. Use floor 14 in a puddle and the clock without hands as the boundary: write only what the message needs to convey before deciding when to open or send it.

ux03 Today Tip:

> Connect floating table to the waking-life clue you named: "I think the question is which small key to try first before the day gets busy". Use it as a morning key check: choose the one small key you named, try that before the day gets busy, and leave the other keys on the table for later.

Blocked terms checked across evidence:

- `reversible first step`
- `drawing showing`
- `various and a`
- old customs framing
- diagnosis / prophecy / fixed-meaning claims

Result: no blocked terms in the V2 evidence assertions.

Additional audit assertions:

- ux02 Today Tip text includes `floor 14 in a puddle`, `clock without hands`, and the message answer clue.
- ux03 question text includes `floating table`, `loose keys`, and `sunrise`.

## Remaining Release Steps

1. Commit and push this smoke package.
2. Send final SHA to tester for clean-worktree QA.
3. Sync final commit to Hugging Face Space after tester PASS.
4. Re-smoke live `/config`, text/image browser path, and one semantic safety case.
5. Add public demo video URL and social post URL to README/submission notes after publishing.
