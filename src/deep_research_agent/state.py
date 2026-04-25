from typing import Annotated, Any, TypedDict, Literal

from pydantic import BaseModel

from src.deep_research_agent.schemas.evidence import EvidenceItem
from langgraph.graph import add_messages
from src.deep_research_agent.schemas.report import ReportOutlineOutput


class TaskModel(BaseModel):
    name: str
    description: str = ""
    args: dict[str, Any]


class AgentState(TypedDict, total=False):
    query: Annotated[str, "User research question"]

    plan: Annotated[list[TaskModel], "Immutable blueprint of tasks to execute"]
    pending_tasks: Annotated[list[TaskModel],
                             "Mutable queue of tasks waiting to run"]
    current_task: Annotated[TaskModel | None,
                            "Task selected for execution by the scheduler"]
    completed_tasks: Annotated[list[TaskModel],
                               "Tasks finished in chronological order"]

    normalized_question: Annotated[str, "Planner-clarified working question"]
    research_scope: Annotated[str,
                              "Intended breadth and depth of the investigation"]
    subtopics: Annotated[list[str], "Major themes the plan must address"]
    ambiguities: Annotated[list[str],
                           "Uncertainties or missing context flagged by the planner"]

    time_sensitivity: Annotated[Literal["high", "medium", "low"],
                                "How sensitive the question is to recent information"]
    preferred_source_types: Annotated[list[str],
                                      "Likely useful source types such as government, academic, news, company, docs"]

    search_results: Annotated[list[Any],
                              "Raw retrieval payloads from search and fetch tools"]
    evidence_items: Annotated[list[EvidenceItem],
                              "Extracted evidence items from the search results"]
    fetched_documents: Annotated[list[Any],
                                 "Batches of documents fetched from search result URLs"]

    ranked_evidence_items: Annotated[list[EvidenceItem],
                                     "Evidence items retained after ranking/filtering"]
    research_complete: Annotated[bool,
                                 "Whether evidence is sufficient to stop research"]
    missing_subtopics: Annotated[list[str],
                                 "Subtopics still lacking strong evidence"]

    report_outline: Annotated[ReportOutlineOutput,
                              "Outline of the report to be written"]

    summary: Annotated[list[str],
                       "Running log of planner and tool outcomes", add_messages]
    final_answer: Annotated[str, "User-facing message when the graph stops"]
