from app.analyzer.rule_analyzer import analyze_rules
from app.schemas.pr import ChangedFile, PullRequestData


def test_detect_sensitive_auth_file():
    pr = PullRequestData(
        owner="o",
        repo="r",
        number=1,
        title="Auth change",
        html_url="https://github.com/o/r/pull/1",
        changed_files=[
            ChangedFile(
                filename="src/auth/login.py",
                status="modified",
                additions=10,
                deletions=1,
                changes=11,
                patch="+def login(): pass",
            )
        ],
    )

    findings = analyze_rules(pr)

    assert findings
    assert findings[0].title == "敏感模块变更"


def test_detect_secret_in_patch():
    pr = PullRequestData(
        owner="o",
        repo="r",
        number=1,
        title="Config change",
        html_url="https://github.com/o/r/pull/1",
        changed_files=[
            ChangedFile(
                filename="settings.py",
                status="modified",
                additions=1,
                deletions=0,
                changes=1,
                patch='+API_KEY = "abc"',
            )
        ],
    )

    findings = analyze_rules(pr)

    assert any(f.severity == "high" for f in findings)

