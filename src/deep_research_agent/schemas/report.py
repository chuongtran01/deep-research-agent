from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field


class OutlineClaim(BaseModel):
    claim: Annotated[str, Field(description="A claim the report should make")]
    evidence_ids: Annotated[
        list[str],
        Field(description="Evidence IDs that support this claim"),
    ]


class OutlineSection(BaseModel):
    heading: Annotated[str, Field(description="Section heading")]
    purpose: Annotated[str, Field(
        description="What this section should explain")]
    claims: Annotated[list[OutlineClaim], Field(
        description="Claims to include in this section")]


class ReportOutlineOutput(BaseModel):
    title: Annotated[str, Field(description="Report title")]
    thesis: Annotated[str, Field(
        description="Main answer or central synthesis")]
    sections: Annotated[list[OutlineSection],
                        Field(description="Report sections")]
    limitations: Annotated[list[str], Field(
        description="Evidence gaps or caveats")]
