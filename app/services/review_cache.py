from collections import OrderedDict
from time import monotonic

from app.schemas.pr import PullRequestData
from app.schemas.review import ReviewResult


class ReviewCache:
    def __init__(self, ttl_seconds: int, max_items: int):
        self.ttl_seconds = ttl_seconds
        self.max_items = max_items
        self._items: OrderedDict[str, tuple[float, PullRequestData, ReviewResult]] = OrderedDict()

    def get(self, key: str) -> tuple[PullRequestData, ReviewResult] | None:
        item = self._items.get(key)
        if not item:
            return None

        created_at, pr, review = item
        if monotonic() - created_at > self.ttl_seconds:
            self._items.pop(key, None)
            return None

        self._items.move_to_end(key)
        return pr.model_copy(deep=True), review.model_copy(deep=True)

    def set(self, key: str, pr: PullRequestData, review: ReviewResult) -> None:
        self._items[key] = (monotonic(), pr.model_copy(deep=True), review.model_copy(deep=True))
        self._items.move_to_end(key)

        while len(self._items) > self.max_items:
            self._items.popitem(last=False)

    @staticmethod
    def key_for_pr_url(pr_url: str) -> str:
        return pr_url.strip().lower().rstrip("/")

