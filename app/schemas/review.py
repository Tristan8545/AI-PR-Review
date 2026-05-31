from pydantic import BaseModel, Field


class RiskItem(BaseModel):
    file: str
    line: int | None = None
    severity: str
    title: str
    reason: str
    suggestion: str
    confidence: float = 0.7


class RuleFinding(BaseModel):
    file: str
    severity: str
    title: str
    reason: str


class ReviewResult(BaseModel):
    mode: str = "demo"
    summary: str
    risk_level: str
    key_changes: list[str] = Field(default_factory=list)
    risks: list[RiskItem] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    suggested_tests: list[str] = Field(default_factory=list)
    rule_findings: list[RuleFinding] = Field(default_factory=list)
    raw_model_output: str | None = None

