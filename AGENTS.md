# AGENTS.md - Dream Customs / 梦境海关

## 语言规则

- 默认使用中文回复用户。
- 面向评审/README/Space 展示的文字可以中英双语，但不要牺牲中文表达的清晰度。

## 项目定位

- 当前项目是 Build Small Hackathon 的 `Dream Customs / 梦境海关`。
- 核心定位：帮用户和昨晚的梦结盟，把不安转成第二天的小建议，把怪梦转成一件有趣的小事。
- 这不是心理诊断、医疗建议或治疗工具。

## 竞赛约束

- 目标交付：Gradio app on Hugging Face Space。
- 模型总参数必须 <= 32B。
- 优先叙事赛道：An Adventure in Thousand Token Wood。
- 次级叙事：Backyard AI，因为项目来自真实睡眠/做梦困扰。
- demo 必须能在短视频中快速展示：输入梦境，获得今日盟约卡。

## 模型规则

- 首选模型组合：
  - `openbmb/MiniCPM-V-4.6`：图片、草图、便签、截图理解。
  - `openbmb/MiniCPM5-1B`：文本推理、梦境外交官人格、结构化输出和建议生成。
- 不要在 MiniCPM 路线未验证前扩展到任意其他小模型。
- 语音输入需要 ASR 适配器；ASR 只做转写，不承担梦境理解。
- 首版不要实现语音输出，避免扩大部署风险。

## 产品边界

- 必须支持文字输入。
- 应支持图片输入，用 MiniCPM-V-4.6 提取视觉线索。
- 应支持语音输入，通过小 ASR 适配器转成文本。
- 所有输入统一进入 `DreamIntake`，不要做成三套割裂产品。
- 输出必须包含：
  - dream visitor / 梦境来访者
  - permit id / 入境编号
  - contraband / 携带情绪违禁品
  - risk level / 风险等级
  - alliance reading / 结盟解读
  - practical suggestion / 今日认真建议
  - weird task / 5 分钟怪趣任务
  - bedtime release / 睡前放行仪式
  - safety note / 必要时的安全提示

## 安全规则

- 不做心理疾病诊断。
- 不声称梦境有唯一含义。
- 不输出恐吓性、宿命论、神秘绝对化内容。
- 普通输出使用“也许”“可以把它当作”“今天先试试”这类非确定措辞。
- 如果用户表达自伤、伤人、长期严重失眠、无法正常生活或极强痛苦，必须显示寻求可信任的人或专业支持的提示。

## 文档优先级

实现前先阅读：

1. `docs/spec.md`
2. `docs/prd.md`
3. `docs/handoff.md`
4. `docs/superpowers/plans/2026-06-05-dream-customs-mvp.md`
5. `docs/dream-customs-concept/index.html`

## 开发流程

- 修改或实验前先确认工作目录是 `/Users/junhaocheng/working-dir/ai-competitions/build-small-hackthon`。
- 当前目录可能位于父级 `vlarepo` git root 下；不要误推到 VLA remote。
- 如果需要正式提交，先确认是否已初始化/切换到 Dream Customs 专用仓库。
- 在仓库归属未确认前，可以本地写文件，但不要强行 `git add` / `git commit` / `git push` 到父级 VLA 仓库。
- 如果建立新功能分支，使用 `feature/xxx` 命名。

## 实现原则

- 先用 fake clients 打通 schema、safety、render、pipeline 和 Gradio UI。
- 核心测试通过后再接真实 MiniCPM 模型。
- 所有模型输出都必须经过 schema 校验。
- JSON 解析失败时必须有修复或降级路径。
- Text-only path 必须永远可用，作为 demo fallback。
- Gradio 页面应优先移动端可用，因为用户可能在手机上记录梦。

## 验收命令

基础验收：

```bash
python -m pytest -q
python app.py
```

人工验收：

- 输入一段文字梦境，能生成盟约卡。
- 上传一张草图或便签，视觉线索进入 `DreamIntake`。
- 上传/录制语音后，有转写或清晰降级提示。
- 输出不包含诊断、恐吓或医疗化建议。
- 页面在手机宽度下可读。
