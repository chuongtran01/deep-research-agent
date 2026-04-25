from __future__ import annotations

from typing import Annotated, Literal
from pydantic import BaseModel, Field


class CitationIssue(BaseModel):
    issue_type: Annotated[
        Literal["missing_citation", "unknown_evidence_id",
                "unused_evidence", "malformed_citation"],
        Field(description="Type of citation issue")
    ]
    location: Annotated[str, Field(description="Where the issue appears")]
    text: Annotated[str, Field(description="Problematic text")]
    message: Annotated[str, Field(description="Explanation of the issue")]


class CitationCheckResult(BaseModel):
    passed: bool
    issues: list[CitationIssue]
    cited_evidence_ids: list[str]
    uncited_evidence_ids: list[str]
