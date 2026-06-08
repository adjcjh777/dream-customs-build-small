# Goal Prompt: Model-Led Pact V2

> Superseded on 2026-06-08: do not use this for new work unless the user explicitly revives the pact direction. Current source of truth is `docs/superpowers/plans/2026-06-08-dream-qa-refactor.md`.

Work in `/Users/junhaocheng/working-dir/ai-competitions/build-small-hackthon`.

Use the repo plan `docs/superpowers/plans/2026-06-08-model-led-pact-v2.md`. Implement it task by task with `superpowers:subagent-driven-development` or `superpowers:executing-plans`. Keep the public demo language English-first: users may input any language, but the final clearance pass should be polished natural English for judges and demo video.

Do not broaden beyond MiniCPM before exhausting the current pair:

- `openbmb/MiniCPM5-1B` owns dream brief, pact draft, critique, and rewrite.
- `openbmb/MiniCPM-V-4.6` owns visual witness reports.
- ASR remains transcription only.

Main acceptance case:

```text
I kept missing an elevator. The buttons melted like wax, and the floor number froze at 14.
```

The final card must not contain `the an`, `the the`, invented `lever`, diagnosis, prophecy, or frightening certainty. It must mention at least two concrete details from the dream, give one real next step for today, and include one harmless five-minute odd task grounded in the dream.

Before changes: confirm cwd, branch, remotes, and run `git pull`. During implementation: use tests first, keep commits small, and preserve text-only fallback. After implementation: run `.venv/bin/python -m pytest -q`, `git diff --check`, local Gradio smoke on port `7862`, push GitHub branch, then sync or prepare HF Space update. Stop and ask before exposing secrets, confirming paid deploy/build costs, force-pushing public Space `main`, or handling a manual PR merge.
