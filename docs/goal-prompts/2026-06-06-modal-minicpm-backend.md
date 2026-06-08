# Modal MiniCPM Backend Goal Prompt

在 `/Users/junhaocheng/working-dir/ai-competitions/build-small-hackthon` 继续 Dream Customs。先读 `AGENTS.md`、`docs/spec.md`、`docs/prd.md`、`docs/handoff.md` 和 `docs/superpowers/plans/2026-06-06-modal-minicpm-backend.md`。

执行计划：用 `feature/modal-minicpm-backend` 分支，按任务勾选推进，部署 Modal 作为隐藏 MiniCPM 后端，HF Space 继续做 Gradio 前台。

硬约束：严禁把任何 token、endpoint secret、HF token、Modal token 写入仓库、日志、文档或截图；只记录变量名和非敏感 smoke 结果。开工前先确认 HF Space secrets 是否已存在；缺失或需要用户填写时立刻停下请求用户处理。默认 backend 保持 `demo`，`model` route 只能作为可切换真实推理路径，失败必须 fallback。MiniCPM-V-4.6 vision route 是硬验收，不允许用 demo vision 或跳过 vision smoke 代替；如果 GPU 不够，升级 Modal GPU，但不要换非 MiniCPM-V-4.6 模型。不要扩展到非 MiniCPM 模型；语音 ASR 不在本轮范围。

验收：每个任务完成后运行相应 pytest/smoke，更新计划 checkbox，分步提交；最后 push 分支并汇报 Modal text smoke、Modal MiniCPM-V-4.6 vision smoke、12 条 eval、Space model route 和 demo fallback 结果。
