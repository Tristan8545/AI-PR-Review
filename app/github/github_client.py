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

        return PullRequestData(
            owner=ref.owner,
            repo=ref.repo,
            number=ref.number,
            title=pr_json.get("title") or "",
            body=pr_json.get("body") or "",
            author=(pr_json.get("user") or {}).get("login", ""),
            base_branch=(pr_json.get("base") or {}).get("ref", ""),
            head_branch=(pr_json.get("head") or {}).get("ref", ""),
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

