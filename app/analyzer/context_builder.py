from app.schemas.pr import PullRequestData
from app.schemas.review import RuleFinding


def build_review_context(
    pr: PullRequestData, rule_findings: list[RuleFinding], max_patch_chars: int
) -> str:
    files_summary = "\n".join(
        f"- {f.filename} ({f.status}, +{f.additions}/-{f.deletions})"
        for f in pr.changed_files
    )

    rules = "\n".join(
        f"- [{f.severity}] {f.file}: {f.title} - {f.reason}" for f in rule_findings
    ) or "- 暂无规则命中"

    patches: list[str] = []
    remaining = max_patch_chars
    for file in pr.changed_files:
        if remaining <= 0:
            break
        patch = file.patch or "(GitHub 未返回 patch，可能是二进制文件或变更过大)"
        block = f"\n### {file.filename}\n```diff\n{patch[:remaining]}\n```"
        patches.append(block)
        remaining -= len(block)

    return f"""
PR: {pr.title}
URL: {pr.html_url}
作者: {pr.author}
分支: {pr.head_branch} -> {pr.base_branch}

PR 描述:
{pr.body or "(无描述)"}

变更文件:
{files_summary}

规则分析结果:
{rules}

Diff:
{''.join(patches)}
""".strip()

