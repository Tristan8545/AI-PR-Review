from app.schemas.pr import PullRequestData
from app.schemas.review import ReviewResult, RiskItem, RuleFinding


def build_mock_review(pr: PullRequestData, findings: list[RuleFinding]) -> ReviewResult:
    risks = [
        RiskItem(
            file=f.file,
            severity=f.severity,
            title=f.title,
            reason=f.reason,
            suggestion="请结合业务场景确认该变更是否需要补充校验、回滚保护或测试覆盖。",
            confidence=0.72,
        )
        for f in findings[:5]
    ]

    if not risks:
        risks.append(
            RiskItem(
                file=pr.changed_files[0].filename if pr.changed_files else "N/A",
                severity="low",
                title="暂无明显高风险规则命中",
                reason="规则扫描没有发现敏感路径或危险代码模式，仍建议人工确认核心逻辑。",
                suggestion="重点检查边界条件、异常路径和测试覆盖。",
                confidence=0.6,
            )
        )

    return ReviewResult(
        mode="demo",
        summary=f"该 PR 修改了 {len(pr.changed_files)} 个文件，主要需要关注变更范围、敏感模块和测试覆盖。",
        risk_level="medium" if findings else "low",
        key_changes=[
            f"{f.filename}: +{f.additions}/-{f.deletions}" for f in pr.changed_files[:5]
        ],
        risks=risks,
        suggestions=[
            "优先 Review 规则命中的文件，确认是否涉及鉴权、数据写入或异常处理。",
            "如果 PR 修改核心流程，建议补充失败路径和边界条件测试。",
        ],
        suggested_tests=[
            "补充本次变更对应的单元测试。",
            "补充至少一个失败路径或异常输入场景。",
        ],
        rule_findings=findings,
    )

