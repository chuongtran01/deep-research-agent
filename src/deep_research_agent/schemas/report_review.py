from __future__ import annotations

from typing import Annotated, Literal
from pydantic import BaseModel, Field


class ReviewIssue(BaseModel):
    severity: Annotated[
        Literal["high", "medium", "low"],
        Field(description="Severity of the issue")
    ]
    issue_type: Annotated[
        Literal[
            "unsupported_claim",
            "bad_citation",
            "missing_citation",
            "overstatement",
            "conflict_ignored",
            "missing_caveat",
            "clarity"
        ],
        Field(description="Type of report issue")
    ]
    location: Annotated[str, Field(description="Where the issue appears")]
    claim_text: Annotated[str, Field(description="Problematic claim or text")]
    explanation: Annotated[str, Field(description="Why this is a problem")]
    suggested_fix: Annotated[str, Field(description="How to fix the issue")]
    supported_evidence_ids: Annotated[
        list[str],
        Field(description="Evidence IDs that could support the corrected claim")
    ]


class ReportReviewOutput(BaseModel):
    verdict: Annotated[
        Literal["pass", "revise", "fail"],
        Field(description="Overall review verdict")
    ]
    summary: Annotated[str, Field(description="Short review summary")]
    issues: Annotated[list[ReviewIssue], Field(
        description="Issues found in the draft")]
    strengths: Annotated[list[str], Field(
        description="What the draft does well")]
