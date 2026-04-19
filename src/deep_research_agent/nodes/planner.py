from src.deep_research_agent.state import AgentState, TaskModel
from src.deep_research_agent.utils.load_prompt import load_prompt
from src.deep_research_agent.schemas.planner import PlannerOutput, SearchTask
from src.deep_research_agent.adapters.llm import LLM
from datetime import datetime
from pydantic import ValidationError

SYSTEM_PROMPT_TEMPLATE = load_prompt("planner").strip()
USER_PROMPT_TEMPLATE = load_prompt("planner_user").strip()


def _planner_tasks_to_task_models(search_tasks: list[SearchTask]) -> list[TaskModel]:
    """
    Convert planner search tasks into your graph's TaskModel objects.

    Assumes TaskModel has fields:
    - name: str
    - description: str
    - args: dict

    Adjust this mapping if your TaskModel differs.
    """
    tasks: list[TaskModel] = []

    for item in search_tasks:
        for query in item.queries:
            tasks.append(
                TaskModel(
                    name="web_search",
                    description=f"Research subtopic: {item.subtopic}. Goal: {item.goal}",
                    args={
                        "query": query,
                        "subtopic": item.subtopic,
                        "goal": item.goal,
                        "preferred_sources": item.preferred_sources,
                        "freshness_requirement": item.freshness_requirement,
                        "evidence_to_collect": item.evidence_to_collect,
                    },
                )
            )

    return tasks


def planner_node(state: AgentState) -> AgentState:
    """
    Plan the user's research question into structured search tasks.

    Expected AgentState inputs:
    - query: str

    Returns state updates for:
    - plan: list[TaskModel]
    - summary: str   (optional planning summary for debugging / downstream context)
    - pending_tasks: list[TaskModel]
    - current_task: TaskModel | None
    """

    query = (state.get("query") or "").strip()
    normalized_question = (state.get("normalized_question") or query).strip()
    research_scope = (state.get("research_scope") or "").strip()
    ambiguities = state.get("ambiguities", [])
    preferred_source_types = state.get("preferred_source_types", [])
    time_sensitivity = state.get("time_sensitivity", "medium")

    if not query:
        return {
            "plan": [],
            "summary": "Planner received an empty query.",
            "pending_tasks": [],
            "current_task": None,
            "final_answer": "I could not create a research plan because no query was provided.",
        }

    llm = LLM(
        structured_output=PlannerOutput,
        system_prompt=SYSTEM_PROMPT_TEMPLATE,
    )

    prompt = USER_PROMPT_TEMPLATE.format(
        query=query,
        normalized_question=normalized_question,
        research_scope=research_scope,
        ambiguities=ambiguities,
        preferred_source_types=preferred_source_types,
        time_sensitivity=time_sensitivity,
        current_date=datetime.now().strftime("%Y-%m-%d")
    )

    try:
        result: PlannerOutput = llm.structured_chat(prompt)
    except ValidationError as e:
        return {
            "plan": [],
            "summary": f"Planner output validation failed: {e}",
            "current_step_index": 0,
            "current_task": None,
            "final_answer": "I failed to create a valid research plan.",
        }
    except Exception as e:
        return {
            "plan": [],
            "summary": f"Planner failed: {e}",
            "current_step_index": 0,
            "current_task": None,
            "final_answer": "I failed to create a research plan due to a planner error.",
        }

    plan = _planner_tasks_to_task_models(result.search_tasks)

    planner_summary = (
        f"Normalized question: {result.normalized_question}\n"
        f"Scope: {result.research_scope}\n"
        f"Subtopics: {', '.join(result.subtopics)}\n"
        f"Ambiguities: {', '.join(result.ambiguities) if result.ambiguities else 'None'}\n"
        f"Generated search tasks: {len(result.search_tasks)}\n"
        f"Expanded execution steps: {len(plan)}"
    )

    return {
        "plan": plan,
        "pending_tasks": plan.copy(),
        "current_task": None,
        "completed_tasks": [],
        "normalized_question": result.normalized_question,
        "research_scope": result.research_scope,
        "subtopics": result.subtopics,
        "ambiguities": result.ambiguities,
        "summary": planner_summary,
    }
