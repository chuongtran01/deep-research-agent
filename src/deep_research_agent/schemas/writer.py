from __future__ import annotations

from typing import Annotated
from pydantic import BaseModel, Field

from src.deep_research_agent.schemas.report import OutlineSection


class ReportSection(BaseModel):
    heading: Annotated[str, Field(description="Section heading")]
    content: Annotated[str, Field(
        description="Section content with inline evidence citations like [E1]")]


class ReportWriterOutput(BaseModel):
    title: Annotated[str, Field(description="Report title")]
    answer_summary: Annotated[str, Field(
        description="Short direct answer to the research question")]
    sections: Annotated[list[OutlineSection],
                        Field(description="Main report sections")]
    limitations: Annotated[list[str], Field(
        description="Evidence limitations, gaps, or caveats")]
    confidence: Annotated[str, Field(
        description="Overall confidence: high, medium, or low")]
