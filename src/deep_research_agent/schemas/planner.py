from pydantic import BaseModel


class SearchTask(BaseModel):
    subtopic: str
    goal: str
    queries: list[str]
    # e.g. ["government", "news", "academic", "company filings"]
    preferred_sources: list[str]
    freshness_requirement: str     # "high", "medium", "low"
    evidence_to_collect: list[str]


class PlannerOutput(BaseModel):
    normalized_question: str
    research_scope: str
    subtopics: list[str]
    ambiguities: list[str]
    search_tasks: list[SearchTask]
