# Dream Customs Space Deployment Smoke

Date: 2026-06-05

## Scope

Goal for this pass: verify the current UI/UX V2 workbench locally, sync it to the Hugging Face Space if authorized, check the public Space with a browser, run a remote text-only queue prediction, and test hosted MiniCPM routes only if runtime secrets are present.

## Local Repo

- CWD verified: `/Users/junhaocheng/working-dir/ai-competitions/build-small-hackthon`.
- Branch verified: `feature/dream-customs-mvp`.
- `git pull --ff-only`: already up to date.
- `git remote -v` showed:
  - `origin`: `https://github.com/adjcjh777/dream-customs-build-small.git`
  - `space`: `https://huggingface.co/spaces/build-small-hackathon/dream-customs`

## Local Verification

- `.venv/bin/python -m pytest -q`: 31 passed.
- `python app.py` could not bind `7860` because another Python process was already listening there.
- Local app started with `GRADIO_SERVER_PORT=7861 .venv/bin/python app.py`.
- Browser smoke on `http://127.0.0.1:7861/` completed:
  - `Send to customs`
  - `Ask another question`
  - `Add material`
  - `Draft pact`
  - `Revise pact`
  - `Seal today's pact`
- Final local V2 state showed:
  - phase `Sealed`
  - permit `DC-DEMO-014`
  - 3 filed evidence items
  - 4 asked questions
  - alliance reading
  - today's suggestion
  - 5-minute task
  - contraband list
  - bedtime release
  - `SEALED` pact card
- Mobile viewport `390x844` remained readable.
- Diagnostics panel opened and showed sealed demo state. Ordinary-case safety fields were empty, and the persistent header copy still stated that this is playful reflection, not medical advice.

## Hugging Face Space Sync

- Space remote `main` was readable.
- Space `main` was on old app history and did not contain the V2 workbench.
- A non-force deployment path was attempted by cloning the Space repo to a temporary directory, copying only this repo's tracked files, committing a Space deployment commit, and pushing to `main`.
- The local temporary deployment commit was created as `3b18ee5 Deploy Dream Customs workbench UI`, but it was not accepted by Hugging Face.
- `git push origin main` in the temporary Space clone was rejected by HF:
  - `You are not authorized to push to this repo.`
- `huggingface-cli` was not installed locally, so no alternate authenticated HF CLI path was available in this environment.

Result: V2 workbench is not deployed to the public Space in this pass.

## Public Space Smoke

Checked URLs:

- `https://huggingface.co/spaces/build-small-hackathon/dream-customs`
- `https://build-small-hackathon-dream-customs.hf.space/`

Observed result:

- Public Space opened successfully.
- Direct hf.space app rendered the older one-shot UI, not the current V2 workbench.
- Existing old UI button `Stamp clearance` completed successfully in the browser.
- Old UI output included `Today's Pact`, permit `DC-DEMO-014`, suggestion, weird task, bedtime release, contraband, and `SEALED`.
- Mobile viewport `390x844` was readable for the currently deployed old app.
- Browser console showed one HF subdomain status request returning 400 and one Gradio warning about too many endpoint arguments; no blocker was observed for the old text-only demo output.

Remote queue check:

- `/config` returned Gradio `4.44.1`.
- Queued endpoint found: `run_customs_once`, `fn_index=0`.
- Raw `/queue/join` plus `/queue/data` text-only call completed with `process_completed`.
- Queue output returned 4 fields and a pact snippet containing `Dream visitor`, `Permit: DC-DEMO-014`, `Today's suggestion`, `Weird task`, and `Bedtime release`.
- `gradio_client.Client(...)` could not be used because the installed client failed while parsing the remote schema with `TypeError: argument of type 'bool' is not iterable`; raw queue protocol worked.

Result: current old public Space queue works, but the required V2 workbench public Space smoke remains blocked until HF push permission is available.

## Hosted MiniCPM Route

Runtime environment check:

- `DREAM_CUSTOMS_TEXT_ENDPOINT`: missing
- `DREAM_CUSTOMS_VISION_ENDPOINT`: missing
- `DREAM_CUSTOMS_HOSTED_TOKEN`: missing

Result: hosted MiniCPM text and vision route smoke was not run. No token or endpoint value was printed, stored, or committed.

## Next Step

Authenticate or grant push access for `https://huggingface.co/spaces/build-small-hackathon/dream-customs`, then push the current workbench files to Space `main` and rerun the V2 public Space browser and queue smoke.
