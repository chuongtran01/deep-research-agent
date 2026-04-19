from __future__ import annotations

from typing import Annotated, Literal
from pydantic import BaseModel, Field


class ExtractedEvidence(BaseModel):
    extracted_claim: Annotated[
        str,
        Field(description="A factual claim grounded in the source text")
    ]
    snippet: Annotated[
        str,
        Field(description="A short verbatim or near-verbatim supporting snippet from the source")
    ]
    relevance_score: Annotated[
        float,
        Field(description="Relevance to the research task from 0.0 to 1.0", ge=0.0, le=1.0)
    ]
    stance: Annotated[
        Literal["support", "oppose", "neutral"],
        Field(description="Whether this evidence supports, opposes, or is neutral to the research goal")
    ]
    evidence_type: Annotated[
        Literal["fact", "statistic", "expert_opinion", "policy", "background"],
        Field(description="Type of evidence")
    ]
    notes: Annotated[
        str,
        Field(description="Short notes about limitations, uncertainty, or context")
    ]


class EvidenceExtractorOutput(BaseModel):
    source_summary: Annotated[
        str,
        Field(description="Short summary of what this source contributes")
    ]
    evidence_items: Annotated[
        list[ExtractedEvidence],
        Field(description="Useful evidence extracted from the source")
    ]


class EvidenceItem(BaseModel):
    query: Annotated[str, Field(
        description="The search query that led to this evidence")]
    subtopic: Annotated[str, Field(description="Research subtopic")]
    goal: Annotated[str, Field(description="Research goal for this evidence")]

    source_title: Annotated[str, Field(description="Source title")]
    source_url: Annotated[str, Field(description="Source URL")]
    source_summary: Annotated[str, Field(
        description="Short summary of the source contribution")]

    extracted_claim: Annotated[str, Field(
        description="Factual claim extracted from the source")]
    snippet: Annotated[str, Field(
        description="Supporting snippet from the source")]
    relevance_score: Annotated[float, Field(
        description="Relevance score", ge=0.0, le=1.0)]
    stance: Annotated[Literal["support", "oppose", "neutral"],
                      Field(description="Stance of the evidence")]
    evidence_type: Annotated[
        Literal["fact", "statistic", "expert_opinion", "policy", "background"],
        Field(description="Evidence type")
    ]
    notes: Annotated[str, Field(description="Notes or caveats")]
