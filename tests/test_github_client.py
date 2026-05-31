from app.config import Settings
from app.github.github_client import GitHubClient
from app.schemas.pr import ChangedFile


def test_select_context_files_prioritizes_sensitive_source_files():
    settings = Settings()
    settings.max_context_files = 1
    client = GitHubClient(settings)
    files = [
        ChangedFile(filename="README.md", status="modified", changes=100),
        ChangedFile(filename="app/auth/login.py", status="modified", changes=10),
    ]

    selected = client._select_context_files(files)

    assert len(selected) == 1
    assert selected[0].filename == "app/auth/login.py"

