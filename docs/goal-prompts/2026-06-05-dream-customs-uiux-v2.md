# Dream Customs UI/UX V2 Goal Prompt

在 `/Users/junhaocheng/working-dir/ai-competitions/build-small-hackthon` 继续 Dream Customs。先读 `AGENTS.md`、`PRODUCT.md`、`DESIGN.md`、`docs/design/2026-06-05-uiux-v2-brief.md`、`docs/superpowers/plans/2026-06-05-dream-customs-uiux-v2.md`。使用 `$impeccable craft Dream Customs UI/UX V2` 的思路实现，不要再做一页普通 Gradio 表单。

目标：把当前 one-shot app 改成 Codex app 风格的梦境海关工作台。核心布局为顶部状态栏、中心会话时间线、底部 multimodal composer、桌面右侧或移动端下方 pact inspector。用户必须能选择 `Add material`、`Ask another question`、`Draft pact`、`Revise pact`、`Seal today's pact`，而不是一次生成后结束。

设计：采用 `Night Desk` 方向，OKLCH 暗色产品界面，cobalt 主动作、aurora evidence 状态、coral seal 稀有强调。使用 `docs/design/assets/` 里的生成图作为氛围参考或空状态资源。避免 beige parchment、tarot、therapy intake、generic purple AI SaaS、side stripe、gradient text、过圆卡片和低对比灰字。

实现：先用 demo backend 打通 session state、schema、pipeline、UI 和测试，再接 hosted MiniCPM route。保留 text-only fallback。可以使用 Modal credits 做 MiniCPM 测试，HF credits 只在 Space 稳定运行需要时使用。不要把任何 token 写入 repo、日志或文档。

验收：`python -m pytest -q` 通过；本地 `python app.py` 可用；远端 Space queue prediction 可用；手机宽度可读；debug JSON 收进折叠 diagnostics；严重痛苦输入触发安全提示。完成后 commit、push，并更新计划 checkbox。
