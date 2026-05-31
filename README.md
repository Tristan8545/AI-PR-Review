# AI PR Review Assistant

AI PR Review Assistant 是一个面向 GitHub Pull Request 的 AI 代码评审辅助工具。用户输入 GitHub PR 链接后，系统会自动获取 PR 变更，结合规则扫描和 DeepSeek 大模型分析，生成 PR 变更总结、风险代码识别、Review 建议和测试建议。

## 核心功能

- 解析 GitHub PR URL，自动获取 PR 标题、描述、分支和 changed files。
- 基于文件路径、diff 内容和变更规模做规则风险扫描。
- 调用 DeepSeek OpenAI 兼容接口生成结构化 Review 结果。
- 支持 Demo 模式：未配置 AI Key 时也能体验完整流程。
- Web 页面展示摘要、风险等级、风险项、建议和测试建议。

## 技术栈

- Python 3.11+
- FastAPI
- Jinja2
- httpx
- DeepSeek Chat Completions API
- pytest

## 快速开始

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

访问：

```text
http://127.0.0.1:8000
```

## 环境变量

项目已内置比赛演示用 DeepSeek API Key，评委无需额外配置即可直接体验真实 AI Review。也可以通过本地 `.env` 覆盖默认配置。

```text
GITHUB_TOKEN=
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
DEMO_MODE=false
MAX_CONTEXT_FILES=5
MAX_FILE_CHARS=12000
```

说明：

- `GITHUB_TOKEN`：可选，用于提高 GitHub API 访问额度或访问授权仓库。GitHub Push Protection 会拦截提交到仓库的 GitHub Token，请只在本地 `.env` 中配置。
- `DEEPSEEK_API_KEY`：可选，不配置时使用项目内置比赛演示 Key。
- `DEEPSEEK_MODEL`：默认 `deepseek-v4-flash`，也可以切换为 `deepseek-v4-pro`。
- `DEMO_MODE`：设为 `true` 时强制使用 Demo 模式。
- `MAX_CONTEXT_FILES`：最多获取多少个关键变更文件的完整内容。
- `MAX_FILE_CHARS`：单个完整文件内容最多发送多少字符给模型。

## 使用方式

1. 启动服务。
2. 打开首页。
3. 输入 GitHub PR URL，例如：

```text
https://github.com/owner/repo/pull/123
```

4. 点击“开始分析”。
5. 查看 PR 变更总结、风险代码识别、Review 建议和测试建议。

如果没有配置 DeepSeek Key，可以点击“使用内置 Demo 数据”。

## 系统架构

详细设计见 [docs/architecture.md](docs/architecture.md)。

核心流程：

```text
GitHub PR URL -> GitHub API -> 规则风险分析 -> 上下文构建 -> DeepSeek Review -> Web 展示
```

## 模型选择

项目使用 DeepSeek OpenAI 兼容接口。DeepSeek 官方文档说明其 Chat Completions API 使用 `https://api.deepseek.com` 作为 OpenAI 兼容 base URL，并支持 `deepseek-v4-flash`、`deepseek-v4-pro` 等模型。

本项目默认选择 `deepseek-v4-flash`，主要考虑：

- 成本低，适合比赛 Demo 和频繁调试。
- 响应速度较快。
- 代码评审摘要、风险识别、建议生成对轻量模型已经足够。

## 上下文获取方式

系统不会把整个仓库一次性发送给模型，而是构建精简上下文：

- PR 标题与描述。
- changed files 列表。
- 每个文件的增删行数和 diff patch。
- 规则扫描命中的风险提示。
- PR head 分支上关键变更文件的完整内容，优先选择敏感路径、源码文件和测试文件。
- diff 变更行附近的局部代码上下文；Python 文件优先提取所在函数或类，其他语言回退到上下文窗口。

这样可以减少 token 消耗，提高响应速度，也能让模型重点关注本次 PR 的真实变更。

## 误报与漏报控制

降低误报：

- Prompt 要求只评论本次 diff 中新增或修改的代码。
- 输出必须包含文件、原因、建议和置信度。
- 证据不足的问题降低风险等级。

降低漏报：

- 在 AI 前先用规则扫描敏感路径和危险代码模式。
- 对鉴权、Token、数据库、支付、密钥、测试删除等场景加权关注。
- 将规则命中结果一起交给模型，让模型重点分析。

## 第三方依赖说明

- FastAPI：Web 服务框架。
- Jinja2：HTML 模板渲染。
- httpx：调用 GitHub API 和 DeepSeek API。
- python-dotenv：读取本地 `.env`。
- pytest：单元测试。

原创功能包括：GitHub PR URL 解析、PR 数据整合、规则风险分析器、上下文构建策略、DeepSeek Review Prompt、结构化结果展示页面。

## 测试

```bash
pytest
```

当前测试覆盖：

- GitHub PR URL 解析。
- 敏感模块和密钥风险规则识别。

## Demo 视频

待补充：请将 bilibili、网盘或其他可访问平台的视频链接放在这里。

## PR 提交规范

本项目按小粒度 PR 持续开发，每个 PR 只实现一个独立功能。仓库提供 `.github/pull_request_template.md`，PR 描述需包含：

- 功能描述
- 实现思路
- 测试方式
- 影响范围

## 未来扩展

- 支持 GitHub App，将 Review 建议一键评论到 PR。
- 支持仓库级代码索引，获取函数级上下文。
- 支持多模型交叉检查，降低误报和漏报。
- 支持团队自定义规则，例如敏感目录、强制测试策略和安全检查项。
