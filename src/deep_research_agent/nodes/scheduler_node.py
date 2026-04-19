from src.deep_research_agent.state import AgentState


def scheduler_node(state: AgentState) -> AgentState:
    pending = state.get("pending_tasks", [])

    if not pending:
        return {
            "current_task": None
        }

    next_task = pending[0]

    return {
        "current_task": next_task,
        "pending_tasks": pending[1:]
    }
