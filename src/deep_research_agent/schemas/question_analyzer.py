from __future__ import annotations

from typing import Annotated, Literal
from pydantic import BaseModel, Field


class AnalyzerOutput(BaseModel):
    normalized_question: Annotated[
        str,
        Field(description="A clarified working version of the user's question")
    ]
    research_scope: Annotated[
        str,
        Field(description="The intended scope and boundaries of the research")
    ]
    ambiguities: Annotated[
        list[str],
        Field(description="Missing context, ambiguity, or assumptions that may affect research")
    ]
    time_sensitivity: Annotated[
        Literal["high", "medium", "low"],
        Field(description="How sensitive the question is to recent information")
    ]
    preferred_source_types: Annotated[
        list[str],
        Field(description="Likely useful source types such as government, academic, news, company, docs")
    ]
    analysis_notes: Annotated[
        list[str],
        Field(description="Short notes that may help the planner")
    ]
