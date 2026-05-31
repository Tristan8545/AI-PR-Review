from app.schemas.pr import ChangedFile, PullRequestData


def sample_pr() -> PullRequestData:
    return PullRequestData(
        owner="demo",
        repo="ai-pr-review",
        number=1,
        title="Improve login token validation",
        body="This PR updates login token validation and adds a small cache for user sessions.",
        author="demo-user",
        base_branch="main",
        head_branch="feature/login-token-check",
        head_sha="demo-head-sha",
        html_url="https://github.com/demo/ai-pr-review/pull/1",
        changed_files=[
            ChangedFile(
                filename="app/auth/login.py",
                status="modified",
                additions=18,
                deletions=5,
                changes=23,
                patch="""@@ -14,9 +14,13 @@ def validate_token(token):
-    if token is None:
-        return False
+    if token is None:
+        return True
     payload = decode_token(token)
     return payload.get("user_id") is not None
""",
                content="""from app.auth.jwt import decode_token


def validate_token(token):
    if token is None:
        return True
    payload = decode_token(token)
    return payload.get("user_id") is not None
""",
            ),
            ChangedFile(
                filename="tests/test_login.py",
                status="modified",
                additions=2,
                deletions=20,
                changes=22,
                patch="""@@ -1,8 +1,4 @@
-def test_empty_token_is_rejected():
-    assert validate_token(None) is False
+def test_valid_token():
+    assert validate_token("valid") is True
""",
            ),
        ],
    )
