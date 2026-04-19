from src.deep_research_agent.state import AgentState
from src.deep_research_agent.adapters.web_search import SearchTool
from typing import Any


def web_search_node(state: AgentState) -> AgentState:
    """
    Execute the current web_search task.

    Expected state:
    - current_task: TaskModel(name="web_search", args={...})
    - search_results: list[Any] (optional existing results)
    - completed_tasks: list[TaskModel] (optional existing completed tasks)

    Behavior:
    - reads the current task query
    - runs web search
    - appends normalized search payload to search_results
    - marks current task as completed
    - clears current_task so router can schedule the next one
    """

    current_task = state.get("current_task")

    if current_task is None:
        return {
            "summary": ["Web search node received no current_task."],
            "final_answer": "I could not run web search because no task was selected.",
        }

    if current_task.name != "web_search":
        return {
            "summary": ["Web search node received a non-web_search task."],
            "final_answer": "I could not run web search because the task was not a web_search task.",
        }

    query = (current_task.args.get("query") or "").strip()
    if not query:
        completed_tasks = state.get("completed_tasks", [])
        return {
            "completed_tasks": completed_tasks + [current_task],
            "current_task": None,
            "summary": ["Web search task had an empty query. Marked as completed without execution."],
        }

    max_results = current_task.args.get("max_results", 5)
    existing_results = state.get("search_results", [])
    completed_tasks = state.get("completed_tasks", [])

    search = SearchTool()
    try:
        results = search.search(
            query=query, max_results=max_results, include_raw_content=True)
    except Exception as e:
        return {
            "completed_tasks": completed_tasks + [current_task],
            "current_task": None,
            "summary": ["Web search failed: " + str(e)],
        }

    search_payload: dict[str, Any] = {
        "task_name": current_task.name,
        "task_description": current_task.description,
        "query": query,
        "subtopic": current_task.args.get("subtopic"),
        "goal": current_task.args.get("goal"),
        "preferred_sources": current_task.args.get("preferred_sources", []),
        "freshness_requirement": current_task.args.get("freshness_requirement"),
        "evidence_to_collect": current_task.args.get("evidence_to_collect", []),
        "results": results,
    }

    return {
        "search_results": existing_results + [search_payload],
        "completed_tasks": completed_tasks + [current_task],
        "current_task": None,
        "summary": [
            f"Web search completed for query '{query}' and returned {len(results)} results."
        ],
    }
