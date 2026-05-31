from app.analyzer.test_finder import guess_related_test_paths
from app.schemas.pr import ChangedFile


def test_guess_python_related_test_paths():
    paths = guess_related_test_paths(
        [ChangedFile(filename="app/auth/login.py", status="modified")]
    )

    assert "tests/auth/test_login.py" in paths
    assert "tests/test_login.py" in paths


def test_guess_java_related_test_paths():
    paths = guess_related_test_paths(
        [
            ChangedFile(
                filename="src/main/java/com/example/AuthService.java",
                status="modified",
            )
        ]
    )

    assert "src/test/java/com/example/AuthServiceTest.java" in paths

