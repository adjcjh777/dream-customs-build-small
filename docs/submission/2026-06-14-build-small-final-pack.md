# Build Small Final Pack - Dream QA

Date: 2026-06-14

## Current Links

- Space: https://huggingface.co/spaces/build-small-hackathon/dream-customs
- Direct app: https://build-small-hackathon-dream-customs.hf.space
- GitHub: https://github.com/adjcjh777/dream-customs-build-small
- Performance QA baseline: HF Space main `60a11f36082f4117a5dbcc9f2b9200f97318e666` with app code from GitHub `0272c67b1862ac8ac4294f6945e937c5f60d38cf`.
- Submission materials branch: `origin/feature/mimo-asr-modal`. Re-check the current HF Space main SHA tomorrow before final submission because README/material-only commits change the Space SHA.

## Official Submission Checklist

- Gradio app hosted in the official Build Small Hugging Face organization.
- Demo video showing the app and why it is useful.
- Social media post about the app.
- README links to the demo video and social media post.
- README frontmatter tags for tracks and badges.
- Short README explanation of the idea, how it was built, and the tech used.

## Track And Badge Targets

- Primary track: Thousand Token Wood.
- Secondary track: Backyard AI.
- Sponsor fit: OpenBMB, Modal, OpenAI Codex.
- Bonus fit: Off Brand, Best Demo.
- Do not claim Tiny Titan because the ASR model is above 4B.

## Model Size Statement

All models are individually under the 32B rule:

- `openbmb/MiniCPM5-1B`: text dream Q&A and grounded Today Tip generation.
- `openbmb/MiniCPM-V-4.6`: image, sketch, and note clues.
- `XiaomiMiMo/MiMo-V2.5-ASR`: voice transcription only.

The app uses Hugging Face Space and Gradio as the public UI. Private Modal endpoints serve MiniCPM text, MiniCPM-V vision, and MiMo ASR when runtime secrets are configured. Secrets stay in Space/Modal runtime and are not committed.

## Final QA Snapshot

Verdict from tester: `PASS_WITH_ASR_RISK`.

- Text live feedback: PASS. `/agent_dream_qa` p50 was `9.868s`, max `9.895s` across three semantic gates.
- Image live feedback: PASS. Browser upload reached Clarify / Step 3 in `6.38s`.
- ASR live feedback: PASS for timely graceful feedback, risk for real transcription success. `/dream-asr` returned 9-10s graceful timeout in two samples but did not produce transcripts.
- Semantic safety: PASS. No known invented-anchor pollution in visible fields.
- Distress handling: PASS. Severe insomnia case showed `safety_note`.

Recommended demo path: text first, optional image upload second. Voice can be shown as available or mentioned as graceful fallback, but should not be the hero path until live transcription success is stable.

## Demo Video Shotlist

Target length: 45-75 seconds.

1. Open Dream QA live Space on mobile width or narrow desktop.
2. Show the four steps: Record, Clarify, Answer, Tip.
3. Select "A friend misunderstood me" or type a short dream about a dead phone and elevator.
4. Click "Ask one question".
5. Show grounded anchors and the one gentle follow-up.
6. Click "Skip and generate tip" or answer one line.
7. Show the Morning Ticket with one grounded Today Tip.
8. Optional quick image moment: upload a small sketch and show that image clues become part of the same intake.
9. Close with safety boundary: not therapy, not prophecy, one gentle morning tip.

## X Draft

Dream QA / The Morning Question Desk is my #BuildSmall project: record a fresh dream, answer or skip one gentle question, and leave with a grounded Morning Ticket - one Today Tip tied to concrete details from the dream.

Not therapy. Not prophecy. Just a small-model morning desk for the half-awake minute.

Built with Gradio on Hugging Face Spaces, MiniCPM5-1B + MiniCPM-V-4.6, MiMo-V2.5-ASR, and Modal-hosted endpoints.

Space: https://huggingface.co/spaces/build-small-hackathon/dream-customs

#Gradio #HuggingFace #MiniCPM #Modal #OpenBMB

## Instagram Caption

Some dreams leave behind only a few strange pieces: an elevator, a room, a dead phone, a question you did not know how to ask.

Dream QA / The Morning Question Desk helps you record the dream, answer or skip one gentle follow-up, and leave with a Morning Ticket: one grounded Today Tip connected to a real detail from what you described.

Not diagnosis. Not prophecy. A small-model morning ritual for the half-awake minute.

Built for the Build Small Hackathon with Gradio, Hugging Face Spaces, MiniCPM, MiMo ASR, and Modal.

## Chinese Social Draft

Dream QA / 梦境问答台 is live for #BuildSmall: 说出一个刚醒来的梦，回答或跳过一个温和追问，然后拿到一张 grounded Morning Ticket：一个引用梦里具体细节的 Today Tip。

不是诊断，不是预言，只是小模型帮你把半醒时的疑问放稳一点。

Built with Gradio on Hugging Face Spaces, MiniCPM5-1B + MiniCPM-V-4.6, MiMo-V2.5-ASR, and Modal.

Space: https://huggingface.co/spaces/build-small-hackathon/dream-customs

## Tomorrow's Final Steps

1. Record or select the final demo video.
2. Upload the video publicly or keep the repo `videos/` file as the demo asset if accepted.
3. Publish the X or Instagram post.
4. Replace the README demo/social placeholders with final public URLs.
5. Re-run final smoke: full pytest, Today Tip eval, live `/config`, text/image browser path, and a quick semantic safety case.
6. Submit the Space URL, demo video URL, and social post URL.
