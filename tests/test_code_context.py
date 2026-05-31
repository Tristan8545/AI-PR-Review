from app.analyzer.code_context import build_local_context
from app.schemas.pr import ChangedFile


def test_extract_python_function_context_for_changed_line():
    file = ChangedFile(
        filename="app/auth/login.py",
        status="modified",
        patch="""@@ -5,4 +5,4 @@ def validate_token(token):
 def validate_token(token):
-    return False
+    return True
""",
        content="""def helper():
    return None


def validate_token(token):
    if token is None:
        return True
    return False
""",
    )

    context = build_local_context(file)

    assert context is not None
    assert "Python scope: validate_token" in context
    assert "return True" in context
