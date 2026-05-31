from app.services.review_cache import ReviewCache
from app.schemas.pr import PullRequestData
from app.schemas.review import ReviewResult


def test_review_cache_returns_copy_and_normalizes_key():
    cache = ReviewCache(ttl_seconds=60, max_items=2)
    pr = PullRequestData(
        owner="o",
        repo="r",
        number=1,
        title="Title",
        html_url="https://github.com/o/r/pull/1",
    )
    review = ReviewResult(summary="summary", risk_level="low")

    key = ReviewCache.key_for_pr_url(" HTTPS://github.com/O/R/pull/1/ ")
    cache.set(key, pr, review)
    cached = cache.get("https://github.com/o/r/pull/1")

    assert cached is not None
    cached_pr, cached_review = cached
    cached_pr.title = "Changed"
    cached_review.summary = "changed"

    second_pr, second_review = cache.get(key)
    assert second_pr.title == "Title"
    assert second_review.summary == "summary"


def test_review_cache_evicts_oldest_item():
    cache = ReviewCache(ttl_seconds=60, max_items=1)
    pr = PullRequestData(
        owner="o",
        repo="r",
        number=1,
        title="Title",
        html_url="https://github.com/o/r/pull/1",
    )
    review = ReviewResult(summary="summary", risk_level="low")

    cache.set("one", pr, review)
    cache.set("two", pr, review)

    assert cache.get("one") is None
    assert cache.get("two") is not None

