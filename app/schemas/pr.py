from pydantic import BaseModel, Field


class PullRequestRef(BaseModel):
    owner: str
    repo: str
    number: int


class ChangedFile(BaseModel):
    filename: str
    status: str
    additions: int = 0
    deletions: int = 0
    changes: int = 0
    patch: str = ""
    content: str | None = None
    content_truncated: bool = False


class RelatedTestFile(BaseModel):
    filename: str
    content: str
    content_truncated: bool = False


class PullRequestData(BaseModel):
    owner: str
    repo: str
    number: int
    title: str
    body: str = ""
    author: str = ""
    base_branch: str = ""
    head_branch: str = ""
    head_sha: str = ""
    html_url: str
    changed_files: list[ChangedFile] = Field(default_factory=list)
    related_tests: list[RelatedTestFile] = Field(default_factory=list)
