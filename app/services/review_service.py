from app.ai.reviewer import DeepSeekReviewer
from app.analyzer.context_builder import build_review_context
from app.analyzer.review_quality import improve_review_quality
from app.analyzer.rule_analyzer import analyze_rules
from app.config import Settings
from app.github.github_client import GitHubClient
from app.services.review_cache import ReviewCache
from app.schemas.pr import PullRequestData
from app.schemas.review import ReviewResult


class ReviewService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.github = GitHubClient(settings)
        self.reviewer = DeepSeekReviewer(settings)
        self.cache = ReviewCache(settings.cache_ttl_seconds, settings.cache_max_items)

    async def analyze_pr(self, pr_url: str) -> tuple[PullRequestData, ReviewResult]:
        cache_key = ReviewCache.key_for_pr_url(pr_url)
        cached = self.cache.get(cache_key)
        if cached:
            pr, review = cached
            review.mode = f"{review.mode}+cache"
            return pr, review

        pr = await self.github.fetch_pull_request(pr_url)
        findings = analyze_rules(pr)
        context = build_review_context(pr, findings, self.settings.max_patch_chars)
        review = await self.reviewer.review(pr, context, findings)
        review = improve_review_quality(pr, review, findings)
        self.cache.set(cache_key, pr, review)
        return pr, review
