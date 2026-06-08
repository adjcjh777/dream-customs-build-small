# AGENTS.md - Dream QA / 梦境问答台

## 语言规则

- 默认使用中文回复用户。
- 面向评审/README/Space 展示的文字可以中英双语，但不要牺牲中文表达的清晰度。

## 项目定位

- 当前项目是 Build Small Hackathon 的 `Dream QA / 梦境问答台`，代码仓库和 Space 仍沿用 `Dream Customs` 名称以保持部署连续性。
- 核心定位：做一个循序渐进的解梦 Gradio app，帮助用户一步步说清梦境、表达疑惑、回答追问，最后得到一个温和的 `今日小 Tips`。
- `今日小 Tips` 可以是一个认真建议、一个用户未尝试过的小事，或一句关心用户的短句；它必须引用梦里的具体细节，不能变成泛泛鸡汤。
- 这不是心理诊断、医疗建议、治疗工具、占卜工具或宿命论解释器。

## 竞赛约束

- 目标交付：Gradio app on Hugging Face Space。
- 模型总参数必须 <= 32B。
- 优先叙事赛道：An Adventure in Thousand Token Wood。
- 次级叙事：Backyard AI，因为项目来自真实睡眠/做梦困扰。
- demo 必须能在短视频中快速展示：输入梦境，回答或跳过追问，获得今日小 Tips。

## 模型规则

- 首选模型组合：
  - `openbmb/MiniCPM-V-4.6`：图片、草图、便签、截图理解。
  - `openbmb/MiniCPM5-1B`：文本推理、追问生成、梦境解读草稿、结构化今日 Tips。
- 不要在 MiniCPM 路线未验证前扩展到任意其他小模型。
- 语音输入需要 ASR 适配器；ASR 只做转写，不承担梦境理解。
- 首版不要实现语音输出，避免扩大部署风险。

## 产品边界

- 必须支持文字输入。
- 应支持图片输入，用 MiniCPM-V-4.6 提取视觉线索。
- 应支持语音输入，通过小 ASR 适配器转成文本。
- 所有输入统一进入同一个梦境 intake，不要做成三套割裂产品。
- 用户流程必须是渐进式的：
  1. 记录梦境。
  2. 明确用户最想理解的问题。
  3. 生成 1-3 个温和追问。
  4. 用户回答、跳过或请求换个角度。
  5. 生成梦境解读草稿。
  6. 输出一个今日小 Tips。
- 输出必须包含：
  - `dream_summary` / 梦境摘要
  - `main_question` / 用户最想理解的问题
  - `dream_anchors` / 梦境具体线索
  - `followup_questions` / 追问
  - `user_answers` / 用户回答或跳过记录
  - `interpretation` / 非确定性的解读草稿
  - `today_tip` / 今日小 Tips
  - `tiny_action` / 可选的小行动
  - `caring_note` / 可选的关心语句
  - `safety_note` / 必要时的安全提示

## 安全规则

- 不做心理疾病诊断。
- 不声称梦境有唯一含义。
- 不输出恐吓性、宿命论、神秘绝对化内容。
- 不把梦解释成“预兆”“证明”“创伤证据”或医学结论。
- 普通输出使用“也许”“可以把它当作”“今天先试试”这类非确定措辞。
- 如果用户表达自伤、伤人、长期严重失眠、无法正常生活或极强痛苦，必须显示寻求可信任的人或专业支持的提示。

## 文档优先级

实现前先阅读：

1. `docs/handoff.md`
2. `docs/spec.md`
3. `docs/prd.md`
4. `PRODUCT.md`
5. `DESIGN.md`
6. `docs/superpowers/plans/2026-06-08-dream-qa-refactor.md`
7. `docs/superpowers/plans/2026-06-08-dream-qa-refactor-doc-plan.md`

旧的 pact/customs 计划、smoke 和概念页是历史记录。除非用户明确要求复盘历史，否则不要再把 permit、contraband、sealed pact 当作新实现目标。

## 开发流程

- 修改或实验前先确认工作目录是 `/Users/junhaocheng/working-dir/ai-competitions/build-small-hackthon`。
- 当前目录可能位于父级 `vlarepo` git root 下；不要误推到 VLA remote。
- 如果需要正式提交，先确认是否已初始化/切换到 Dream Customs 专用仓库。
- 在仓库归属未确认前，可以本地写文件，但不要强行 `git add` / `git commit` / `git push` 到父级 VLA 仓库。
- 如果建立新功能分支，使用 `feature/xxx` 命名。
- 用户要求修改完成后，默认不仅推送 GitHub 分支，也要同步提交到 Hugging Face Space，并完成可用的 merge / 部署路径；不要只停在本地或 GitHub 分支。
- 同步 HF Space 前先确认 `space` remote 指向 `build-small-hackathon/dream-customs`，并复核当前分支与提交 SHA，避免误推到其他 Space 或父级仓库。
- 如果 HF Space 同步涉及密钥、账单、权限弹窗、强制覆盖公开 `main`、或无法自动 merge 的 PR/Discussion，则先说明具体阻塞并请求用户确认；不要打印或保存任何 token。

## 实现原则

- 先用 fake clients 打通 schema、safety、render、pipeline 和 Gradio UI。
- 核心测试通过后再接真实 MiniCPM 模型。
- 所有模型输出都必须经过 schema 校验。
- JSON 解析失败时必须有修复或降级路径。
- Text-only path 必须永远可用，作为 demo fallback。
- Gradio 页面应优先移动端可用，因为用户可能在手机上记录梦。
- 今日 Tips 必须有梦境锚点，不能是“多休息、多喝水、保持积极”这类脱离梦境的通用话。

## 验收命令

基础验收：

```bash
python -m pytest -q
python app.py
```

人工验收：

- 输入一段文字梦境后，app 能提出至少一个相关追问。
- 用户可以回答追问，也可以跳过。
- 上传一张草图或便签后，视觉线索进入同一个 intake。
- 上传/录制语音后，有转写或清晰降级提示。
- 最终输出包含梦境摘要、解读草稿和一个今日小 Tips。
- 今日小 Tips 引用至少一个具体梦境细节。
- 输出不包含诊断、恐吓、预言或医疗化建议。
- 页面在手机宽度下可读。
