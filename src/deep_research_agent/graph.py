from langgraph.graph import StateGraph, START, END
from src.deep_research_agent.state import AgentState
from src.deep_research_agent.nodes.planner import planner_node
from src.deep_research_agent.nodes.scheduler_node import scheduler_node
from src.deep_research_agent.nodes.web_search import web_search_node


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("scheduler", scheduler_node)
    graph.add_node("web_search", web_search_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "scheduler")

    graph.add_conditional_edges(
        "scheduler",
        lambda state: state["current_task"]["name"],
        {
            "web_search": "web_search",
        }
    )

    graph.add_edge("web_search", "scheduler")

    return graph.compile()
