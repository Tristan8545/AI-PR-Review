from base64 import b64decode

import httpx

from app.config import Settings
from app.github.pr_url_parser import parse_pr_url
from app.schemas.pr import ChangedFile, PullRequestData


class GitHubClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = "https://api.github.com"

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "AI-PR-Review-Assistant",
        }
        if self.settings.github_token:
            headers["Authorization"] = f"Bearer {self.settings.github_token}"
        return headers

    async def fetch_pull_request(self, pr_url: str) -> PullRequestData:
        ref = parse_pr_url(pr_url)
        async with httpx.AsyncClient(timeout=20.0, headers=self._headers()) as client:
            pr_resp = await client.get(
                f"{self.base_url}/repos/{ref.owner}/{ref.repo}/pulls/{ref.number}"
            )
            pr_resp.raise_for_status()
            pr_json = pr_resp.json()

            files = await self._fetch_changed_files(client, ref.owner, ref.repo, ref.number)
            head_sha = (pr_json.get("head") or {}).get("sha", "")
            await self._attach_file_contents(client, ref.owner, ref.repo, head_sha, files)

        return PullRequestData(
            owner=ref.owner,
            repo=ref.repo,
            number=ref.number,
            title=pr_json.get("title") or "",
            body=pr_json.get("body") or "",
            author=(pr_json.get("user") or {}).get("login", ""),
            base_branch=(pr_json.get("base") or {}).get("ref", ""),
            head_branch=(pr_json.get("head") or {}).get("ref", ""),
            head_sha=head_sha,
            html_url=pr_json.get("html_url", pr_url),
            changed_files=files[: self.settings.max_files],
        )

    async def _fetch_changed_files(
        self, client: httpx.AsyncClient, owner: str, repo: str, number: int
    ) -> list[ChangedFile]:
        all_files: list[ChangedFile] = []
        page = 1
        while page <= 5:
            resp = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/pulls/{number}/files",
                params={"per_page": 100, "page": page},
            )
            resp.raise_for_status()
            items = resp.json()
            if not items:
                break

            for item in items:
                all_files.append(
                    ChangedFile(
                        filename=item.get("filename", ""),
                        status=item.get("status", ""),
                        additions=item.get("additions", 0),
                        deletions=item.get("deletions", 0),
                        changes=item.get("changes", 0),
                        patch=item.get("patch") or "",
                    )
                )

            if len(items) < 100:
                break
            page += 1

        return all_files

    async def _attach_file_contents(
        self,
        client: httpx.AsyncClient,
        owner: str,
        repo: str,
        head_sha: str,
        files: list[ChangedFile],
    ) -> None:
        if not head_sha:
            return

        for file in self._select_context_files(files):
            if file.status == "removed":
                continue
            content = await self.fetch_file_content(
                client, owner, repo, file.filename, head_sha
            )
            if content is None:
                continue
            file.content_truncated = len(content) > self.settings.max_file_chars
            file.content = content[: self.settings.max_file_chars]

    async def fetch_file_content(
        self,
        client: httpx.AsyncClient,
        owner: str,
        repo: str,
        path: str,
        ref: str,
    ) -> str | None:
        resp = await client.get(
            f"{self.base_url}/repos/{owner}/{repo}/contents/{path}",
            params={"ref": ref},
        )
        if resp.status_code in {403, 404}:
            return None
        resp.raise_for_status()

        data = resp.json()
        if data.get("type") != "file" or data.get("encoding") != "base64":
            return None

        try:
            return b64decode(data.get("content", "")).decode("utf-8", errors="replace")
        except ValueError:
            return None

    def _select_context_files(self, files: list[ChangedFile]) -> list[ChangedFile]:
        source_exts = (".py", ".java", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs")
        skip_exts = (".lock", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf", ".zip")

        candidates = [
            file
            for file in files[: self.settings.max_files]
            if not file.filename.lower().endswith(skip_exts)
        ]

        def score(file: ChangedFile) -> tuple[int, int]:
            path = file.filename.lower()
            risk_hint = any(
                word in path
                for word in ("auth", "login", "permission", "token", "payment", "sql")
            )
            source_hint = path.endswith(source_exts)
            test_hint = "test" in path
            return (int(risk_hint) * 3 + int(source_hint) * 2 + int(test_hint), file.changes)

        return sorted(candidates, key=score, reverse=True)[: self.settings.max_context_files]
