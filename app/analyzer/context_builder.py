from app.schemas.pr import PullRequestData
from app.schemas.review import RuleFinding
from app.analyzer.code_context import build_local_context


def _build_file_contents(pr: PullRequestData) -> str:
    blocks: list[str] = []
    for file in pr.changed_files:
        if not file.content:
            continue
        truncated = " (truncated)" if file.content_truncated else ""
        blocks.append(
            f"\n### {file.filename}{truncated}\n"
            f"```text\n{file.content}\n```"
        )

    return "\n".join(blocks) or "- No full file content was fetched."


def _build_local_contexts(pr: PullRequestData) -> str:
    blocks: list[str] = []
    for file in pr.changed_files:
        local_context = build_local_context(file)
        if not local_context:
            continue
        blocks.append(f"\n## {file.filename}\n{local_context}")

    return "\n".join(blocks) or "- No local code context was extracted."


def build_review_context(
    pr: PullRequestData, rule_findings: list[RuleFinding], max_patch_chars: int
) -> str:
    files_summary = "\n".join(
        f"- {f.filename} ({f.status}, +{f.additions}/-{f.deletions})"
        for f in pr.changed_files
    )

    rules = "\n".join(
        f"- [{f.severity}] {f.file}: {f.title} - {f.reason}" for f in rule_findings
    ) or "- No rule findings."

    patches: list[str] = []
    remaining = max_patch_chars
    for file in pr.changed_files:
        if remaining <= 0:
            break
        patch = file.patch or "(GitHub did not return a patch. The file may be binary or too large.)"
        block = f"\n### {file.filename}\n```diff\n{patch[:remaining]}\n```"
        patches.append(block)
        remaining -= len(block)

    return f"""
PR: {pr.title}
URL: {pr.html_url}
Author: {pr.author}
Branch: {pr.head_branch} -> {pr.base_branch}
Head SHA: {pr.head_sha}

PR Description:
{pr.body or "(No description)"}

Changed Files:
{files_summary}

Rule Findings:
{rules}

Diff:
{''.join(patches)}

Full File Context:
{_build_file_contents(pr)}

Local Code Context:
{_build_local_contexts(pr)}
""".strip()
