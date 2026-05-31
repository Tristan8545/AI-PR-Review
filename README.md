# AI PR Review Assistant

AI PR Review Assistant 是一个面向 GitHub Pull Request 的 AI 代码评审辅助工具。用户输入 GitHub PR 链接后，系统会自动获取 PR 变更，结合规则扫描、上下文增强和 DeepSeek 大模型分析，生成 PR 变更总结、风险代码识别、Review 建议和测试建议，帮助开发者提升代码评审效率与质量。

## 作品提交信息

- 仓库地址：[https://github.com/Tristan8545/AI-PR-Review](https://github.com/Tristan8545/AI-PR-Review)
- Demo 视频：待补充，请将 bilibili、网盘或其他可访问平台的视频链接放在这里
- 技术方向：AI PR Review 助手

## 核心功能

- 解析 GitHub PR URL，自动获取 PR 标题、描述、分支、changed files 和 diff patch。
- 基于文件路径、diff 内容和变更规模进行规则风险扫描。
- 获取关键变更文件完整内容、局部函数/代码块上下文和相关测试文件，提升模型上下文理解能力。
- 调用 DeepSeek OpenAI 兼容接口生成结构化 Review 结果。
- 对 AI 输出进行二次过滤、去重和规则兜底，降低误报与漏报。
- 使用进程内缓存优化重复分析同一 PR 的响应速度。
- Web 页面支持 loading 状态、最近分析记录、一键复制 Review Markdown、文件级折叠展示。

## 技术栈与依赖

- Python 3.11+
- FastAPI：Web 服务框架
- Jinja2：HTML 模板渲染
- httpx：调用 GitHub API 和 DeepSeek API
- python-dotenv：读取本地 `.env`
- pydantic：数据结构校验
- pytest：单元测试

所有第三方依赖已在 [requirements.txt](requirements.txt) 中列明。

## 原创功能说明

本项目原创实现包括：

- GitHub PR URL 解析器
- GitHub PR 数据整合与 changed files 获取
- 规则风险分析器
- 分层上下文构建策略
- diff 变更行解析与 Python AST 局部函数上下文提取
- 相关测试文件路径推测与内容获取
- DeepSeek Review Prompt 与结构化输出解析
- Review 结果质量守卫：过滤、去重、规则兜底
- PR Review 结果缓存
- Web 结果展示、一键复制 Markdown、最近分析记录和文件折叠视图

未复用个人历史项目代码。

## 快速开始

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload
```

访问：

```text
http://127.0.0.1:8000
```

## 环境变量

项目已内置比赛演示用 DeepSeek API Key，评委无需额外配置即可体验真实 AI Review。也可以通过本地 `.env` 覆盖默认配置。

```text
GITHUB_TOKEN=
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
DEMO_MODE=false
MAX_CONTEXT_FILES=5
MAX_FILE_CHARS=12000
MAX_TEST_FILES=3
CACHE_TTL_SECONDS=600
CACHE_MAX_ITEMS=32
```

说明：

- `GITHUB_TOKEN`：可选，用于提高 GitHub API 访问额度或访问授权仓库。请只在本地 `.env` 中配置，不要提交到仓库。
- `DEEPSEEK_API_KEY`：可选，不配置时使用项目内置比赛演示 Key。
- `DEEPSEEK_MODEL`：默认 `deepseek-v4-flash`，也可以切换为 `deepseek-v4-pro`。
- `DEMO_MODE`：设为 `true` 时强制使用 Demo 模式。
- `MAX_CONTEXT_FILES`：最多获取多少个关键变更文件的完整内容。
- `MAX_FILE_CHARS`：单个完整文件内容最多发送多少字符给模型。
- `MAX_TEST_FILES`：最多自动获取多少个相关测试文件。
- `CACHE_TTL_SECONDS`：同一个 PR 分析结果的内存缓存时间。
- `CACHE_MAX_ITEMS`：最多缓存多少个 PR 分析结果。

## 使用方式

1. 启动服务。
2. 打开首页。
3. 输入 GitHub PR URL，例如：

```text
https://github.com/owner/repo/pull/123
```

4. 点击“开始分析”。
5. 查看 PR 变更总结、风险代码识别、Review 建议和测试建议。
6. 可点击“复制 Review Markdown”，将结果粘贴到 GitHub PR 评论中。

如果暂时不想请求真实仓库，可以点击“使用内置 Demo 数据”体验完整流程。

## 系统架构

详细设计见 [docs/architecture.md](docs/architecture.md)。

核心流程：

```text
GitHub PR URL
-> GitHub API 获取 PR 元数据和 diff
-> 规则风险分析
-> 分层上下文构建
-> DeepSeek Review
-> Review 质量守卫
-> Web 展示
```

## 模型选择

项目使用 DeepSeek OpenAI 兼容接口，base URL 为 `https://api.deepseek.com`。

默认模型选择 `deepseek-v4-flash`，主要考虑：

- 成本较低，适合比赛 Demo 和频繁调试。
- 响应速度较快。
- 对 PR 摘要、风险识别、Review 建议生成等轻量评审任务已经足够。

如果需要更强推理能力，可以通过 `DEEPSEEK_MODEL=deepseek-v4-pro` 切换。

## 上下文获取方式

系统不会把整个仓库一次性发送给模型，而是构建分层上下文：

- PR 标题、描述、作者、分支。
- changed files 列表、增删行数和 diff patch。
- 规则扫描命中的风险提示。
- PR head 分支上关键变更文件的完整内容。
- diff 变更行附近的局部代码上下文。
- Python 文件使用 AST 定位变更所在函数或类，其他语言回退到上下文窗口。
- 根据源码路径自动猜测并获取相关测试文件。

这样可以在上下文理解、响应速度、模型成本之间取得平衡。

## 误报与漏报控制

降低误报：

- Prompt 要求只评论本次 diff 中新增或修改的代码。
- 输出必须包含文件、原因、建议和置信度。
- 证据不足的问题降低风险等级和置信度。
- Review 后处理会过滤非本次变更文件、低置信度风险项，并对重复标题和重复建议去重。

降低漏报：

- 在 AI 前先用规则扫描敏感路径和危险代码模式。
- 对鉴权、Token、数据库、支付、密钥、测试删除等场景加权关注。
- 将规则命中结果一起交给模型，让模型重点分析。
- 如果模型漏掉规则命中的风险，后处理会把规则发现补回结果列表，作为人工 Review 的兜底提醒。

## 响应速度设计

- 通过 `MAX_FILES`、`MAX_PATCH_CHARS`、`MAX_CONTEXT_FILES` 控制上下文规模。
- 对同一个 PR URL 使用进程内 TTL 缓存，重复分析时直接返回缓存结果。
- 缓存命中时结果模式会显示 `+cache`，便于 Demo 时说明性能优化是否生效。

## 持续交付与 PR 记录

项目按照小粒度 PR 持续开发，每个 PR 只做一件事，且 PR 描述包含功能描述、实现思路、测试方式和影响范围。

已合并 PR：

- [PR #1 Add full file content context for PR review](https://github.com/Tristan8545/AI-PR-Review/pull/1)
- [PR #2 Add local code context extraction](https://github.com/Tristan8545/AI-PR-Review/pull/2)
- [PR #3 Add related test file context](https://github.com/Tristan8545/AI-PR-Review/pull/3)
- [PR #4 Add review quality guardrails](https://github.com/Tristan8545/AI-PR-Review/pull/4)
- [PR #5 Add cached PR review results](https://github.com/Tristan8545/AI-PR-Review/pull/5)
- [PR #6 Improve review web experience](https://github.com/Tristan8545/AI-PR-Review/pull/6)

PR 模板见 [.github/pull_request_template.md](.github/pull_request_template.md)。

## 测试

```bash
pytest
```

当前测试覆盖：

- GitHub PR URL 解析
- 规则风险识别
- 上下文构建
- diff 行号解析
- Python 局部代码上下文提取
- 相关测试文件路径推测
- Review 质量守卫
- Review 缓存

## Demo 视频

待补充：请将 bilibili、网盘或其他可访问平台的视频链接放在这里。

## 未来扩展

- GitHub App 集成：一键把 Review 建议评论到 PR 的具体行。
- 仓库级代码索引：构建函数、类、调用关系索引，提升跨文件上下文理解。
- 多模型交叉检查：使用不同模型分别做安全、测试、可维护性审查，再合并结果。
- 团队规则配置：支持自定义敏感目录、必测模块、安全检查项和忽略规则。
- AI Agent 自动 Review 流程：让 Agent 自动拉取 PR、分文件分析、生成草稿评论、等待人工确认后发布。
- AI Agent 修复建议：对明确风险生成可选 patch，由开发者确认后自动提交到修复分支。
- AI Agent 学习团队偏好：根据人工采纳/驳回反馈调整规则权重和提示策略。

