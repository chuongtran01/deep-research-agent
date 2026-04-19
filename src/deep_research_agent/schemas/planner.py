from pydantic import BaseModel, Field
from typing import Annotated, Literal


class SearchTask(BaseModel):
    subtopic: Annotated[str, Field(
        description="The research subtopic this task belongs to")]
    goal: Annotated[str, Field(
        description="What this task is trying to find out")]
    queries: Annotated[
        list[str],
        Field(description="Concrete web/document search queries", min_length=1)
    ]
    preferred_sources: Annotated[
        list[str],
        Field(description="Preferred source types such as government, academic, news, company, docs")
    ]
    freshness_requirement: Annotated[
        Literal["high", "medium", "low"],
        Field(description="How time-sensitive this task is")
    ]
    evidence_to_collect: Annotated[
        list[str],
        Field(description="Specific evidence types to look for")
    ]


class PlannerOutput(BaseModel):
    normalized_question: Annotated[
        str,
        Field(description="A cleaned up, specific version of the user's question")
    ]
    research_scope: Annotated[
        str,
        Field(description="What is in scope for the research")
    ]
    subtopics: Annotated[
        list[str],
        Field(description="3-7 key subtopics needed to answer the question", min_length=1)
    ]
    ambiguities: Annotated[
        list[str],
        Field(description="Any missing context or ambiguity that could affect the research")
    ]
    search_tasks: Annotated[
        list[SearchTask],
        Field(description="Actionable search tasks for the retrieval step", min_length=1)
    ]
