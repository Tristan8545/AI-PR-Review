# PR 持续交付记录

项目按照比赛要求基于 PR 添加功能，并保持主分支可运行。

每个 PR 只做一件事，PR 描述包含：

- 标题
- 功能描述
- 实现思路
- 测试方式
- 影响范围

已合并 PR：

1. [Add full file content context for PR review](https://github.com/Tristan8545/AI-PR-Review/pull/1)
2. [Add local code context extraction](https://github.com/Tristan8545/AI-PR-Review/pull/2)
3. [Add related test file context](https://github.com/Tristan8545/AI-PR-Review/pull/3)
4. [Add review quality guardrails](https://github.com/Tristan8545/AI-PR-Review/pull/4)
5. [Add cached PR review results](https://github.com/Tristan8545/AI-PR-Review/pull/5)
6. [Improve review web experience](https://github.com/Tristan8545/AI-PR-Review/pull/6)

每次 PR 合并前均执行：

```bash
pytest
```

并通过本地 Demo 请求验证 Web 流程可运行。

