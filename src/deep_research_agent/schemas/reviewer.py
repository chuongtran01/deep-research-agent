from pydantic import BaseModel


class ReviewIssue(BaseModel):
    severity: str              # "high", "medium", "low"
    issue_type: str  # "unsupported_claim", "bad_citation", "missing_citation", "overstatement", "conflict_ignored", "missing_caveat"
    section: str
    claim_text: str
    explanation: str
    suggested_fix: str
    supported_evidence_ids: list[str]


class ReviewerOutput(BaseModel):
    overall_verdict: str       # "pass", "revise", "fail"
    summary: str
    issues: list[ReviewIssue]
    strengths: list[str]
