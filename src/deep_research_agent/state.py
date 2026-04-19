from typing import TypedDict
from pydantic import BaseModel
from typing import Any


class TaskModel(BaseModel):
    name: str
    args: dict[str, Any]


class AgentState(TypedDict):
    query: str
    plan: list[TaskModel]
    pending_tasks: list[TaskModel]
    current_task: TaskModel | None
    completed_tasks: list[TaskModel]

    normalized_question: str
    research_scope: str
    subtopics: list[str]
    ambiguities: list[str]

    search_results: list[Any]
    summary: str
    final_answer: str
