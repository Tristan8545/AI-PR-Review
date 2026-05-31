import json

import httpx

from app.ai.mock_reviewer import build_mock_review
from app.ai.prompts import SYSTEM_PROMPT, build_user_prompt
from app.config import Settings
from app.schemas.pr import PullRequestData
from app.schemas.review import ReviewResult, RuleFinding


class DeepSeekReviewer:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def review(
        self, pr: PullRequestData, context: str, rule_findings: list[RuleFinding]
    ) -> ReviewResult:
        if self.settings.demo_mode or not self.settings.deepseek_api_key:
            return build_mock_review(pr, rule_findings)

        payload = {
            "model": self.settings.deepseek_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(context)},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "stream": False,
        }
        if self.settings.deepseek_model.startswith("deepseek-v4"):
            payload["thinking"] = {"type": "disabled"}

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.settings.deepseek_base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.settings.deepseek_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        parsed = self._parse_json(content)
        parsed["mode"] = "deepseek"
        parsed["rule_findings"] = [finding.model_dump() for finding in rule_findings]
        parsed["raw_model_output"] = content
        return ReviewResult.model_validate(parsed)

    def _parse_json(self, content: str) -> dict:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")
            if start >= 0 and end > start:
                return json.loads(content[start : end + 1])
            raise

