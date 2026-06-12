# Modal Vision Sketch Evidence - 2026-06-12

Goal: verify whether Dream QA can use MiniCPM-V-4.6 to understand uploaded dream sketches, and clarify how text plus image should be merged.

## Test Assets

- Sea sketch: `docs/smoke/assets/dream_sketch_01_sea.png`
- Elevator sketch: `docs/smoke/assets/dream_sketch_02_elevator.png`
- Subway child sketch: `docs/smoke/assets/dream_sketch_03_subway_child.png`
- Raw Modal evidence: `docs/smoke/2026-06-12-modal-vision-sketch-evidence.json`
- Chrome local paste screenshot: `docs/smoke/assets/2026-06-12-chrome-local-image-paste-fallback.png`

## Chrome Local Upload Check

Local app URL: `http://127.0.0.1:7870`

Result:

- Native file chooser injection was blocked by the Chrome extension file-access permission.
- Clipboard paste into the Gradio image input worked. The page showed `Remove Image`, confirming the image slot received the sketch.
- Submitting the local page without Modal endpoint/token configured did not prove real MiniCPM-V behavior. The follow-up used fallback/demo visual clues (`melted elevator button`) instead of the pasted sea sketch.

Interpretation: the local Gradio image UI can receive images, but a local browser smoke without configured hosted endpoint/token only verifies upload plumbing. It must not be treated as evidence that MiniCPM-V understood the image.

## Real MiniCPM-V-4.6 Route

The three sketches were sent to the Modal vision endpoint through a temporary local runner. Secret handling: token was used only inside the Modal runner path; no token was printed, stored, or committed.

| Case | Expected visual markers | HTTP | Elapsed | Marker hits | Modal-V result |
| --- | --- | --- | ---: | --- | --- |
| `sea` | sea, wave, moon, person | 200 | 25.48s | sea, wave, moon | saw a sea under night, stick figure, waves, crescent moon, visible text `dark sea dream` |
| `elevator` | elevator, button, 14, melted | 200 | 5.55s | elevator, button, 14, melted | saw melted elevator buttons, two gray doors, visible text `14` |
| `subway_child` | subway, child, home, arrow | 200 | 5.62s | subway, child, home, arrow | saw a lost child at a subway station, subway sign, arrow, visible text `HOME ?` |

Conclusion: MiniCPM-V-4.6 did understand the low-resolution dream sketches and returned concrete visual evidence.

## Backend Fix Verified

Observed Modal response shape:

- The hosted endpoint returned `response` as a stringified Python dictionary.
- The useful assistant JSON was nested under `generated_text[-1].content`.
- Before this fix, Dream QA could treat that whole string as unparsed text and lose the structured witness report.

Fix:

- `HostedMiniCPMVisionClient` now extracts assistant content from stringified Modal pipeline payloads and message lists.
- Chinese Dream QA now localizes common English visual anchors from MiniCPM-V, so a Chinese user does not see awkward anchors like `dreamlike representation of a sea`.

Verification:

```bash
.venv/bin/python -m pytest -q tests/test_ollama_models.py tests/test_vision_witness.py tests/test_pipeline.py::test_visual_witness_clues_drive_questions_and_today_tip tests/test_pipeline.py::test_zh_text_and_image_keep_user_question_while_using_visual_anchors
.venv/bin/python -m py_compile dream_customs/models.py dream_customs/pipeline.py
```

Result: `21 passed in 0.12s`; `py_compile` passed.

## Text + Image Product Rule

When the user uploads both text and image:

1. User text owns the emotional question and intent. Example: `我想知道为什么它让我这么慌` becomes the main question.
2. Image contributes concrete anchors. Example: sea, waves, crescent moon, elevator button, subway sign, `HOME ?`.
3. The follow-up and Today Tip must combine them: answer the user's feeling first, then use the visual anchors as evidence.
4. If text and image conflict, do not force a single meaning. Ask one gentle clarification or phrase it as uncertainty.
5. Text-only remains the fallback; image failure must not block the user from getting a grounded response.
