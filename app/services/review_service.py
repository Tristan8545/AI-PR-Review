from app.ai.reviewer import DeepSeekReviewer
from app.analyzer.context_builder import build_review_context
from app.analyzer.rule_analyzer import analyze_rules
from app.config import Settings
from app.github.github_client import GitHubClient
from app.schemas.pr import PullRequestData
from app.schemas.review import ReviewResult


class ReviewService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.github = GitHubClient(settings)
        self.reviewer = DeepSeekReviewer(settings)

    async def analyze_pr(self, pr_url: str) -> tuple[PullRequestData, ReviewResult]:
        pr = await self.github.fetch_pull_request(pr_url)
        findings = analyze_rules(pr)
        context = build_review_context(pr, findings, self.settings.max_patch_chars)
        review = await self.reviewer.review(pr, context, findings)
        return pr, review

