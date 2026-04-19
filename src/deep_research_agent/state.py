from typing import Annotated, Any, TypedDict

from pydantic import BaseModel


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
    current_step_index: Annotated[int,
                                  "Progress index for plan execution or error recovery"]

    normalized_question: Annotated[str, "Planner-clarified working question"]
    research_scope: Annotated[str,
                              "Intended breadth and depth of the investigation"]
    subtopics: Annotated[list[str], "Major themes the plan must address"]
    ambiguities: Annotated[list[str],
                           "Uncertainties or missing context flagged by the planner"]

    search_results: Annotated[list[Any],
                              "Raw retrieval payloads from search and fetch tools"]
    summary: Annotated[str, "Running log of planner and tool outcomes"]
    final_answer: Annotated[str, "User-facing message when the graph stops"]
