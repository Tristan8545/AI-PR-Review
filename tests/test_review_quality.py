from app.analyzer.review_quality import improve_review_quality
from app.schemas.pr import ChangedFile, PullRequestData
from app.schemas.review import ReviewResult, RiskItem, RuleFinding


def test_review_quality_filters_dedupes_and_merges_rule_findings():
    pr = PullRequestData(
        owner="o",
        repo="r",
        number=1,
        title="Auth change",
        html_url="https://github.com/o/r/pull/1",
        changed_files=[
            ChangedFile(
                filename="app/auth/login.py",
                status="modified",
                patch="""@@ -10,2 +10,2 @@ def login():
-    return False
+    return True
""",
            )
        ],
    )
    review = ReviewResult(
        summary="summary",
        risk_level="high",
        risks=[
            RiskItem(
                file="app/auth/login.py",
                line=10,
                severity="HIGH",
                title="Bypass auth",
                reason="reason",
                suggestion="fix",
                confidence=0.9,
            ),
            RiskItem(
                file="app/auth/login.py",
                line=10,
                severity="high",
                title="Bypass auth",
                reason="duplicate",
                suggestion="fix",
                confidence=0.8,
            ),
            RiskItem(
                file="README.md",
                severity="medium",
                title="Out of diff",
                reason="not changed",
                suggestion="ignore",
                confidence=0.9,
            ),
            RiskItem(
                file="app/auth/login.py",
                severity="low",
                title="Weak signal",
                reason="low confidence",
                suggestion="ignore",
                confidence=0.1,
            ),
        ],
        suggestions=["Add tests", "Add tests"],
        suggested_tests=["test auth", "test auth"],
    )
    findings = [
        RuleFinding(
            file="app/auth/login.py",
            severity="medium",
            title="Sensitive module change",
            reason="auth path changed",
        )
    ]

    result = improve_review_quality(pr, review, findings)

    assert [risk.title for risk in result.risks] == [
        "Bypass auth",
        "Sensitive module change",
    ]
    assert result.risks[0].severity == "high"
    assert result.risk_level == "high"
    assert result.suggestions == ["Add tests"]
    assert result.suggested_tests == ["test auth"]
