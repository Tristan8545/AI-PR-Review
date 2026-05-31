from app.analyzer.context_builder import build_review_context
from app.schemas.pr import ChangedFile, PullRequestData, RelatedTestFile


def test_context_includes_full_file_content():
    pr = PullRequestData(
        owner="o",
        repo="r",
        number=1,
        title="Add auth check",
        head_sha="abc123",
        html_url="https://github.com/o/r/pull/1",
        changed_files=[
            ChangedFile(
                filename="app/auth/login.py",
                status="modified",
                additions=1,
                deletions=0,
                changes=1,
                patch="+return True",
                content="def validate_token(token):\n    return True\n",
            )
        ],
        related_tests=[
            RelatedTestFile(
                filename="tests/auth/test_login.py",
                content="def test_login():\n    assert True\n",
            )
        ],
    )

    context = build_review_context(pr, [], 1000)

    assert "Full File Context" in context
    assert "def validate_token" in context
    assert "Head SHA: abc123" in context
    assert "Local Code Context" in context
    assert "Related Test Context" in context
    assert "tests/auth/test_login.py" in context
