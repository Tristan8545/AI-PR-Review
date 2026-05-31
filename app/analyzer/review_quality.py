from app.schemas.pr import PullRequestData
from app.schemas.review import ReviewResult, RiskItem, RuleFinding
from app.analyzer.patch_parser import extract_changed_lines


VALID_SEVERITIES = {"high", "medium", "low", "info"}
SEVERITY_ORDER = {"high": 3, "medium": 2, "low": 1, "info": 0}
MIN_CONFIDENCE = 0.35


def improve_review_quality(
    pr: PullRequestData, review: ReviewResult, rule_findings: list[RuleFinding]
) -> ReviewResult:
    changed_paths = {file.filename for file in pr.changed_files}
    patch_by_file = {file.filename: file.patch or "" for file in pr.changed_files}

    filtered: list[RiskItem] = []
    seen: set[tuple[str, str]] = set()
    for risk in review.risks:
        normalized = _normalize_risk(risk)
        if normalized.confidence < MIN_CONFIDENCE:
            continue
        if normalized.file not in changed_paths:
            continue
        if normalized.line is not None and not _line_is_in_changed_patch(
            normalized.line, patch_by_file.get(normalized.file, "")
        ):
            normalized = normalized.model_copy(
                update={
                    "severity": _downgrade(normalized.severity),
                    "confidence": min(normalized.confidence, 0.55),
                }
            )

        key = (normalized.file, normalized.title.strip().lower())
        if key in seen:
            continue
        seen.add(key)
        filtered.append(normalized)

    review.risks = _merge_rule_findings(pr, filtered, rule_findings)
    review.risk_level = _calculate_risk_level(review.risks)
    review.suggestions = _dedupe_strings(review.suggestions)
    review.suggested_tests = _dedupe_strings(review.suggested_tests)
    return review


def _normalize_risk(risk: RiskItem) -> RiskItem:
    severity = risk.severity.lower().strip()
    if severity not in VALID_SEVERITIES:
        severity = "info"

    confidence = max(0.0, min(1.0, risk.confidence))
    return risk.model_copy(update={"severity": severity, "confidence": confidence})


def _line_is_in_changed_patch(line: int, patch: str) -> bool:
    changed_lines = extract_changed_lines(patch)
    return not changed_lines or line in changed_lines


def _downgrade(severity: str) -> str:
    if severity == "high":
        return "medium"
    if severity == "medium":
        return "low"
    return severity


def _merge_rule_findings(
    pr: PullRequestData, risks: list[RiskItem], rule_findings: list[RuleFinding]
) -> list[RiskItem]:
    existing = {(risk.file, risk.title.strip().lower()) for risk in risks}
    changed_paths = {file.filename for file in pr.changed_files}

    for finding in rule_findings:
        if finding.file not in changed_paths:
            continue
        key = (finding.file, finding.title.strip().lower())
        if key in existing:
            continue
        risks.append(
            RiskItem(
                file=finding.file,
                severity=finding.severity,
                title=finding.title,
                reason=finding.reason,
                suggestion="请人工重点确认该规则命中的变更是否需要补充校验、测试或回滚保护。",
                confidence=0.68,
            )
        )
        existing.add(key)

    return sorted(
        risks,
        key=lambda item: (SEVERITY_ORDER.get(item.severity, 0), item.confidence),
        reverse=True,
    )

def _calculate_risk_level(risks: list[RiskItem]) -> str:
    if any(risk.severity == "high" for risk in risks):
        return "high"
    if any(risk.severity == "medium" for risk in risks):
        return "medium"
    return "low"


def _dedupe_strings(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        normalized = " ".join(item.split()).lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(item)
    return result
