from src.deep_research_agent.state import AgentState
from langgraph.types import Command
from typing import Literal

TASK_TO_NODE = {
    "web_search": "web_search",
}


def _has_enough_evidence(state: AgentState) -> bool:
    """
    Simple sufficiency check.

    Replace this later with smarter logic based on:
    - number of ranked evidence items
    - subtopic coverage
    - source diversity
    - confidence thresholds
    """
    evidence_items = state.get("evidence_items", [])
    return len(evidence_items) >= 5


def _append_summary(state: AgentState, message: str) -> str:
    existing = (state.get("summary") or "").strip()
    if not existing:
        return message
    return f"{existing}\n{message}"


def search_router_node(state: AgentState) -> Command[Literal["web_search", "outline_report"]]:
    """
      Scheduler + router for the research loop.

      Responsibilities:
      1. If no current task exists, pull the next task from pending_tasks.
      2. Route to the correct execution node based on task type.
      3. If no tasks remain, decide whether to move to report outlining.
      """

    pending_tasks = state.get("pending_tasks", [])
    current_task = state.get("current_task")

    # Case 1: no current task, but there is pending work -> schedule next task
    if current_task is None and pending_tasks:
        next_task = pending_tasks[0]
        remaining_tasks = pending_tasks[1:]
        node_name = TASK_TO_NODE.get(next_task.name)

        if node_name is None:
            return Command(
                update={
                    "current_task": None,
                    "pending_tasks": remaining_tasks,
                    "summary": [_append_summary(
                        state,
                        f"Unsupported task type '{next_task.name}'. Skipping.",
                    )],
                },
                goto="outline_report",
            )

        return Command(
            update={
                "current_task": next_task,
                "pending_tasks": remaining_tasks,
                "summary": [_append_summary(
                    state,
                    f"Scheduled task '{next_task.name}' for subtopic '{next_task.args.get('subtopic', '')}'.",
                )],
            },
            goto=node_name,
        )

    # Case 2: Current task already exists -> route based on it
    if current_task is not None:
        node_name = TASK_TO_NODE.get(current_task.name)
        if node_name is not None:
            return Command(
                update={
                    "summary": [_append_summary(
                        state,
                        f"Routing current task '{current_task.name}'.",
                    )],
                },
                goto=node_name,
            )

        return Command(
            update={
                "current_task": None,
                "summary": [_append_summary(
                    state,
                    f"Unsupported current task '{current_task.name}'. Moving on.",
                )],
            },
            goto="outline_report",
        )

    # Case 3: no current task and no pending tasks -> decide whether to write report
    enough_evidence = _has_enough_evidence(state)

    if enough_evidence:
        summary = [_append_summary(
            state,
            "Router found no pending tasks and enough evidence. Moving to outline_report.",
        )]
    else:
        summary = [_append_summary(
            state,
            "Router found no pending tasks and limited evidence. Proceeding to outline_report with available evidence.",
        )]

    return Command(
        update={"summary": summary},
        goto="outline_report",
    )
